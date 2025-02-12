import streamlit as st
import wikipediaapi
import requests
import json
import pdfplumber
import google.generativeai as genai
from langchain_community.embeddings import HuggingFaceEmbeddings  # Updated import
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS  # Using FAISS instead of Milvus
from langchain.docstore.in_memory import InMemoryDocstore
from serpapi import GoogleSearch
import faiss
import numpy as np
from docx import Document
import base64
import drawsvg as draw  # Adding DrawSVG for diagrams

# Set up Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(user_agent='DeepResearchBot', language='en')

# Load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

# Use Free HuggingFace Embeddings Instead of OpenAI
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize FAISS with proper dimension handling
vector_dim = 384  # Dimension for 'all-MiniLM-L6-v2' embeddings
index = faiss.IndexFlatL2(vector_dim)
docstore = InMemoryDocstore({})
index_to_docstore_id = {}
vectorstore = FAISS(embedding_model, index, docstore, index_to_docstore_id)

# Function to search Wikipedia
def search_wikipedia(query):
    page = wiki_wiki.page(query)
    if not page.exists():
        return "No relevant Wikipedia article found."
    return page.text

# Function to perform Google search
def search_google(query):
    search = GoogleSearch({"q": query, "api_key": SERPAPI_KEY})
    results = search.get_dict()
    return "\n".join([r['snippet'] for r in results.get("organic_results", [])[:5]]) if results else "No results found."

# Function to get search results using Gemini API
def search_gemini(query):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Search and summarize results for: {query}")
    return response.text if response else "No results found."

# Function to extract text from PDF and analyze it
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text if text else "No readable text found in PDF."

# Function to generate a downloadable Word document
def generate_word_document(content):
    filename = "output.docx"
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)
    return filename

# Function to generate a diagram using drawsvg
def generate_diagram(content):
    d = draw.Drawing(800, 400, origin='center')
    steps = content.split("->")
    y = 100
    for i, step in enumerate(steps):
        d.append(draw.Text(step.strip(), 20, 0, y))
        if i < len(steps) - 1:
            d.append(draw.Line(0, y - 10, 0, y - 30, stroke='black', stroke_width=2))
        y -= 50
    d.save_svg("diagram.svg")
    d.save_png("diagram.png")
    return "diagram.png"

# Streamlit UI
st.title("Deep Research AI Agent created by Srijith Nair")
st.write("Ask questions and get answers from Wikipedia, Google, Gemini, PDFs, and generate flowcharts!")

query = st.text_input("Enter your research question:")
search_type = st.radio("Select search source:", ["Wikipedia", "Google", "Gemini AI Search", "Upload PDF", "Generate Visual Diagram"])

if query:
    result = ""
    if search_type == "Wikipedia":
        result = search_wikipedia(query)
    elif search_type == "Google":
        result = search_google(query)
    elif search_type == "Gemini AI Search":
        result = search_gemini(query)
    elif search_type == "Upload PDF":
        pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if pdf_file:
            result = extract_text_from_pdf(pdf_file)
    elif search_type == "Generate Visual Diagram":
        process_steps = st.text_area("Enter process steps (use '->' to link steps, e.g., 'Start -> Step 1 -> Step 2 -> End'):")
        if st.button("Generate Diagram"):
            diagram_file = generate_diagram(process_steps)
            st.image(diagram_file, caption="Generated Diagram", use_column_width=True)
            with open(diagram_file, "rb") as file:
                st.download_button(label="Download Diagram as PDF", data=file, file_name="diagram.pdf", mime="application/pdf")
    
    if result:
        st.write(f"{search_type} Results:", result[:1000])
        ai_analysis = search_gemini(query)
        st.write("AI Analysis:", ai_analysis)
        
        full_content = result + "\n\nAI Analysis:\n" + ai_analysis
        filename = generate_word_document(full_content)
        with open(filename, "rb") as file:
            st.download_button(label="Download Results as Word Document", data=file, file_name=filename, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
