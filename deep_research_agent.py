import streamlit as st
import requests
import json
import wikipedia
from PyPDF2 import PdfReader

# Set page title
st.title("Deep Research AI Agent created by Srijith Nair")

# Load API keys from Streamlit secrets
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No page found for the given query."

# Function to search Google using Custom Search API
def search_google(query):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query}
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json()
        return results.get("items", ["No results found"])
    else:
        return f"Google Search API Error: {response.status_code}"

# Function to get Claude AI response
def search_claude(query):
    headers = {"Authorization": f"Bearer {CLAUDE_API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({"prompt": query})
    response = requests.post("https://api.anthropic.com/v1/complete", headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("completion", "No Claude AI response available.")
    else:
        return f"Claude API Error: {response.status_code}"

# Function to analyze uploaded PDF
def analyze_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text[:2000]  # Limit characters to avoid overload

# Function to generate a D3.js-based visualization
def generate_d3_chart(data):
    d3_script = f"""
    <script>
        var data = {json.dumps(data)};
        var svg = d3.select("body").append("svg").attr("width", 500).attr("height", 500);
        svg.selectAll("circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", (d, i) => (i + 1) * 50)
            .attr("cy", 250)
            .attr("r", d => d.value * 5);
    </script>
    """
    return d3_script

# Interface
query = st.text_input("Enter your search query:")
search_option = st.selectbox("Choose a source:", ["Wikipedia", "Google", "Claude (Open AI)"])

if st.button("Search"):
    if search_option == "Wikipedia":
        st.write(search_wikipedia(query))
    elif search_option == "Google":
        results = search_google(query)
        for result in results:
            st.write(result.get("title", "No Title"), result.get("link", "No Link"))
    elif search_option == "Claude (Open AI)":
        st.write(search_claude(query))

# File upload for PDF analysis
uploaded_file = st.file_uploader("Upload a PDF for analysis", type="pdf")
if uploaded_file:
    st.write("Analyzing PDF...")
    st.write(analyze_pdf(uploaded_file))

# D3.js visualization
st.subheader("Generate Data Visualization")
d3_data = [{"value": i} for i in range(1, 6)]
if st.button("Generate Diagram"):
    st.components.v1.html(generate_d3_chart(d3_data), height=500)
