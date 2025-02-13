import streamlit as st
import requests
import json
import wikipedia
from docx import Document
from graphviz import Digraph
import fitz  # PyMuPDF for PDF processing

# Constants for API keys (Manually entered for now)
CLAUDE_API_KEY = "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"
GOOGLE_API_KEY = "AIzaSyCAFevmGzelx6_L1MrN_FwPr-HBXR9etEI"
GOOGLE_CSE_ID = "3244f2ed221224262"

# Page Title
st.title("Deep Research AI Agent created by Srijith Nair")

# Wikipedia Search Function
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except Exception as e:
        return f"Error fetching Wikipedia data: {e}"

# Google Search Function
def search_google(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
    }
    response = requests.get(search_url, params=params)
    results = response.json()
    try:
        return results["items"][0]["snippet"]
    except KeyError:
        return "❌ No results found. Check API key or CSE ID."

# Claude (Open AI) Search Function
def search_claude(query):
    url = "https://api.anthropic.com/v1/complete"
    headers = {
        "Authorization": f"Bearer {CLAUDE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"prompt": query, "max_tokens": 100})
    response = requests.post(url, headers=headers, data=payload)
    try:
        return response.json()["completion"]
    except KeyError:
        return "❌ Error with Claude API response."

# PDF Processing Function
def process_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Flowchart Generation using D3.js
def generate_flowchart(data):
    dot = Digraph()
    for node in data:
        dot.node(node["id"], node["label"])
    for edge in data:
        if "source" in edge and "target" in edge:
            dot.edge(edge["source"], edge["target"])
    return dot

# Sidebar Selection
st.sidebar.title("Choose Search Mode")
option = st.sidebar.radio("Select Source:", ("Wikipedia", "Google", "Claude (Open AI)"))

# User Query Input
query = st.text_input("Enter your query:")
if st.button("Search"):
    if option == "Wikipedia":
        result = search_wikipedia(query)
    elif option == "Google":
        result = search_google(query)
    elif option == "Claude (Open AI)":
        result = search_claude(query)
    st.write(result)

# PDF Upload
st.subheader("Upload a PDF for Analysis")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded_file is not None:
    pdf_content = process_pdf(uploaded_file)
    st.write("Extracted Text:")
    st.text_area("", pdf_content, height=200)

# Flowchart Generation
st.subheader("Generate Flowchart")
flowchart_data = st.text_area("Enter Flowchart Data (JSON Format)")
if st.button("Generate Diagram"):
    try:
        data = json.loads(flowchart_data)
        diagram = generate_flowchart(data)
        st.graphviz_chart(diagram)
    except Exception as e:
        st.error(f"Error generating diagram: {e}")

# Download Result as Word Document
def save_to_word(text):
    doc = Document()
    doc.add_paragraph(text)
    doc_path = "output.docx"
    doc.save(doc_path)
    return doc_path

if st.button("Download as Word Document"):
    doc_path = save_to_word(result)
    with open(doc_path, "rb") as file:
        st.download_button(label="Download Document", data=file, file_name="Research_Output.docx")
