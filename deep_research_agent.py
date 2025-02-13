import streamlit as st
import requests
import wikipedia
import graphviz
import os
import fitz  # PyMuPDF for PDF processing
from docx import Document

# **MANUAL API KEYS (Set them here)**
GEMINI_API_KEY = "AIzaSyCgluUAIWtVRvAPtj9tZDhA3gbL4tcgPdg"
GOOGLE_API_KEY = "AIzaSyCAFevmGzelx6_L1MrN_FwPr-HBXR9etEI"
GOOGLE_CSE_ID = "3244f2ed221224262"

# **App Title**
st.title("Deep Research AI Agent created by Srijith Nair")

# **🔹 Google Search Function**
def search_google(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query}
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    if "items" in data:
        return "\n".join([item["title"] + ": " + item["link"] for item in data["items"][:5]])
    else:
        return "❌ No results found. Check API key or CSE ID."

# **🔹 Wikipedia Search Function**
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."
    except Exception as e:
        return f"Error: {str(e)}"

# **🔹 Gemini AI Search Function**
def search_gemini(query):
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": query}]}]}
    
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "❌ Error: No valid response from Gemini AI."
    else:
        return f"Error {response.status_code}: {response.json()}"

# **🔹 PDF Upload & Analysis**
def analyze_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in doc])
        return text[:2000]  # Limiting to 2000 characters for display
    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}"

# **🔹 Process Diagram Generator**
def generate_diagram(process_steps):
    dot = graphviz.Digraph(comment="Process Diagram")
    
    for i, step in enumerate(process_steps):
        dot.node(f"{i}", step)
        if i > 0:
            dot.edge(f"{i-1}", f"{i}")

    diagram_path = "process_diagram"
    full_path = os.path.abspath(f"{diagram_path}.pdf")
    dot.render(full_path, format="pdf")
    
    return full_path

# **🔹 UI Elements**
st.subheader("Search Wikipedia, Google, or Gemini AI")

query = st.text_input("Enter your query:")
search_option = st.radio("Choose Search Method:", ["Wikipedia", "Google", "Gemini AI"])

if st.button("Search"):
    if search_option == "Wikipedia":
        result = search_wikipedia(query)
    elif search_option == "Google":
        result = search_google(query)
    elif search_option == "Gemini AI":
        result = search_gemini(query)
    
    st.write(result)

    # **Download as Word Document**
    if st.button("📥 Download as Word Document"):
        doc = Document()
        doc.add_heading("Search Results", level=1)
        doc.add_paragraph(result)
        doc_path = "Search_Result.docx"
        doc.save(doc_path)

        with open(doc_path, "rb") as file:
            st.download_button("Download Word File", file, file_name="Search_Result.docx")

# **🔹 PDF Upload Feature**
st.subheader("Upload & Analyze a PDF")

uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_pdf:
    pdf_text = analyze_pdf(uploaded_pdf)
    st.write("Extracted Text Preview:")
    st.write(pdf_text)

# **🔹 Process Flow Diagram Generator**
st.subheader("Generate a Process Flow Diagram")

process_steps = st.text_area("Enter process steps (one per line):").split("\n")

if st.button("Generate Diagram"):
    diagram_file = generate_diagram(process_steps)
    
    if os.path.exists(diagram_file):
        with open(diagram_file, "rb") as file:
            st.download_button("Download Process Diagram", file, file_name="process_diagram.pdf")
    else:
        st.error("Failed to generate the diagram. Please try again.")
