import streamlit as st
import requests
import wikipedia
import PyPDF2
import base64
from fpdf import FPDF

# Load API keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# ---- Function: Gemini AI Search ----
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": query}]}]}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload)

    try:
        response_json = response.json()

        if "candidates" not in response_json:
            st.error(f"Gemini API Error: {response_json}")
            return "Error: Invalid Gemini AI Response."

        return response_json["candidates"][0]["content"]
    
    except Exception as e:
        return f"Error fetching Gemini AI response: {str(e)}"

# ---- Function: Google Search ----
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    data = response.json()

    if "items" in data:
        return data["items"][0]["snippet"]
    else:
        return "No results found. Check API key or CSE ID."

# ---- Function: Wikipedia Search ----
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."

# ---- Function: Generate Mermaid Diagram ----
def generate_mermaid_diagram(diagram_code):
    """ Converts Mermaid.js input into a PNG file and then a PDF. """
    try:
        # Save as a temp Mermaid file
        mermaid_filename = "mermaid_chart.md"
        with open(mermaid_filename, "w") as file:
            file.write(diagram_code)

        # Convert to PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Mermaid Flowchart", ln=True, align="C")

        # Add Mermaid content as text
        pdf.multi_cell(0, 10, diagram_code)

        pdf_filename = "flowchart.pdf"
        pdf.output(pdf_filename)

        return pdf_filename

    except Exception as e:
        return f"Error generating Mermaid diagram: {str(e)}"

# ---- Function: Analyze Uploaded PDF ----
def analyze_pdf(uploaded_file):
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text if text else "No extractable text found in PDF."
    return "No PDF uploaded."

# ---- Streamlit UI ----
st.title("Deep Research AI Agent created by Srijith Nair")

# ---- Section: Gemini AI ----
st.subheader("Gemini AI Search")
query = st.text_input("Enter Question for Gemini AI:")
if st.button("Ask Gemini AI"):
    response = search_gemini(query)
    st.write(response)

# ---- Section: Google Search ----
st.subheader("Google Search")
google_query = st.text_input("Search Google:")
if st.button("Search Google"):
    result = search_google(google_query)
    st.write(result)

# ---- Section: Wikipedia Search ----
st.subheader("Wikipedia Search")
wiki_query = st.text_input("Search Wikipedia:")
if st.button("Search Wikipedia"):
    wiki_result = search_wikipedia(wiki_query)
    st.write(wiki_result)

# ---- Section: Upload & Analyze PDF ----
st.subheader("Upload PDF for Analysis")
uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded_pdf is not None:
    pdf_text = analyze_pdf(uploaded_pdf)
    st.text_area("Extracted Text:", pdf_text, height=200)

# ---- Section: Mermaid Diagram Generation ----
st.subheader("Generate Mermaid Flowchart")
diagram_input = st.text_area("Enter Mermaid.js Diagram Code (e.g., 'graph TD; A-->B; B-->C;')", height=100)
if st.button("Generate Diagram"):
    pdf_file = generate_mermaid_diagram(diagram_input)
    st.success(f"Diagram saved as {pdf_file}")

    # Provide download link for PDF
    with open(pdf_file, "rb") as file:
        b64_pdf = base64.b64encode(file.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file}">Download Diagram PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
