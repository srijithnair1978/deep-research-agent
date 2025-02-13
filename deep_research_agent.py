import streamlit as st
import requests
import wikipedia
import graphviz
import fitz  # PyMuPDF for PDF processing
from docx import Document
from googleapiclient.discovery import build

# ✅ Manually Set API Keys
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
GOOGLE_CSE_ID = "YOUR_GOOGLE_CSE_ID_HERE"

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

if st.button("Search Wikipedia"):
    wiki_result = search_wikipedia(query)
    st.write(wiki_result)

if st.button("Search Google"):
    google_result = search_google(query)
    st.write(google_result)

if st.button("Ask Gemini AI"):
    gemini_result = search_gemini(query)
    st.write(gemini_result)

# ✅ PDF Upload & Analysis
uploaded_file = st.file_uploader("Upload a PDF for Analysis", type=["pdf"])
if uploaded_file:
    with st.spinner("Extracting text..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted PDF Content:")
    st.write(pdf_text[:1000])  # Display only first 1000 characters

    # ✅ Analyze PDF Content with Gemini AI
    with st.spinner("Analyzing PDF with Gemini AI..."):
        pdf_analysis = analyze_pdf_with_gemini(pdf_text)
    st.subheader("AI Analysis of PDF:")
    st.write(pdf_analysis)

# ✅ PDF Download Option
if st.button("Download as Word Document"):
    content = f"Wikipedia: {search_wikipedia(query)}\n\nGoogle: {search_google(query)}\n\nGemini AI: {search_gemini(query)}\n\nPDF Analysis: {pdf_analysis}"
    pdf_path = generate_pdf(content)
    with open(pdf_path, "rb") as file:
        st.download_button("Download Report", file, file_name="research_report.pdf")

# ✅ Diagram Generation Option
process_steps = st.text_area("Enter process steps (one per line):").split("\n")
if st.button("Generate Diagram"):
    diagram_file = generate_diagram(process_steps)
    with open(diagram_file, "rb") as file:
        st.download_button("Download Process Diagram", file, file_name="process_diagram.pdf")
