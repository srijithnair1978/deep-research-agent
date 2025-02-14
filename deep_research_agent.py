import streamlit as st
import requests
import json
import wikipedia
from fpdf import FPDF

# Manually provide the Gemini API key
GEMINI_API_KEY = "YAIzaSyCyn5LuSyrKuXMKsjNsvcP03meyhCuEMO4"
GOOGLE_API_KEY = "AIzaSyCl1JDLiQim_m4ESkJELK8pZ-PIYB5SUDE"
GOOGLE_CSE_ID = "b18ad0d5fdd864c8c"

# Function to search using Gemini AI
def search_gemini(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": query}]}]}
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Extract the correct response format
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in data:
            return f"❌ Error fetching Gemini AI response: {data['error']['message']}"
        else:
            return "❌ No valid response from Gemini AI."
    except Exception as e:
        return f"❌ Error fetching Gemini AI response: {str(e)}"

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"🔎 Multiple results found: {e.options}"
    except wikipedia.exceptions.PageError:
        return "❌ No Wikipedia page found."
    except Exception as e:
        return f"❌ Error fetching Wikipedia content: {str(e)}"

# Function to search Google
def search_google(query):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
        response = requests.get(url)
        data = response.json()

        if "items" in data:
            results = "\n".join([f"🔗 {item['title']}: {item['link']}" for item in data["items"][:3]])
            return results
        elif "error" in data:
            return f"❌ Google Search Error: {data['error']['message']}"
        else:
            return "❌ No results found."
    except Exception as e:
        return f"❌ Error fetching Google results: {str(e)}"

# Function to generate a PDF with response content
def create_pdf(response, filename="response.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, response)
    
    pdf_file = f"/mnt/data/{filename}"
    pdf.output(pdf_file)
    return pdf_file

# Streamlit UI
st.title("Deep Research AI Agent")

# User Query Input
query = st.text_input("Enter your research query:")

# Option Selection
option = st.radio("Choose Search Mode:", ("Gemini AI", "Wikipedia", "Google"))

# Search Button
if st.button("Search"):
    if option == "Gemini AI":
        response = search_gemini(query)
    elif option == "Wikipedia":
        response = search_wikipedia(query)
    else:
        response = search_google(query)
    
    st.write(response)
    
    # Provide PDF Download
    pdf_path = create_pdf(response)
    with open(pdf_path, "rb") as file:
        st.download_button("Download PDF", file, file_name="Research_Response.pdf", mime="application/pdf")

# Diagram Generation using Diagrams.net (User Input)
st.subheader("Generate a Diagram")

diagram_code = st.text_area("Enter Diagram Code (Diagrams.net format):")

if st.button("Generate Diagram"):
    if diagram_code:
        diagram_url = f"https://www.draw.io/?chrome=0&lang=en&type=svg&format=xml&data={diagram_code}"
        st.markdown(f"**[Click to View Diagram]( {diagram_url} )**", unsafe_allow_html=True)
    else:
        st.warning("Please enter valid diagram code.")

