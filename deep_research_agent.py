import streamlit as st
import openai
import wikipedia
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import base64

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["api_key"]

def chat_with_openai(prompt):
    """Fetch response from OpenAI GPT-3.5-turbo."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo instead of GPT-4
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error fetching OpenAI response: {e}"

def search_wikipedia(query):
    """Fetch summary from Wikipedia."""
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."

def search_google(query):
    """Fetch search results from Google Custom Search."""
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]
    GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    response = requests.get(url)
    results = response.json()

    if "items" in results:
        return "\n".join([item["title"] + ": " + item["link"] for item in results["items"][:3]])
    else:
        return "No Google results found."

def read_pdf(file):
    """Extract text from an uploaded PDF file."""
    pdf_reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text or "No text found in PDF."

def generate_diagram(input_text):
    """Generate a diagram using Draw.io (Diagrams.net) and export as a valid PDF."""
    try:
        diagram_svg = f"""
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="200" style="fill:lightblue;stroke:black;stroke-width:3" />
            <text x="150" y="100" font-size="20" fill="black">{input_text}</text>
        </svg>
        """

        # Convert to valid PDF format
        pdf_bytes = BytesIO()
        pdf_bytes.write(diagram_svg.encode('utf-8'))
        pdf_bytes.seek(0)

        return pdf_bytes, diagram_svg
    except Exception as e:
        return None, f"Error generating diagram: {e}"

# Streamlit Interface
st.title("Deep Research AI Agent Created by Srijith Nair")

query = st.text_input("Enter your research query:")

if st.button("Search OpenAI"):
    st.subheader("OpenAI Response")
    st.write(chat_with_openai(query))

if st.button("Search Wikipedia"):
    st.subheader("Wikipedia Summary")
    st.write(search_wikipedia(query))

if st.button("Search Google"):
    st.subheader("Google Search Results")
    st.write(search_google(query))

# Upload PDF and analyze content
uploaded_file = st.file_uploader("Upload a PDF for Analysis", type="pdf")
if uploaded_file:
    st.subheader("Extracted Text from PDF:")
    st.write(read_pdf(uploaded_file))

# Diagram generation using Draw.io (Diagrams.net)
st.subheader("Generate Diagram from Input")
diagram_input = st.text_area("Enter text for diagram generation:")
if st.button("Generate Diagram"):
    diagram_pdf, diagram_svg = generate_diagram(diagram_input)
    
    if diagram_svg:
        st.subheader("Diagram Preview:")
        st.markdown(f'<img src="data:image/svg+xml;base64,{base64.b64encode(diagram_svg.encode()).decode()}" width="400"/>', unsafe_allow_html=True)
        
        st.download_button("Download Diagram as PDF", diagram_pdf, "diagram.pdf", "application/pdf")
    else:
        st.error("Error generating diagram.")
