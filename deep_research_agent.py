import streamlit as st
import requests
import wikipedia
import fitz  # PyMuPDF for PDF processing
from docx import Document
import os

# Load API keys from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# -----------------------------------
# 🔹 Function to Search Wikipedia
# -----------------------------------
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."
    except Exception as e:
        return f"Error: {e}"

# -----------------------------------
# 🔹 Function to Search Google
# -----------------------------------
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query
    }
    response = requests.get(url, params=params)
    
    try:
        data = response.json()
        if "items" in data:
            return "\n".join([f"{i+1}. {item['title']} - {item['link']}" for i, item in enumerate(data['items'][:5])])
        return "❌ No results found. Check API key or CSE ID."
    except requests.exceptions.JSONDecodeError:
        return "❌ Google API Error: Received invalid response."

# -----------------------------------
# 🔹 Function to Query Gemini AI
# -----------------------------------
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    data = {"prompt": {"text": query}, "maxTokens": 100}
    
    response = requests.post(url, json=data, headers=headers)
    
    try:
        result = response.json()
        if "error" in result:
            return f"❌ Gemini AI Error: {result['error']['message']}"
        return result.get("candidates", [{}])[0].get("output", "❌ No response received.")
    except requests.exceptions.JSONDecodeError:
        return "❌ Error: Received non-JSON response from Gemini API. Check API key."

# -----------------------------------
# 🔹 Function to Process PDF Upload
# -----------------------------------
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text if text.strip() else "No text found in the PDF."

# -----------------------------------
# 🔹 Function to Download as Word Document
# -----------------------------------
def download_as_word(content, filename="Research_Output.docx"):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)

    with open(filename, "rb") as f:
        st.download_button(
            label="📩 Download as Word Document",
            data=f,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# -----------------------------------
# 🔹 Streamlit UI
# -----------------------------------
st.title("🧠 Deep Research AI Agent - Created by Srijith Nair")

st.sidebar.header("Choose Research Method")
option = st.sidebar.radio("Select an Option:", ["Wikipedia", "Google", "Gemini AI", "Upload PDF"])

if option == "Wikipedia":
    query = st.text_input("🔍 Enter search term for Wikipedia:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.subheader("Wikipedia Result:")
        st.write(result)
        download_as_word(result)

elif option == "Google":
    query = st.text_input("🔍 Enter search term for Google:")
    if st.button("Search Google"):
        result = search_google(query)
        st.subheader("Google Search Results:")
        st.write(result)
        download_as_word(result)

elif option == "Gemini AI":
    query = st.text_input("🔍 Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.subheader("Gemini AI Response:")
        st.write(result)
        download_as_word(result)

elif option == "Upload PDF":
    pdf_file = st.file_uploader("📄 Upload a PDF File", type=["pdf"])
    if pdf_file is not None:
        extracted_text = extract_text_from_pdf(pdf_file)
        st.subheader("Extracted Text from PDF:")
        st.write(extracted_text)
        download_as_word(extracted_text)
