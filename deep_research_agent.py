import streamlit as st
import openai
import requests
import wikipedia
import PyPDF2
import os
from io import BytesIO
from fpdf import FPDF

# ---- 🔑 OpenAI API Key ----
openai.api_key = st.secrets["openai"]["api_key"]  # Ensure this is set in Streamlit Secrets

# ---- 📌 Function to Query OpenAI ----
def chat_with_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful AI research assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error fetching OpenAI response: {e}"

# ---- 🔍 Wikipedia Search ----
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."

# ---- 🔍 Google Search ----
def search_google(query):
    google_api_key = st.secrets["google"]["api_key"]
    google_cse_id = st.secrets["google"]["cse_id"]
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={google_cse_id}"

    response = requests.get(url)
    try:
        results = response.json()
        return results["items"][0]["snippet"] if "items" in results else "No results found."
    except:
        return "Error fetching Google results."

# ---- 📂 PDF Upload and Analysis ----
def analyze_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text if text else "No readable text found in the PDF."

# ---- 🖼️ Generate Diagram (via diagrams.net / draw.io) ----
def generate_diagram(query):
    diagram_url = f"https://www.draw.io/?title={query.replace(' ', '_')}.xml"
    return diagram_url

# ---- 🏠 Streamlit UI ----
st.title("Deep Research AI Agent by Srijith Nair")

query = st.text_input("Enter your research topic:")

if st.button("OpenAI Search"):
    st.write(chat_with_openai(query))

if st.button("Search Wikipedia"):
    st.write(search_wikipedia(query))

if st.button("Search Google"):
    st.write(search_google(query))

# ---- 📂 PDF Upload Section ----
st.subheader("Upload a PDF for Analysis")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    st.subheader("Extracted Text from PDF:")
    st.write(analyze_pdf(uploaded_file))

# ---- 📊 Generate Diagram ----
if st.button("Generate Diagram"):
    diagram_link = generate_diagram(query)
    st.markdown(f"🔗 [Click here to open your diagram in Draw.io]({diagram_link})")

# ---- 📄 Download Research as PDF ----
if st.button("Download as PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Deep Research AI Report", ln=True, align="C")
    pdf.multi_cell(0, 10, f"Research Topic: {query}\n\n")
    pdf.multi_cell(0, 10, f"OpenAI Result: {chat_with_openai(query)}\n\n")
    pdf.multi_cell(0, 10, f"Wikipedia Summary: {search_wikipedia(query)}\n\n")
    pdf.multi_cell(0, 10, f"Google Search Result: {search_google(query)}\n\n")

    if uploaded_file:
        pdf.multi_cell(0, 10, f"PDF Analysis:\n{analyze_pdf(uploaded_file)}\n\n")

    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)

    st.download_button("📥 Download Report", pdf_output, "research_report.pdf", "application/pdf")
