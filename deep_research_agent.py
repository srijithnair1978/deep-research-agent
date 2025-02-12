import streamlit as st
import requests
import wikipediaapi
import json
import fitz  # PyMuPDF for PDF processing
import googleapiclient.discovery
from docx import Document
import os
from diagrams import Diagram
from diagrams.generic.blank import Blank

# Set up Google API Keys
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
GOOGLE_CSE_ID = "YOUR_GOOGLE_CSE_ID"

# Streamlit UI
st.title("Deep Research AI Agent - Created by Srijith Nair")
st.write("Perform deep research using Wikipedia, Google, PDFs, and auto-generated diagrams.")

# Search Options
search_option = st.radio("Select Search Type:", ["Wikipedia", "Google Search", "Upload PDF", "Generate Diagram"])

# Function to search Wikipedia
def search_wikipedia(query):
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(query)
    
    if page.exists():
        return page.summary
    else:
        return "No Wikipedia page found for this topic."

# Function to perform Google Search
def search_google(query):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    result = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=5).execute()
    search_results = result.get("items", [])
    
    return "\n".join([f"{i+1}. {item['title']}: {item['link']}" for i, item in enumerate(search_results)])

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        doc = fitz.open(pdf_file)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        text = f"Error processing PDF: {e}"
    return text

# Function to generate a simple diagram
def generate_diagram(diagram_text):
    filename = "process_diagram"
    with Diagram(filename, show=False):
        Blank(diagram_text)
    return filename + ".png"

# Function to save research to Word Document
def save_to_word(content):
    doc = Document()
    doc.add_heading("Deep Research AI Agent Output", level=1)
    doc.add_paragraph(content)
    
    output_path = "research_output.docx"
    doc.save(output_path)
    
    return output_path

# Handling different search options
query = None
if search_option == "Wikipedia":
    query = st.text_input("Enter Wikipedia Topic:")
    if st.button("Search Wikipedia"):
        if query:
            result = search_wikipedia(query)
            st.write(result)
            word_file = save_to_word(result)
            st.download_button("Download as Word", data=open(word_file, "rb"), file_name="research_output.docx")
        else:
            st.warning("Please enter a topic.")

elif search_option == "Google Search":
    query = st.text_input("Enter Google Search Query:")
    if st.button("Search Google"):
        if query:
            result = search_google(query)
            st.write(result)
            word_file = save_to_word(result)
            st.download_button("Download as Word", data=open(word_file, "rb"), file_name="research_output.docx")
        else:
            st.warning("Please enter a search query.")

elif search_option == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if pdf_file and st.button("Extract PDF Text"):
        extracted_text = extract_text_from_pdf(pdf_file)
        st.write(extracted_text)
        word_file = save_to_word(extracted_text)
        st.download_button("Download as Word", data=open(word_file, "rb"), file_name="research_output.docx")

elif search_option == "Generate Diagram":
    process_steps = st.text_area("Enter diagram description (e.g., 'Step 1 → Step 2 → Step 3'):")
    if st.button("Generate Diagram"):
        if process_steps:
            diagram_file = generate_diagram(process_steps)
            st.image(diagram_file, caption="Generated Diagram", use_column_width=True)
            st.download_button("Download Diagram", data=open(diagram_file, "rb"), file_name="process_diagram.png")
        else:
            st.warning("Please enter a diagram description.")

st.write("📢 **Note:** Ensure your API keys are set correctly in the script.")
