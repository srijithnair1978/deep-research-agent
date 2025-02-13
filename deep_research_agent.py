import streamlit as st
import requests
import wikipedia
import graphviz
import fitz  # PyMuPDF for PDF processing
from docx import Document

# Load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# -----------------------------------
# 📌 Function: Search Wikipedia
# -----------------------------------
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."

# -----------------------------------
# 📌 Function: Google Custom Search
# -----------------------------------
def search_google(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        results = response.json().get("items", [])
        return "\n\n".join([f"{res['title']} - {res['link']}" for res in results[:5]])
    else:
        return "No results found. Check API key or CSE ID."

# -----------------------------------
# 📌 Function: Gemini AI Search (Fixed)
# -----------------------------------
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    data = {"prompt": {"text": query}, "temperature": 0.7}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # Extracting AI Response
        if "candidates" in response_data:
            return response_data["candidates"][0]["output"]["text"]
        else:
            return "No Gemini AI response available."
    except requests.exceptions.RequestException as e:
        return f"API error: {str(e)}"
    except requests.exceptions.JSONDecodeError:
        return "Invalid response from Gemini AI"

# -----------------------------------
# 📌 Function: Upload & Extract Text from PDF
# -----------------------------------
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text if text else "No text found in PDF."

# -----------------------------------
# 📌 Function: Generate Graphviz Diagram
# -----------------------------------
def generate_diagram(process_steps):
    dot = graphviz.Digraph(format="png")
    
    for i, step in enumerate(process_steps):
        dot.node(str(i), step)

    for i in range(len(process_steps) - 1):
        dot.edge(str(i), str(i + 1))
    
    return dot

# -----------------------------------
# 📌 Function: Download Output as Word Document
# -----------------------------------
def download_as_word(text):
    doc = Document()
    doc.add_paragraph(text)
    file_path = "Deep_Research_Output.docx"
    doc.save(file_path)
    return file_path

# -----------------------------------
# 📌 Streamlit UI
# -----------------------------------
st.title("Deep Research AI Agent created by Srijith Nair")

# 🔍 **Wikipedia Search**
st.header("Search Wikipedia")
query_wiki = st.text_input("Enter a topic:")
if st.button("Search Wikipedia"):
    result = search_wikipedia(query_wiki)
    st.write(result)
    if st.button("Download as Word Document", key="wiki"):
        file = download_as_word(result)
        st.download_button("Download Word Document", open(file, "rb"), file_name="Wikipedia_Result.docx")

# 🔍 **Google Search**
st.header("Search Google")
query_google = st.text_input("Enter Google search query:")
if st.button("Search Google"):
    result = search_google(query_google)
    st.write(result)
    if st.button("Download as Word Document", key="google"):
        file = download_as_word(result)
        st.download_button("Download Word Document", open(file, "rb"), file_name="Google_Result.docx")

# 🤖 **Gemini AI**
st.header("Enter Question for Gemini AI:")
query_gemini = st.text_input("Ask Gemini AI:")
if st.button("Ask Gemini AI"):
    result = search_gemini(query_gemini)
    st.write(result)
    if st.button("Download as Word Document", key="gemini"):
        file = download_as_word(result)
        st.download_button("Download Word Document", open(file, "rb"), file_name="Gemini_Result.docx")

# 📄 **Upload & Process PDF**
st.header("Upload PDF for Analysis")
uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_pdf:
    text = extract_text_from_pdf(uploaded_pdf)
    st.text_area("Extracted Text:", text, height=200)
    if st.button("Download as Word Document", key="pdf"):
        file = download_as_word(text)
        st.download_button("Download Word Document", open(file, "rb"), file_name="Extracted_PDF_Text.docx")

# 📌 **Generate Flowchart / Diagram**
st.header("Generate Diagram")
process_steps = st.text_area("Enter steps (one per line):").split("\n")
if st.button("Generate Diagram"):
    diagram = generate_diagram(process_steps)
    st.graphviz_chart(diagram)

st.write("⚡ Powered by Wikipedia, Google Custom Search, Gemini AI, and Graphviz")
