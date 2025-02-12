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
    return response.text

# Function to extract text from PDF and analyze it
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text if text else "No readable text found in PDF."

# Function to provide explanation from extracted text
def analyze_text_with_gemini(text):
    if not text.strip():
        return "No readable content found to analyze."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Analyze and explain this content: {text}")
    return response.text

# Function to store and retrieve information
def process_and_store(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.create_documents([text])
    vectorstore.add_texts([text])
    return docs

# Function to generate a downloadable Word document
def generate_word_document(content, filename="output.docx"):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)
    return filename

# Streamlit UI
st.title("Deep Research AI Agent created by Srijith Nair")
st.write("Ask questions and get answers from Wikipedia, Google, Gemini, and PDFs!")

query = st.text_input("Enter your research question:")
search_type = st.radio("Select search source:", ["Wikipedia", "Google", "Gemini AI Search", "Upload PDF"])

if query:
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
    
    if result:
        docs = process_and_store(result)
        st.write(f"{search_type} Results:", result[:1000])
        ai_analysis = get_ai_response(query)
        st.write("AI Analysis:", ai_analysis)
        
        # Generate and provide download link for Word document
        filename = generate_word_document(result + "\n\nAI Analysis:\n" + ai_analysis)
        with open(filename, "rb") as file:
            st.download_button(label="Download Results as Word Document", data=file, file_name=filename, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
