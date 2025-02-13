import streamlit as st
import requests
import wikipedia
import graphviz
import fitz  # PyMuPDF for PDF processing
from docx import Document
from googleapiclient.discovery import build

# ✅ Manually Set API Keys
GEMINI_API_KEY = "AIzaSyBDno6BAWR6zeVnF1Zwwa-_uDfffDBEhTg"
GOOGLE_API_KEY = "AIzaSyCAFevmGzelx6_L1MrN_FwPr-HBXR9etEI"
GOOGLE_CSE_ID = "3244f2ed221224262"

# ✅ Function to call Gemini AI
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": query}]}]}

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        try:
            return response.json().get("candidates", [{}])[0].get("output", "No valid response from Gemini AI.")
        except (IndexError, KeyError):
            return "Unexpected response structure from Gemini AI."
    else:
        return f"Error {response.status_code}: {response.json()}"

# ✅ Function to search Google
def search_google(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        return res.get("items", [{}])[0].get("snippet", "No results found.")
    except Exception as e:
        return f"Error: {e}"

# ✅ Function to search Wikipedia
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."

# ✅ Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text if text else "No readable text found in the PDF."

# ✅ Function to analyze and summarize a PDF using Gemini AI
def analyze_pdf_with_gemini(pdf_text):
    query = f"Summarize the following document and highlight key insights:\n\n{pdf_text[:4000]}"  # Gemini API has a token limit
    return search_gemini(query)

# ✅ Function to create a PDF report
def generate_pdf(content):
    doc = Document()
    doc.add_heading("Deep Research AI Report", level=1)
    doc.add_paragraph(content)
    pdf_path = "research_report.pdf"
    doc.save(pdf_path)
    return pdf_path

# ✅ Function to create a simple diagram
def generate_diagram(process_steps):
    dot = graphviz.Digraph(comment="Process Diagram")
    for i, step in enumerate(process_steps):
        dot.node(f"{i}", step)
        if i > 0:
            dot.edge(f"{i-1}", f"{i}")
    
    diagram_path = "process_diagram.pdf"
    dot.render(diagram_path, format="pdf", cleanup=True)
    return diagram_path

# ✅ Streamlit UI
st.title("Deep Research AI Agent")

query = st.text_input("Enter your research topic:")

if st.button(
