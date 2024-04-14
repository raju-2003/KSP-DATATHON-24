
import json
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from openai import OpenAI
import toml
import fitz
import os
import mysql.connector
import jwt

#create a connection to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ksp_datathon"
)



secrets = toml.load("secrets.toml")
openai = OpenAI(api_key=secrets["api_keys"]["openai"])


def read_file(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return extract_entities(text)


def extract_entities(text):
    prompt = "Without having any comment on this , I have FIR file in EngLish and Kannada Languages, Analyse the pdf in both languages to answer my query, in this all the personal identifiers like names, addresses in exact word format if it's in capital letter give it as capital letter , same for small letters:\n\n" + \
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
    print(f"Redacted PDF saved to: {redacted_pdf_path}")
    st.success("File redacted successfully")

token = ""

def main():
    
    
    st.title("KSP Datathon 24")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Home", "Login", "Redact", "About"])
    
    with tab1:
        
        st.title("FIR Redactor for Karnataka Police Department")
        st.write("This is a tool to redact personal information from FIRs in English and Kannada languages.")
        st.write("To get started, please login using the form in the 'Login' tab.")
        
    with tab2:
        
        
        st.title("Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            cursor = mydb.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            if len(result) > 0:
                payload = {
                    "username": username,
                    "password": password
                }
                token_new = jwt.encode(payload, secrets["jwt_secret"], algorithm="HS256")
                token = token_new
                
                st.success("Login successful")
            else:
                st.error("Invalid username or password")
                
    with tab3:
        
        st.write("Upload a FIR document")

        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None & token != "":
            if st.button("AI suggestion"):
                res_str = read_file(uploaded_file)
                # Convert the string to a dictionary
                res_dict = json.loads(res_str)
                st.write("AI Suggested replacements:")
                # st.write(res_dict)
                # if value is empty then remove the key
                for key in list(res_dict.keys()):
                    if not res_dict[key]:
                        del res_dict[key]
                df = pd.DataFrame(res_dict.items(), columns=["Entity", "Value"])
                st.write(df)
        

        path = st.text_input("Input the path of file", key="path")
        text = st.text_input("Enter the text to Redact in the file", key="text")

        if st.button("Redact"):
            search_replace(path, text)
            
    with tab4:
            
            st.title("About")
            st.write("This is a tool to redact personal information from FIRs in English and Kannada languages.")
            st.write("This tool uses LLM model to extract and identify personal and privacy info from the FIR document.")
            st.write("The extracted entities are then redacted from the document using the PyMuPDF library.")
            st.write("This tool is intended for use by the Karnataka Police Department to protect the privacy of individuals in FIR documents.")

    


if __name__ == "__main__":
    main()
