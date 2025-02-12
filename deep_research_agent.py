import streamlit as st
import requests
import wikipedia
import fitz  # PyMuPDF for PDF processing
import graphviz
from docx import Document
from io import BytesIO

# Set Page Title
st.title("🔍 Deep Research AI Agent - Created by Srijith Nair")

# Load API Keys from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# ---- Function: Google Search ----
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    data = response.json()

    if "items" in data:
        return [f"🔗 {item['title']} - {item['link']}" for item in data["items"]]
    else:
        return ["❌ No results found. Check API key or CSE ID."]

# ---- Function: Wikipedia Search ----
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠ Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "❌ No Wikipedia page found."

# ---- Function: Gemini AI Search ----
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
    data = {"prompt": {"text": query}, "maxTokens": 100}
    response = requests.post(url, json=data)
    result = response.json()

    if "error" in result:
        return f"❌ Gemini AI Error: {result['error']['message']}"
    else:
        return result["candidates"][0]["output"]

# ---- Function: PDF Text Extraction ----
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text if text else "❌ No text found in PDF."

# ---- Function: Generate Diagram ----
def generate_diagram(process_steps):
    dot = graphviz.Digraph()
    for i, step in enumerate(process_steps):
        dot.node(f"Step {i+1}", step)
        if i > 0:
            dot.edge(f"Step {i}", f"Step {i+1}")
    return dot

# ---- Function: Generate Word Document ----
def generate_word_doc(content, filename="Deep_Research_Output.docx"):
    doc = Document()
    doc.add_heading("Deep Research AI Agent - Output", level=1)
    doc.add_paragraph(content)
    byte_io = BytesIO()
    doc.save(byte_io)
    return byte_io

# ---- Streamlit UI ----
st.sidebar.header("Choose Research Mode")
mode = st.sidebar.radio("Select an Option:", ["Google Search", "Wikipedia", "Gemini AI", "PDF Processing", "Generate Diagram"])

# ---- Handle Different Options ----
if mode == "Google Search":
    query = st.text_input("Enter Search Query for Google:")
    if st.button("Search Google"):
        results = search_google(query)
        for res in results:
            st.write(res)

elif mode == "Wikipedia":
    query = st.text_input("Enter Search Query for Wikipedia:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.write(result)

elif mode == "Gemini AI":
    query = st.text_input("Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.write("### Gemini AI Response:")
        st.code(result, language="json")

elif mode == "PDF Processing":
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        text = extract_text_from_pdf(pdf_file)
        st.text_area("Extracted Text:", text, height=300)

elif mode == "Generate Diagram":
    steps_input = st.text_area("Enter process steps (one per line):")
    if st.button("Generate Diagram"):
        steps = steps_input.split("\n")
        diagram = generate_diagram(steps)
        st.graphviz_chart(diagram)

# ---- Download as Word Document ----
if mode in ["Google Search", "Wikipedia", "Gemini AI"]:
    if st.button("📥 Download as Word Document"):
        content = search_google(query) if mode == "Google Search" else search_wikipedia(query) if mode == "Wikipedia" else search_gemini(query)
        word_file = generate_word_doc(content)
        st.download_button(label="Download Word Document", data=word_file.getvalue(), file_name="Deep_Research_Output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
