import streamlit as st
import requests
import wikipedia
from googleapiclient.discovery import build

# ✅ Correct API key retrieval
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_CSE_ID = st.secrets["google"]["cse_id"]

# ✅ Fix for Gemini AI error
def search_gemini(query):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": query}]}]}

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["candidates"][0]["output"]
    else:
        return f"Error {response.status_code}: {response.json()}"

# ✅ Fix for Google Search API error
def search_google(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        return res.get("items", [{}])[0].get("snippet", "No results found.")
    except Exception as e:
        return f"Error: {e}"

# ✅ Fix for Wikipedia API usage
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."

# ✅ Streamlit UI
st.title("Deep Research AI Agent")

query = st.text_input("Enter your research topic:")
if st.button("Search Wikipedia"):
    st.write(search_wikipedia(query))
if st.button("Search Google"):
    st.write(search_google(query))
if st.button("Ask Gemini AI"):
    st.write(search_gemini(query))
