import streamlit as st
import wikipediaapi
import requests
import json
import os
import pytesseract
import cv2
import pdfplumber
import google.generativeai as genai
from langchain.embeddings import HuggingFaceEmbeddings  # Using free embeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS  # Using FAISS instead of Milvus
from langchain.docstore.in_memory import InMemoryDocstore
from serpapi import GoogleSearch
import faiss
import numpy as np

# Set up Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(user_agent='DeepResearchBot', language='en')

# Set up Google Search API Key
SERPAPI_KEY = "7faf237ab111d4ae788faac02fe9f1ff94239a2e01f6885432ee72d2da68703e"

# Ensure Gemini API Key is set
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyBzT2kIMz5vyqhWImeau4m-59GFSYSFAIk")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

# Function to extract text from PDF and analyze it
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text if text else "No readable text found in PDF."

# Function to extract text from images and analyze it
def extract_text_from_image(image_file):
    try:
        image = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text if extracted_text.strip() else "No readable text found in image."
    except Exception as e:
        return f"Error processing image: {str(e)}"

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

# Function to get AI-generated response using Gemini API
def get_ai_response(query):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(query)
    return response.text

# Streamlit UI
st.title("Deep Research AI Agent")
st.write("Ask questions and get answers from Wikipedia, Google, PDFs, and Images!")

query = st.text_input("Enter your research question:")
search_type = st.radio("Select search source:", ["Wikipedia", "Google", "Upload PDF", "Upload Image"])

if search_type == "Wikipedia" and query:
    result = search_wikipedia(query)
    docs = process_and_store(result)
    st.write("Wikipedia Research:", result[:1000])
    st.write("AI Analysis:", get_ai_response(query))

elif search_type == "Google" and query:
    result = search_google(query)
    docs = process_and_store(result)
    st.write("Google Search Summary:", result)
    st.write("AI Analysis:", get_ai_response(query))

elif search_type == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        pdf_text = extract_text_from_pdf(pdf_file)
        docs = process_and_store(pdf_text)
        st.write("Extracted Text from PDF:", pdf_text[:1000])
        st.write("AI Explanation:", analyze_text_with_gemini(pdf_text))

elif search_type == "Upload Image":
    image_file = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])
    if image_file:
        image_text = extract_text_from_image(image_file)
        docs = process_and_store(image_text)
        st.write("Extracted Text from Image:", image_text[:1000])
        st.write("AI Explanation:", analyze_text_with_gemini(image_text))
