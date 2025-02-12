import streamlit as st
import requests
import json
import wikipedia
import fitz  # PyMuPDF for PDF processing
import graphviz
from docx import Document
import os

# Load API keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# --- Function to search Wikipedia using 'wikipedia' Library ---
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=10)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for the given query."
    except Exception as e:
        return f"Error retrieving Wikipedia data: {str(e)}"

# --- Function to search Google using Custom Search API ---
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        return "\n".join([f"{item['title']}: {item['link']}" for item in results[:5]])
    else:
        return "Error retrieving Google search results."

# --- Fixed Function for Gemini AI ---
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"prompt": {"text": query}})
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0].get("output", "No response generated.")
        else:
            return "No valid response from Gemini AI."
    else:
        return f"Error {response.status_code}: {response.text}"

# --- Function to Extract Text from PDF ---
def extract_text_from_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return text if text else "No text found in PDF."
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

# --- Function to Generate Diagram Using Graphviz ---
def generate_diagram(process_steps):
    dot = graphviz.Digraph(format="png")
    prev_node = None
    for step in process_steps.split(","):
        step = step.strip()
        dot.node(step, step)
        if prev_node:
            dot.edge(prev_node, step)
        prev_node = step
    diagram_path = "process_diagram"
    dot.render(diagram_path, cleanup=True)
    return f"{diagram_path}.png"

# --- Function to Save Output as Word Document ---
def save_to_word(content, filename="output.docx"):
    doc = Document()
    doc.add_paragraph(content)
    doc_path = f"./{filename}"
    doc.save(doc_path)
    return doc_path

# --- Streamlit UI ---
st.title("Deep Research AI Agent Created by Srijith Nair")
st.write("Select an option to perform research.")

option = st.selectbox("Choose a research option:", ["Wikipedia", "Google", "PDF", "Gemini AI", "Generate Diagram"])

if option == "Wikipedia":
    query = st.text_input("Enter topic for Wikipedia search:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.text_area("Wikipedia Result:", result, height=200)
        word_file = save_to_word(result)
        st.download_button("📥 Download as Word Document", data=open(word_file, "rb"), file_name="Wikipedia_Result.docx")

elif option == "Google":
    query = st.text_input("Enter topic for Google search:")
    if st.button("Search Google"):
        result = search_google(query)
        st.text_area("Google Search Results:", result, height=200)
        word_file = save_to_word(result)
        st.download_button("📥 Download as Word Document", data=open(word_file, "rb"), file_name="Google_Result.docx")

elif option == "PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button("Extract Text"):
        result = extract_text_from_pdf(pdf_file)
        st.text_area("Extracted Text:", result, height=200)
        word_file = save_to_word(result)
        st.download_button("📥 Download as Word Document", data=open(word_file, "rb"), file_name="Extracted_PDF_Text.docx")

elif option == "Gemini AI":
    query = st.text_input("Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.text_area("Gemini AI Response:", result, height=200)
        word_file = save_to_word(result)
        st.download_button("📥 Download as Word Document", data=open(word_file, "rb"), file_name="Gemini_AI_Response.docx")

elif option == "Generate Diagram":
    process_steps = st.text_input("Enter process steps (comma-separated):")
    if st.button("Generate Diagram"):
        diagram_file = generate_diagram(process_steps)
        st.image(diagram_file, caption="Generated Diagram", use_column_width=True)
        with open(diagram_file, "rb") as file:
            st.download_button("📥 Download Diagram as PNG", file, file_name="Process_Diagram.png")

# --- End of Code ---
