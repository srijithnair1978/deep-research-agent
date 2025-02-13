import streamlit as st
import openai
import fitz  # PyMuPDF for PDF processing
import requests
import wikipedia

# ---- API Keys ----
OPENAI_API_KEY = st.secrets["openai"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# ---- Function: OpenAI Search ----
def search_openai(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": query}],
            api_key=OPENAI_API_KEY
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error fetching OpenAI response: {str(e)}"

# ---- Function: Google Search ----
def search_google(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID
        }
        response = requests.get(url, params=params)
        results = response.json()
        return results.get("items", [{}])[0].get("snippet", "No results found.")
    except Exception as e:
        return f"Error fetching Google results: {str(e)}"

# ---- Function: Wikipedia Search ----
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."
    except Exception as e:
        return f"Error fetching Wikipedia results: {str(e)}"

# ---- Function: Read PDF and Extract Text ----
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(pdf_file) as doc:
        for page in doc:
            text += page.get_text()
    return text

# ---- Function: Generate Mermaid.js Flowchart Code ----
def generate_mermaid_code(text):
    summary = text[:50]  # Take first 50 characters as a summary
    return f"""
    ```mermaid
    graph TD;
        A[Start] -->|{summary}...| B[Processing];
        B --> C[Output];
    ```
    """

# ---- Streamlit UI ----
st.title("Deep Research AI Agent - Open AI Search")

# ---- Search Section ----
st.subheader("Choose Search Engine")
search_option = st.selectbox("Select an option:", ["OpenAI Search", "Google Search", "Wikipedia Search"])
query = st.text_input("Enter your search query:")

if st.button("Search"):
    if search_option == "OpenAI Search":
        result = search_openai(query)
    elif search_option == "Google Search":
        result = search_google(query)
    else:
        result = search_wikipedia(query)

    st.write(result)

# ---- PDF Upload Section ----
st.subheader("Upload and Analyze PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Text:")
    st.text_area("PDF Content:", pdf_text, height=200)

    if st.button("Generate Flowchart from PDF"):
        mermaid_code = generate_mermaid_code(pdf_text)
        st.subheader("Flowchart Representation:")
        st.markdown(mermaid_code)  # Render Mermaid diagram

# ---- Footer ----
st.write("Powered by OpenAI, Google, Wikipedia & Mermaid.js")
