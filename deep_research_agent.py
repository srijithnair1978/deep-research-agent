import streamlit as st
import requests
import wikipedia
import googleapiclient.discovery
import graphviz
import docx
from docx import Document
from io import BytesIO

# Load API Keys from Streamlit Secrets
GEMINI_API_KEY = st.secrets["gemini"]["api_key"] if "gemini" in st.secrets and "api_key" in st.secrets["gemini"] else None
GOOGLE_API_KEY = st.secrets["google"]["api_key"] if "google" in st.secrets and "api_key" in st.secrets["google"] else None
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"] if "google" in st.secrets and "cse_id" in st.secrets["google"] else None

# Error Handling for API Keys
if not GEMINI_API_KEY:
    st.error("🚨 Missing Gemini API Key! Please update `.streamlit/secrets.toml` or Streamlit Cloud Secrets.")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    st.error("🚨 Missing Google API Key or CSE ID! Please update `.streamlit/secrets.toml` or Streamlit Cloud Secrets.")

# Function to fetch Wikipedia summary
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."

# Function to fetch results from Google Search
def search_google(query):
    try:
        service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        if "items" in result:
            return "\n\n".join([item["title"] + "\n" + item["link"] for item in result["items"][:5]])
        else:
            return "No results found."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to fetch Gemini AI response
def search_gemini(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"prompt": {"text": query}, "temperature": 0.7, "top_k": 40}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("candidates", [{}])[0].get("output", "No response available.")
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate a simple flowchart using Graphviz
def generate_diagram():
    dot = graphviz.Digraph()
    dot.node('A', 'Start')
    dot.node('B', 'Process')
    dot.node('C', 'End')
    dot.edge('A', 'B')
    dot.edge('B', 'C')
    return dot

# Function to save output as Word Document
def save_as_word(content, filename="Deep_Research_Output.docx"):
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Deep Research AI Agent - Created by Srijith Nair")

tab1, tab2, tab3, tab4 = st.tabs(["Wikipedia", "Google", "Gemini AI", "Diagram"])

# Wikipedia Search
with tab1:
    st.header("Wikipedia Search")
    wiki_query = st.text_input("Enter topic for Wikipedia Search:")
    if st.button("Search Wikipedia"):
        wiki_result = search_wikipedia(wiki_query)
        st.write(wiki_result)

# Google Search
with tab2:
    st.header("Google Search")
    google_query = st.text_input("Enter query for Google Search:")
    if st.button("Search Google"):
        google_result = search_google(google_query)
        st.write(google_result)

# Gemini AI Search
with tab3:
    st.header("Gemini AI Search")
    gemini_query = st.text_input("Enter Question for Gemini AI:")
    if st.button("Ask Gemini AI"):
        gemini_result = search_gemini(gemini_query)
        st.write(gemini_result)

# Diagram Generation
with tab4:
    st.header("Process Diagram")
    if st.button("Generate Diagram"):
        diagram = generate_diagram()
        st.graphviz_chart(diagram)

# Download Word Document
if st.button("📥 Download as Word Document"):
    combined_text = f"""
    Wikipedia Search Result:
    {wiki_result if 'wiki_result' in locals() else 'No search performed.'}

    Google Search Result:
    {google_result if 'google_result' in locals() else 'No search performed.'}

    Gemini AI Response:
    {gemini_result if 'gemini_result' in locals() else 'No response available.'}
    """
    doc_file = save_as_word(combined_text)
    st.download_button(label="📥 Download Word Document", data=doc_file, file_name="Deep_Research_Output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
