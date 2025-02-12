import streamlit as st
import requests
import fitz  # PyMuPDF for PDF processing
import googleapiclient.discovery
import wikipedia
from docx import Document
from io import BytesIO
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

# Load API keys from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# Function for Google Search
def search_google(query):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    result = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
    return result.get("items", [])

# Function for Wikipedia Search
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this topic."

# Function to Extract Text from PDF
def extract_text_from_pdf(file):
    text = ""
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf_document:
        text += page.get_text()
    return text

# Function to Generate Diagrams
def generate_diagram(process_steps):
    with Diagram("Process Flow", show=False):
        with Cluster("Web Services"):
            lb = ELB("Load Balancer")
            web = [EC2("Web1"), EC2("Web2")]
        
        with Cluster("Database"):
            db = RDS("DB Instance")

        lb >> web >> db

    diagram_path = "process_diagram.png"
    return diagram_path

# Function to Save Output as Word File
def save_as_word(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Deep Research AI Agent created by Srijith Nair")
st.sidebar.header("Select an Option")
option = st.sidebar.radio("Choose an option:", ["Google Search", "Wikipedia Search", "Upload PDF", "Generate Diagram"])

if option == "Google Search":
    query = st.text_input("Enter your search query:")
    if st.button("Search"):
        results = search_google(query)
        for item in results[:5]:
            st.write(f"**{item['title']}**")
            st.write(item["snippet"])
            st.write(item["link"])

elif option == "Wikipedia Search":
    query = st.text_input("Enter Wikipedia topic:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.write(result)
        word_file = save_as_word(result)
        st.download_button("Download Result as Word", word_file, file_name="Wikipedia_Result.docx")

elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text", text, height=300)
        word_file = save_as_word(text)
        st.download_button("Download Extracted Text as Word", word_file, file_name="Extracted_PDF_Text.docx")

elif option == "Generate Diagram":
    process_steps = st.text_area("Enter Process Steps:")
    if st.button("Generate"):
        diagram_path = generate_diagram(process_steps)
        st.image(diagram_path)
        with open(diagram_path, "rb") as file:
            st.download_button("Download Diagram as PDF", file, file_name="Process_Diagram.pdf", mime="application/pdf")
