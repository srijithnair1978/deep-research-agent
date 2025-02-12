import streamlit as st
import wikipediaapi
import requests
import fitz  # PyMuPDF for PDF processing
from docx import Document
import base64
from io import BytesIO
from googleapiclient.discovery import build
from diagrams import Diagram
from diagrams.programming.language import Python
import tempfile

# --- CONFIGURE PAGE ---
st.set_page_config(page_title="Deep Research AI Agent by Srijith Nair", layout="wide")

st.title("Deep Research AI Agent by Srijith Nair")

# --- GOOGLE SEARCH SETTINGS ---
GOOGLE_API_KEY = "your-google-api-key"
GOOGLE_CSE_ID = "your-google-cse-id"

def google_search(query):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
    results = res.get("items", [])
    return [f"{item['title']}: {item['link']}" for item in results]

# --- GEMINI SEARCH (REPLACE WITH YOUR OWN INTEGRATION) ---
def gemini_search(query):
    return f"🔍 Gemini search result for: {query} (Placeholder response)"

# --- WIKIPEDIA SEARCH ---
def fetch_wikipedia_summary(topic):
    wiki = wikipediaapi.Wikipedia("en")
    page = wiki.page(topic)
    return page.summary if page.exists() else "No Wikipedia content found."

# --- PDF FILE PROCESSING ---
def extract_text_from_pdf(file):
    text = ""
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf_document:
        text += page.get_text()
    return text

# --- GENERATE DIAGRAM (Diagrams.net / Draw.io Alternative) ---
def generate_diagram(process_steps):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        with Diagram("Process Flow", show=False, outformat="png") as diag:
            Python("Start") >> Python(process_steps) >> Python("End")
        temp_file_path = temp_file.name
    return temp_file_path

# --- DOWNLOAD OUTPUT AS WORD DOCUMENT ---
def generate_word_doc(content):
    doc = Document()
    doc.add_heading("Deep Research AI Agent - Analysis", level=1)
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- STREAMLIT APP INTERFACE ---
option = st.radio("Select Research Method:", ["Google", "Wikipedia", "Gemini AI", "Upload PDF", "Generate Diagram"])

if option == "Google":
    query = st.text_input("Enter your search query:")
    if st.button("Search Google"):
        if query:
            results = google_search(query)
            st.write("### Google Search Results:")
            for res in results:
                st.write(res)
            st.download_button("Download as Word", generate_word_doc("\n".join(results)), file_name="Google_Results.docx")

elif option == "Wikipedia":
    topic = st.text_input("Enter a Wikipedia topic:")
    if st.button("Search Wikipedia"):
        if topic:
            summary = fetch_wikipedia_summary(topic)
            st.write("### Wikipedia Summary:")
            st.write(summary)
            st.download_button("Download as Word", generate_word_doc(summary), file_name="Wikipedia_Summary.docx")

elif option == "Gemini AI":
    query = st.text_input("Enter your search query for Gemini AI:")
    if st.button("Search Gemini"):
        if query:
            result = gemini_search(query)
            st.write("### Gemini AI Response:")
            st.write(result)
            st.download_button("Download as Word", generate_word_doc(result), file_name="Gemini_AI_Response.docx")

elif option == "Upload PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_pdf and st.button("Extract Text"):
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        st.write("### Extracted PDF Text:")
        st.write(pdf_text)
        st.download_button("Download as Word", generate_word_doc(pdf_text), file_name="PDF_Extracted_Text.docx")

elif option == "Generate Diagram":
    process_steps = st.text_area("Enter process steps (e.g., Step 1 → Step 2 → Step 3)")
    if st.button("Generate Diagram"):
        if process_steps:
            diagram_file_path = generate_diagram(process_steps)
            with open(diagram_file_path, "rb") as file:
                st.download_button("Download Diagram (PNG)", file, file_name="Process_Diagram.png")
