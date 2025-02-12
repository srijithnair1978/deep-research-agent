import streamlit as st
import requests
import json
import wikipedia
import fitz  # PyMuPDF for PDF processing
import graphviz
from docx import Document
from io import BytesIO

# Set API Keys (Replace with your actual keys)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Function: Wikipedia Search
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ Disambiguation Error: {str(e)}"
    except wikipedia.exceptions.PageError:
        return "⚠️ No Wikipedia page found."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Function: Google Search
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    try:
        response = requests.get(url)
        data = response.json()
        results = [item["title"] + "\n" + item["link"] for item in data.get("items", [])]
        return "\n\n".join(results) if results else "⚠️ No Google results found."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Function: Gemini AI Search
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"prompt": {"text": query}})
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("candidates", [{}])[0].get("output", "⚠️ No response generated.")
        elif response.status_code == 404:
            return "⚠️ Error 404: Requested entity not found. Check your API key."
        else:
            return f"⚠️ API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error.')}"
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

# Function: Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in pdf_document:
            text += page.get_text("text") + "\n"
        return text if text else "⚠️ No text extracted from PDF."
    except Exception as e:
        return f"⚠️ PDF Processing Error: {str(e)}"

# Function: Generate Flowchart (Graphviz)
def generate_diagram(process_steps):
    dot = graphviz.Digraph()
    for i, step in enumerate(process_steps):
        dot.node(str(i), step)
        if i > 0:
            dot.edge(str(i - 1), str(i))
    return dot

# Function: Download Word Document
def download_word(content, filename="Research_Report.docx"):
    doc = Document()
    doc.add_heading("Deep Research AI Agent - Report", level=1)
    doc.add_paragraph(content)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Deep Research AI Agent - Created by Srijith Nair")

# Sidebar for Options
st.sidebar.header("Select Search Option")
option = st.sidebar.radio("", ["Wikipedia", "Google Search", "Gemini AI", "Upload PDF", "Generate Flowchart"])

# Wikipedia Search
if option == "Wikipedia":
    query = st.text_input("Enter Topic for Wikipedia:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.subheader("Wikipedia Summary:")
        st.write(result)
        st.download_button("📥 Download as Word Document", download_word(result), file_name="Wikipedia_Report.docx")

# Google Search
elif option == "Google Search":
    query = st.text_input("Enter Google Search Query:")
    if st.button("Search Google"):
        result = search_google(query)
        st.subheader("Google Search Results:")
        st.write(result)
        st.download_button("📥 Download as Word Document", download_word(result), file_name="Google_Report.docx")

# Gemini AI
elif option == "Gemini AI":
    query = st.text_input("Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.subheader("Gemini AI Response:")
        st.write(result)
        st.download_button("📥 Download as Word Document", download_word(result), file_name="Gemini_Report.docx")

# PDF Upload
elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF File", type=["pdf"])
    if uploaded_file is not None:
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Text from PDF:")
        st.write(extracted_text)
        st.download_button("📥 Download as Word Document", download_word(extracted_text), file_name="PDF_Report.docx")

# Generate Flowchart
elif option == "Generate Flowchart":
    process_steps = st.text_area("Enter steps (one per line)").split("\n")
    if st.button("Generate Diagram"):
        if len(process_steps) > 1:
            diagram = generate_diagram(process_steps)
            st.graphviz_chart(diagram)
            st.success("Flowchart Generated Successfully!")
        else:
            st.error("⚠️ Enter at least two steps to generate a flowchart.")
