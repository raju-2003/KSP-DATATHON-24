**KSP DATATHON 2024**

**Data Privacy in Law Enforcement**

---

# FIR Redactor for Karnataka Police Department

## Overview
Welcome to the FIR Redactor, a powerful and intuitive tool designed specifically for the Karnataka Police Department. Our application aims to enhance the privacy and security of sensitive information within First Information Reports (FIRs). This tool leverages advanced language models and PDF processing libraries to identify and redact personal identifiers from FIR documents written in both English and Kannada.

## Key Features

1. **Dual Language Support**: Handles FIRs in both English and Kannada, ensuring comprehensive coverage for diverse linguistic needs.

2. **AI-Powered Entity Extraction**: Utilizes the cutting-edge LLM model to accurately extract personal identifiers such as names, addresses, and other sensitive information from FIR texts.

3. **Automated Redaction**: Employs PyMuPDF to seamlessly redact identified sensitive information from PDF documents, replacing it with blacked-out text to maintain confidentiality.

4. **User-Friendly Interface**: Provides an intuitive and easy-to-navigate interface for users, including tabs for Home, Login, Redaction, and comprehensive information about the tool.

## How It Works

- **Upload FIR Documents**: Users can upload FIR PDFs through a simple file uploader. The application reads and extracts text from these documents for further processing.

- **AI-Suggested Redactions**: After analyzing the text, the application suggests redactions by identifying sensitive entities. These suggestions are presented in a structured format for user review.

- **Redaction Execution**: Users can input the specific text they wish to redact, and the tool will automatically find and redact these instances within the document. The redacted PDF is then saved securely.

## Security and Privacy

The FIR Redactor ensures that the privacy of individuals involved in FIRs is protected by securely handling all documents and utilizing state-of-the-art redaction techniques. All data processing is performed with strict adherence to security protocols to prevent unauthorized access and maintain the integrity of sensitive information.

## Intended Use

This tool is designed to assist the Karnataka Police Department in safeguarding personal information within FIRs, facilitating compliance with privacy regulations and enhancing the trust and confidence of the public.

## Setup and Installation

### Prerequisites

- Python 3.7 or higher
- MongoDB
- Streamlit
- PyPDF2
- PyMuPDF
- OpenAI API key

### Installation Steps

1. **Clone the Repository**

   ```sh
   git clone https://github.com/raju-2003/FIR-Redactor
   ```

2. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**

   Create a `.streamlit/secrets.toml` file and add your OpenAI API key and MongoDB connection string:

   ```toml
   [secrets]
   openai = "your_openai_api_key"
   connection_string = "your_mongodb_connection_string"
   ```

### Running the Application

```sh
streamlit run app.py
```

## Application Structure

- **app.py**: The main application file containing the Streamlit interface and all functionalities.
- **requirements.txt**: A file containing all the dependencies required to run the application.

## Main Functions and Their Roles

- **generate_token(user_id)**: Generates a JWT token for user authentication.
- **validate_token(token)**: Validates the JWT token.
- **save_token(user_id, token, expiry)**: Saves the generated token to the MongoDB database.
- **check_login(username, password)**: Verifies user credentials against the database.
- **read_file(pdf_file)**: Reads the uploaded PDF file and extracts text.
- **extract_entities(text)**: Uses the OpenAI API to extract sensitive entities from the text.
- **search_replace(path, text)**: Redacts specified text from the PDF document and provides a downloadable redacted version.

## Usage

1. **Login**: Users must log in using their credentials to access the redaction features.
2. **Upload FIR Document**: After logging in, users can upload FIR documents in PDF format.
3. **AI-Suggested Redactions**: The application will provide AI-suggested redactions based on the uploaded document.
4. **Manual Redaction**: Users can manually input text to be redacted and download the redacted PDF.

## Developed By

### Rubix Cube

This tool is designed to assist the Karnataka Police Department in safeguarding personal information within FIRs, facilitating compliance with privacy regulations and enhancing the trust and confidence of the public.
