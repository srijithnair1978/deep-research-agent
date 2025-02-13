import streamlit as st
import requests
import json
import wikipedia
from fpdf import FPDF
import base64

# 🔹 Manually define Gemini API Key here
GEMINI_API_KEY = "AIzaSyCyn5LuSyrKuXMKsjNsvcP03meyhCuEMO4"

# Function to query Gemini AI
def query_gemini_ai(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except KeyError:
            return "⚠️ No valid response received from Gemini AI."
    else:
        return f"❌ Error fetching Gemini AI response: {response.status_code} - {response.text}"

# Function to search Google (Custom Search API)
def search_google(query, google_api_key, google_cse_id):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={google_cse_id}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            results = response.json().get("items", [])
            return "\n\n".join([f"🔗 [{res['title']}]({res['link']})" for res in results[:5]])
        except KeyError:
            return "⚠️ No results found."
    else:
        return f"❌ Google Search Error: {response.status_code} - {response.text}"

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.PageError:
        return "⚠️ No matching Wikipedia page found."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ Multiple results found: {', '.join(e.options[:5])}..."
    except Exception as e:
        return f"❌ Wikipedia Error: {str(e)}"

# Function to generate and display diagrams from diagrams.net
def generate_diagram(data):
    diagram_url = "https://www.diagrams.net/diagram-export"
    payload = {"format": "png", "data": data}
    response = requests.post(diagram_url, json=payload)

    if response.status_code == 200:
        return response.content
    else:
        return None

# Function to read and analyze PDF
def analyze_pdf(uploaded_file):
    from PyPDF2 import PdfReader
    pdf_reader = PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text[:1000]  # Limiting text for demo

# Function to create a downloadable PDF
def create_pdf(content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, content)

    pdf_file = "output.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        pdf_data = f.read()
    
    b64 = base64.b64encode(pdf_data).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="generated_output.pdf">📄 Download PDF</a>'

# ---------- Streamlit UI ----------
st.title("Deep Research AI Agent")

st.sidebar.header("🔍 Search Options")
query = st.sidebar.text_input("Enter your research query")

option = st.sidebar.radio("Choose a search method:", ("Gemini AI", "Google Search", "Wikipedia", "Upload PDF", "Generate Diagram"))

if option == "Gemini AI":
    if query:
        st.subheader("Gemini AI Response:")
        response = query_gemini_ai(query)
        st.write(response)
        st.markdown(create_pdf(response), unsafe_allow_html=True)

elif option == "Google Search":
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
    GOOGLE_CSE_ID = "YOUR_GOOGLE_CSE_ID"

    if query:
        st.subheader("Google Search Results:")
        response = search_google(query, GOOGLE_API_KEY, GOOGLE_CSE_ID)
        st.markdown(response, unsafe_allow_html=True)
        st.markdown(create_pdf(response), unsafe_allow_html=True)

elif option == "Wikipedia":
    if query:
        st.subheader("Wikipedia Summary:")
        response = search_wikipedia(query)
        st.write(response)
        st.markdown(create_pdf(response), unsafe_allow_html=True)

elif option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        pdf_text = analyze_pdf(uploaded_file)
        st.subheader("PDF Analysis:")
        st.write(pdf_text)
        st.markdown(create_pdf(pdf_text), unsafe_allow_html=True)

elif option == "Generate Diagram":
    diagram_data = st.text_area("Enter diagram data for diagrams.net (XML format)")
    if st.button("Generate Diagram"):
        diagram_image = generate_diagram(diagram_data)
        if diagram_image:
            st.image(diagram_image, caption="Generated Diagram")
            st.markdown(create_pdf("Diagram Generated"), unsafe_allow_html=True)
        else:
            st.error("Failed to generate diagram. Please check input format.")
