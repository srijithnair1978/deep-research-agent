import streamlit as st
import requests
import wikipedia
from fpdf import FPDF

# ------------------------------#
# **MANUALLY ENTER GEMINI API KEY**
GEMINI_API_KEY = "AIzaSyCyn5LuSyrKuXMKsjNsvcP03meyhCuEMO4"

# **MANUALLY ENTER GOOGLE API & CSE ID**
GOOGLE_API_KEY = "AIzaSyCl1JDLiQim_m4ESkJELK8pZ-PIYB5SUDE"
GOOGLE_CSE_ID = "b18ad0d5fdd864c8c"

# ------------------------------#
# **FUNCTION TO SEARCH WIKIPEDIA**
def search_wikipedia(query):
    try:
        result = wikipedia.summary(query, sentences=3)  # Get first 3 sentences
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e.options[:5]} (Try being more specific)"
    except wikipedia.exceptions.PageError:
        return "No matching page found on Wikipedia."
    except Exception as e:
        return f"Error fetching Wikipedia data: {str(e)}"

# ------------------------------#
# **FUNCTION TO SEARCH GOOGLE**
def search_google(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "items" in data:
            return "\n".join([item["title"] + ": " + item["link"] for item in data["items"][:3]])
        elif "error" in data:
            return f"Google Search Error: {data['error']['message']}"
        else:
            return "No results found."
    except Exception as e:
        return f"Error fetching Google search results: {str(e)}"

# ------------------------------#
# **FUNCTION TO QUERY GEMINI AI**
def search_gemini(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": query}]}]}
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "candidates" in data:
            return data["candidates"][0]["output"]
        else:
            return f"Error fetching Gemini AI response: {data}"
    except Exception as e:
        return f"Error fetching Gemini AI response: {str(e)}"

# ------------------------------#
# **FUNCTION TO CREATE PDF**
def create_pdf(response):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Ensure UTF-8 encoding
    response_text = response.encode("utf-8", "ignore").decode("utf-8")

    pdf.multi_cell(0, 10, response_text)

    pdf_file = "output.pdf"
    pdf.output(pdf_file, "F")
    return pdf_file

# ------------------------------#
# **STREAMLIT UI**
st.title("Deep Research AI Agent")

query = st.text_input("Enter your research topic:")

if st.button("Search Wikipedia"):
    wiki_result = search_wikipedia(query)
    st.write(wiki_result)

if st.button("Search Google"):
    google_result = search_google(query)
    st.write(google_result)

if st.button("Ask Gemini AI"):
    gemini_result = search_gemini(query)
    st.write(gemini_result)

    # Provide PDF Download
    pdf_file = create_pdf(gemini_result)
    with open(pdf_file, "rb") as f:
        st.download_button("Download as PDF", f, file_name="Gemini_Response.pdf", mime="application/pdf")

