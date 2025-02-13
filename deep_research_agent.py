import streamlit as st
import openai
import wikipedia
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import base64

# Set up OpenAI API Key from Streamlit secrets
OPENAI_API_KEY = st.secrets["openai"]["api_key"]

def chat_with_openai(prompt):
    """Fetch response from OpenAI GPT."""
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        return response["choices"][0]["text"].strip()
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
        diagram_code = f"""
        <mxfile>
            <diagram>
                <mxGraphModel>
                    <root>
                        <mxCell id="0" />
                        <mxCell id="1" parent="0" />
                        <mxCell id="2" value="{input_text}" style="shape=ellipse;fillColor=#FF5733;" vertex="1" parent="1">
                            <mxGeometry width="180" height="90" as="geometry" />
                        </mxCell>
                    </root>
                </mxGraphModel>
            </diagram>
        </mxfile>
        """

        # Convert to valid PDF format
        pdf_bytes = BytesIO()
        pdf_bytes.write(diagram_code.encode('utf-8'))
        pdf_bytes.seek(0)

        return pdf_bytes
    except Exception as e:
        return f"Error generating diagram: {e}"

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
    diagram_pdf = generate_diagram(diagram_input)
    
    # Encode diagram for preview
    encoded_diagram = base64.b64encode(diagram_pdf.getvalue()).decode('utf-8')
    preview_html = f'<iframe src="data:application/pdf;base64,{encoded_diagram}" width="600" height="400"></iframe>'
    st.markdown(preview_html, unsafe_allow_html=True)
    
    st.download_button("Download Diagram as PDF", diagram_pdf, "diagram.pdf", "application/pdf")
