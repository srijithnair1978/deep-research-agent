import streamlit as st
import wikipediaapi
import requests
import json
import fitz  # PyMuPDF for PDF processing
import graphviz  # For diagram generation
from docx import Document
from io import BytesIO

# Set Streamlit Page Configuration
st.set_page_config(page_title="Deep Research AI Agent", layout="wide")
st.title("🔍 Deep Research AI Agent - Created by Srijith Nair")

# Load API Keys from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Function to fetch Wikipedia Summary
def search_wikipedia(query):
    wiki_wiki = wikipediaapi.Wikipedia('en')
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary
    return "No Wikipedia page found for this topic."

# Function to fetch Google Search Results
def search_google(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(search_url)
    results = response.json()
    
    if "items" in results:
        return "\n\n".join([f"- [{item['title']}]({item['link']})" for item in results["items"][:5]])
    return "No Google search results found."

# Function to fetch Gemini AI response
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": {"text": query}, "max_tokens": 200}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if "candidates" in result:
        return result["candidates"][0]["output"]
    return "No Gemini AI response available."

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text if text else "No text found in the PDF."

# Function to generate process diagram using Graphviz
def generate_diagram(diagram_text):
    dot = graphviz.Digraph()
    steps = diagram_text.split("→")
    
    for i in range(len(steps) - 1):
        dot.edge(steps[i].strip(), steps[i + 1].strip())

    output_path = "process_diagram"
    dot.render(output_path, format="png", cleanup=True)
    
    return output_path + ".png"

# Function to save output to Word
def save_to_word(content):
    doc = Document()
    doc.add_heading("Deep Research AI Output", level=1)
    doc.add_paragraph(content)
    
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return file_stream

# Streamlit Sidebar for Input
st.sidebar.header("Search Options")
search_type = st.sidebar.radio("Choose a Search Method:", ["Wikipedia", "Google", "Gemini AI", "Upload PDF", "Generate Diagram"])

query = st.sidebar.text_input("Enter Search Query:")

# Handling Different Search Options
if search_type == "Wikipedia" and query:
    result = search_wikipedia(query)
    st.subheader("📖 Wikipedia Summary")
    st.write(result)
    st.download_button("Download as Word", save_to_word(result), file_name="wikipedia_summary.docx")

elif search_type == "Google" and query:
    result = search_google(query)
    st.subheader("🌍 Google Search Results")
    st.write(result, unsafe_allow_html=True)
    st.download_button("Download as Word", save_to_word(result), file_name="google_search_results.docx")

elif search_type == "Gemini AI" and query:
    result = search_gemini(query)
    st.subheader("🤖 Gemini AI Analysis")
    st.write(result)
    st.download_button("Download as Word", save_to_word(result), file_name="gemini_ai_analysis.docx")

elif search_type == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF File", type=["pdf"])
    if uploaded_file:
        result = extract_text_from_pdf(uploaded_file)
        st.subheader("📄 Extracted Text from PDF")
        st.write(result)
        st.download_button("Download as Word", save_to_word(result), file_name="pdf_extracted_text.docx")

elif search_type == "Generate Diagram":
    process_steps = st.text_area("Enter process steps separated by '→' (Example: Step 1 → Step 2 → Step 3)")
    if st.button("Generate Diagram"):
        if process_steps:
            diagram_file = generate_diagram(process_steps)
            st.subheader("📊 Generated Process Diagram")
            st.image(diagram_file)
            with open(diagram_file, "rb") as file:
                st.download_button("Download Diagram", file, file_name="process_diagram.png", mime="image/png")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Developed by **Srijith Nair** 🚀")
