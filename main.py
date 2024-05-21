
import json
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from openai import OpenAI
import os
from pymongo import MongoClient
import jwt
import datetime
import tempfile
import fitz

openai = OpenAI(api_key=st.secrets["openai"])

#create a connection to the database

client = MongoClient(st.secrets["connection_string"])

db = client["KSP"]


user_table = db["User"]
token_table = db["Token"]


# Generate JWT token
def generate_token(user_id):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        "user_id": user_id,
        "exp": expiry
    }
    token = jwt.encode(payload, key='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', algorithm="HS256")
    return token, expiry

# Validate JWT token
def validate_token(token):
    try:
        payload = jwt.decode(token, key='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', algorithms=["HS256"])
        return payload["user_id"], payload["exp"]
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

# Save token to database
def save_token(user_id, token, expiry):
    token_table.insert_one({
        "user_id": user_id,
        "token": token,
        "expiry": expiry
    })

# Check login credentials
def check_login(username, password):
    user_table.find_one({"username": username, "password": password})
    return user_table.find_one({"username": username, "password": password})


def read_file(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return extract_entities(text)


def extract_entities(text):
    prompt = "Without having any comment on this , I have FIR file in EngLish and Kannada Languages, Analyse the pdf in both languages to answer my query, in this all the personal identifiers like names, addresses in exact word format\n\n" + \
        str(text)+"\n\n. I need result in a dict format with key and value , key describes about either it is name , address with values. Can you provide me the result in this format ?\n\n"

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content


def search_replace(path, text):
    
    
    doc = fitz.open(path)
    for page in doc:
        instances = page.search_for(text)
        for inst in instances:
            page.add_redact_annot(inst, fill=(0, 0, 0))
        page.apply_redactions()
    directory = os.path.dirname(path)
    redacted_pdf_path = os.path.join(directory, 'redacted_document.pdf')
    doc.save(redacted_pdf_path)
    doc.close()
    
    #download the redacted file to the local system
    st.download_button(label="Download Redacted PDF", data=open(redacted_pdf_path, 'rb').read(), file_name='redacted_document.pdf', mime='application/pdf')
    
    # st.success(f"Redacted PDF saved to: {redacted_pdf_path}")
    st.success("File redacted successfully")


def main():
    
    
    st.title("KSP Datathon 24")
    
    tab1, tab2, tab3, tab4 = st.tabs(["#### Home", "#### Login", "#### Redact", "#### About"])
    
    with tab1:
        
       st.write("""
    Welcome to the FIR Redactor, an advanced tool designed to protect sensitive information in First Information Reports (FIRs) for the Karnataka Police Department. Our application harnesses the power of AI and cutting-edge PDF processing technology to identify and redact personal identifiers, ensuring privacy and compliance with legal standards.

    In the digital age, the privacy and security of personal information have become paramount. FIRs often contain sensitive data, including names, addresses, and other personal identifiers. Unauthorized disclosure of this information can lead to privacy violations and potentially compromise the safety of individuals. Ensuring that sensitive data is redacted before sharing or publishing FIRs is crucial for maintaining public trust and compliance with privacy laws.

    ### Benefits for the Karnataka Police Department:

    - **Enhanced Privacy Protection**

    - **Compliance with Legal Standards**

    - **Efficiency and Accuracy**

    - **Improved Public Trust**

    
    """)
    with tab2:
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = check_login(username, password)
            if user:
                token, expiry = generate_token(user["username"])
                save_token(user["_id"], token, expiry)
                st.success("Login successful!")
                st.session_state["token"] = token
            else:
                st.error("Invalid username or password")
                
    with tab3:

        if "token" in st.session_state:
            user_id, error = validate_token(st.session_state["token"])
            if user_id:
                st.write("Upload a FIR document")
                uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

                if uploaded_file is not None:
                    if st.button("AI suggestion"):
                        res_str = read_file(uploaded_file)
                        res_dict = json.loads(res_str)
                        st.write("AI Suggested replacements:")
                        for key in list(res_dict.keys()):
                            if not res_dict[key]:
                                del res_dict[key]
                        df = pd.DataFrame(res_dict.items(), columns=["Entity", "Value"])
                        st.write(df)

                # path = st.text_input("Input the path of file", key="path")
                text = st.text_input("Enter the text to Redact in the file", key="text")

                if st.button("Redact"):
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        uploaded_file = temp_file.name
                        search_replace(uploaded_file, text)
            else:
                st.error(error)
                # st.experimental_rerun()
        else:
            st.error("Please login to access this page.")
            # st.experimental_rerun()
            
    with tab4:
            st.write("""        
        #### FIR Redactor for Karnataka Police Department
        
        Welcome to the FIR Redactor, a powerful and intuitive tool designed specifically for the Karnataka Police Department. Our application aims to enhance the privacy and security of sensitive information within First Information Reports (FIRs). This tool leverages advanced language models and PDF processing libraries to identify and redact personal identifiers from FIR documents written in both English and Kannada.
        
        #### Key Features:
        
        1. **Dual Language Support:**
           - Handles FIRs in both English and Kannada, ensuring comprehensive coverage for diverse linguistic needs.
        
        2. **AI-Powered Entity Extraction:**
           - Utilizes the cutting-edge LLM model to accurately extract personal identifiers such as names, addresses, and other sensitive information from FIR texts.
        
        3. **Automated Redaction:**
           - Employs PyMuPDF to seamlessly redact identified sensitive information from PDF documents, replacing it with blacked-out text to maintain confidentiality.
        
        4. **User-Friendly Interface:**
           - Provides an intuitive and easy-to-navigate interface for users, including tabs for Home, Login, Redaction, and comprehensive information about the tool.
        
        #### How It Works:
        
        - **Upload FIR Documents:**
          - Users can upload FIR PDFs through a simple file uploader. The application reads and extracts text from these documents for further processing.
        
        - **AI-Suggested Redactions:**
          - After analyzing the text, the application suggests redactions by identifying sensitive entities. These suggestions are presented in a structured format for user review.
        
        - **Redaction Execution:**
          - Users can input the specific text they wish to redact, and the tool will automatically find and redact these instances within the document. The redacted PDF is then saved securely.
        
        #### Security and Privacy:
        
        The FIR Redactor ensures that the privacy of individuals involved in FIRs is protected by securely handling all documents and utilizing state-of-the-art redaction techniques. All data processing is performed with strict adherence to security protocols to prevent unauthorized access and maintain the integrity of sensitive information.
        
        #### Intended Use:
        
        This tool is designed to assist the Karnataka Police Department in safeguarding personal information within FIRs, facilitating compliance with privacy regulations and enhancing the trust and confidence of the public.
        
        ### Developed by: Rubix Cube
        """)
    

    


if __name__ == "__main__":
    main()
