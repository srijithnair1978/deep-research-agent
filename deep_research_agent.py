import streamlit as st
import requests
import wikipedia
import PyPDF2
import json
from fpdf import FPDF

# Load API Keys from Streamlit Secrets
HUGGINGFACE_API_KEY = st.secrets["huggingface"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# Hugging Face API Endpoint
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"

# Function to query Hugging Face API
def query_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_length": 500}}
    
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Error: {response.json()}"

# Function to query Google Search API
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    
    if response.status_code == 200:
        results = response.json().get("items", [])
        return results[:5]  # Return top 5 search results
    else:
        return f"Error: {response.json()}"

# Function to query Wikipedia
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for the given query."

# Function to analyze uploaded PDF
def analyze_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text[:2000]  # Limit text length

# Function to generate Mermaid flowchart
def generate_mermaid_flowchart(data):
    flowchart = "graph TD;\n"
    for idx, step in enumerate(data.split(".")):
        if step.strip():
            node = f"A{idx}({step.strip()})"
            if idx > 0:
                flowchart += f"    A{idx-1} --> {node}\n"
            else:
                flowchart += f"    {node}\n"
    return flowchart

# Streamlit UI
st.title("Deep Research AI Agent (Open AI Search)")

# Search options
option = st.selectbox("Select search method:", ["Open AI Search", "Google Search", "Wikipedia Search", "Upload PDF"])

# Text input for query
query = st.text_input("Enter your query:")

if option == "Open AI Search":
    if st.button("Search AI"):
        if query:
            response = query_huggingface(query)
            st.subheader("AI Response:")
            st.write(response)
        else:
            st.warning("Please enter a query!")

elif option == "Google Search":
    if st.button("Search Google"):
        if query:
            results = search_google(query)
            st.subheader("Google Search Results:")
            for result in results:
                st.write(f"[{result['title']}]({result['link']})")
        else:
            st.warning("Please enter a query!")

elif option == "Wikipedia Search":
    if st.button("Search Wikipedia"):
        if query:
            summary = search_wikipedia(query)
            st.subheader("Wikipedia Summary:")
            st.write(summary)
        else:
            st.warning("Please enter a query!")

elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file:
        st.subheader("Extracted Text:")
        pdf_text = analyze_pdf(uploaded_file)
        st.write(pdf_text)

# Mermaid Flowchart Generator
st.subheader("Generate Flowchart")
mermaid_input = st.text_area("Enter process steps (separate with a period '.'): ")
if st.button("Generate Diagram"):
    if mermaid_input:
        flowchart_code = generate_mermaid_flowchart(mermaid_input)
        st.subheader("Flowchart:")
        st.code(flowchart_code, language="mermaid")

        # Convert flowchart into PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(200, 10, txt=flowchart_code)
        pdf_file_path = "flowchart.pdf"
        pdf.output(pdf_file_path)
        
        with open(pdf_file_path, "rb") as pdf_file:
            st.download_button(label="Download Flowchart PDF", data=pdf_file, file_name="flowchart.pdf", mime="application/pdf")
    else:
        st.warning("Please enter process steps!")

