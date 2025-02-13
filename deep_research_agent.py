import streamlit as st
import requests
import wikipedia
import PyPDF2
import json
import base64

# ---- API Keys (Ensure these are set correctly) ----
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# ---- Set Up the App ----
st.title("Deep Research AI Agent created by Srijith Nair")

# ---- Search Wikipedia Function ----
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception as e:
        return f"Error fetching Wikipedia: {str(e)}"

# ---- Google Search Function ----
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    results = response.json()
    if "items" in results:
        return results["items"][0]["snippet"]
    return "No results found. Check API key or CSE ID."

# ---- Gemini AI Search Function ----
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": query}]}]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    try:
        return response.json()["candidates"][0]["content"]
    except Exception as e:
        return f"Error fetching Gemini AI response: {str(e)}"

# ---- PDF Upload and Analysis Function ----
def analyze_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text[:1000]  # Limiting to first 1000 chars for efficiency
    return "No PDF uploaded."

# ---- Mermaid Diagram Function ----
def generate_mermaid_diagram(code):
    return f"""
    ```mermaid
    {code}
    ```
    """

# ---- User Inputs ----
st.subheader("Search Options")
query = st.text_input("Enter your query:")

option = st.radio("Choose a source:", ["Google Search", "Wikipedia", "Gemini AI"])

if st.button("Search"):
    if option == "Google Search":
        result = search_google(query)
    elif option == "Wikipedia":
        result = search_wikipedia(query)
    else:
        result = search_gemini(query)
    
    st.write(result)

# ---- PDF Upload ----
st.subheader("Upload a PDF for Analysis")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
if uploaded_file:
    pdf_analysis = analyze_pdf(uploaded_file)
    st.write(pdf_analysis)

# ---- Mermaid Diagram Generation ----
st.subheader("Generate a Mermaid Diagram")
diagram_code = st.text_area("Enter Mermaid diagram code:")
if st.button("Generate Diagram"):
    if diagram_code:
        mermaid_output = generate_mermaid_diagram(diagram_code)
        st.markdown(mermaid_output, unsafe_allow_html=True)
    else:
        st.error("Please enter a valid Mermaid diagram code.")

# ---- Download Response as Word Document ----
def create_download_link(content, filename):
    """Create a downloadable link for a file"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download as Word Document</a>'
    return href

if st.button("Download as Word Document"):
    result_text = query + "\n\n" + result
    st.markdown(create_download_link(result_text, "Deep_Research_Agent_Output.docx"), unsafe_allow_html=True)
