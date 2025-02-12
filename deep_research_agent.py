import streamlit as st
import wikipediaapi
import requests
import json
import fitz  # PyMuPDF for PDF processing
import graphviz
from docx import Document
import os

# Set up Wikipedia API
wiki_api = wikipediaapi.Wikipedia("en")

# Set up Google Search API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# Set up Gemini AI API
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Streamlit Page Config
st.set_page_config(page_title="Deep Research AI Agent", layout="wide")
st.title("🔍 Deep Research AI Agent Created by Srijith Nair")

# Sidebar Menu
st.sidebar.header("Select Research Option")
option = st.sidebar.radio("Choose:", ["Wikipedia", "Google Search", "Gemini AI", "Upload PDF", "Generate Diagram"])

# Function to Search Wikipedia
def search_wikipedia(query):
    page = wiki_api.page(query)
    if page.exists():
        return page.summary
    else:
        return "No Wikipedia page found."

# Function to Search Google
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    data = response.json()
    
    results = []
    if "items" in data:
        for item in data["items"]:
            results.append(f"🔗 [{item['title']}]({item['link']})\n{item['snippet']}")
    
    return "\n\n".join(results) if results else "No Google search results found."

# Function to Search Gemini AI
def search_gemini(query):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"prompt": query, "key": GEMINI_API_KEY})
    
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    
    if "candidates" in data:
        return data["candidates"][0]["output"]
    return "No Gemini AI response available."

# Function to Process PDF
def process_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text if text else "No text found in PDF."

# Function to Generate Diagram
def generate_diagram(steps):
    dot = graphviz.Digraph()
    
    # Add nodes and edges
    for i, step in enumerate(steps):
        dot.node(f"{i}", step)
        if i > 0:
            dot.edge(f"{i-1}", f"{i}")
    
    diagram_path = "diagram.png"
    dot.render(diagram_path, format="png", cleanup=True)
    return diagram_path

# Function to Download as Word Document
def download_word(content, filename="Research_Output.docx"):
    doc = Document()
    doc.add_paragraph(content)
    doc_path = os.path.join(os.getcwd(), filename)
    doc.save(doc_path)
    
    with open(doc_path, "rb") as f:
        st.download_button(label="📥 Download as Word Document", data=f, file_name=filename, mime="application/msword")

# Handle Different Research Options
if option == "Wikipedia":
    query = st.text_input("Enter Wikipedia Topic:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.write(result)
        download_word(result)

elif option == "Google Search":
    query = st.text_input("Enter Google Search Query:")
    if st.button("Search Google"):
        result = search_google(query)
        st.markdown(result, unsafe_allow_html=True)
        download_word(result)

elif option == "Gemini AI":
    query = st.text_input("Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.write(result)
        download_word(result)

elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Extract Text from PDF"):
            extracted_text = process_pdf(uploaded_file)
            st.text_area("Extracted Text:", extracted_text, height=300)
            download_word(extracted_text)

elif option == "Generate Diagram":
    process_steps = st.text_area("Enter steps for diagram (one per line):").split("\n")
    if st.button("Generate Diagram"):
        if process_steps:
            diagram_file = generate_diagram(process_steps)
            st.image(diagram_file, caption="Generated Diagram")
            st.download_button(label="📥 Download Diagram", data=open(diagram_file, "rb").read(), file_name="diagram.png", mime="image/png")

