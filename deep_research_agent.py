import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import PyPDF2
import requests
from bs4 import BeautifulSoup
import wikipedia
import base64

# Load OLAMA Model
@st.cache_resource()
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_model():
    model_name = "openlm-research/open_llama_3b"
    
    # Load tokenizer & model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    return tokenizer, model

tokenizer, model = load_model()

# Function to generate response using OLAMA
def generate_olama_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_length=200)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."

# Function to search Google (requires API key and CSE ID)
def search_google(query):
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]
    GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    
    response = requests.get(url)
    data = response.json()
    
    if "items" in data:
        return data["items"][0]["snippet"]
    return "No results found."

# Function to analyze uploaded PDF
def analyze_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text[:2000]  # Limit text size

# Function to generate Mermaid Flowchart
def generate_mermaid_chart(text):
    mermaid_code = f"graph TD;\n{text.replace(' ', '-->')};"
    return mermaid_code

# Streamlit UI
st.title("🔍 Deep Research AI Agent (OLAMA)")
st.write("A powerful AI-powered research assistant.")

query = st.text_input("Enter your query:")
if st.button("Search OLAMA"):
    st.write(generate_olama_response(query))

if st.button("Search Wikipedia"):
    st.write(search_wikipedia(query))

if st.button("Search Google"):
    st.write(search_google(query))

uploaded_file = st.file_uploader("Upload a PDF for analysis", type=["pdf"])
if uploaded_file is not None:
    pdf_text = analyze_pdf(uploaded_file)
    st.write("Extracted PDF Text:", pdf_text)

if st.button("Generate Flowchart"):
    flowchart_code = generate_mermaid_chart(query)
    st.write("### Flowchart:")
    st.code(flowchart_code, language="mermaid")

