import streamlit as st
import wikipedia
import requests
import openai
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image, ImageDraw
import io

# --- SET PAGE TITLE ---
st.set_page_config(page_title="Deep Research AI Agent created by Srijith Nair")

st.title("Deep Research AI Agent created by Srijith Nair")

# --- CONFIGURE API KEYS ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]

# --- FUNCTION: Wikipedia Search ---
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=5)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found. Try specifying: {e.options}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."

# --- FUNCTION: Google Search ---
def search_google(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        search_results = result.get("items", [])
        return "\n".join([f"{item['title']} - {item['link']}" for item in search_results[:5]])
    except Exception as e:
        return f"Error in Google Search: {str(e)}"

# --- FUNCTION: Gemini AI Search ---
def search_gemini(query):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"prompt": {"text": query}, "temperature": 0.7}

    response = requests.post(url, json=data, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["candidates"][0]["output"]
    return "Error retrieving Gemini AI results."

# --- FUNCTION: PDF Text Extraction ---
def extract_text_from_pdf(uploaded_pdf):
    pdf_reader = PdfReader(uploaded_pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text if text else "No text found in PDF."

# --- FUNCTION: Generate a Simple Diagram ---
def generate_diagram(process_steps):
    img_width, img_height = 800, 400
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    y_position = 50
    for step in process_steps:
        draw.rectangle([(100, y_position), (700, y_position + 50)], outline="black", width=3)
        draw.text((120, y_position + 15), step, fill="black")
        y_position += 70

    return img

# --- FUNCTION: Convert Image to PDF ---
def convert_image_to_pdf(img):
    pdf_io = io.BytesIO()
    img.convert("RGB").save(pdf_io, format="PDF")
    pdf_io.seek(0)
    return pdf_io

# --- FUNCTION: Save Output to Word ---
def save_to_word(text):
    doc = Document()
    doc.add_paragraph(text)
    word_io = io.BytesIO()
    doc.save(word_io)
    word_io.seek(0)
    return word_io

# --- SELECT FUNCTIONALITY ---
st.sidebar.header("Select Research Mode")
option = st.sidebar.radio(
    "Choose an option:",
    ("Wikipedia", "Google Search", "Gemini AI", "Upload PDF", "Generate Diagram")
)

# --- EXECUTE SELECTED FUNCTION ---
if option == "Wikipedia":
    query = st.text_input("Enter Wikipedia Search Query:")
    if st.button("Search Wikipedia"):
        result = search_wikipedia(query)
        st.write(result)
        st.download_button("Download as Word", data=save_to_word(result), file_name="wikipedia_result.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif option == "Google Search":
    query = st.text_input("Enter Google Search Query:")
    if st.button("Search Google"):
        result = search_google(query)
        st.write(result)
        st.download_button("Download as Word", data=save_to_word(result), file_name="google_result.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif option == "Gemini AI":
    query = st.text_input("Enter Gemini AI Query:")
    if st.button("Ask Gemini AI"):
        result = search_gemini(query)
        st.write(result)
        st.download_button("Download as Word", data=save_to_word(result), file_name="gemini_result.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif option == "Upload PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF File", type="pdf")
    if uploaded_pdf is not None:
        text = extract_text_from_pdf(uploaded_pdf)
        st.text_area("Extracted Text", text, height=300)
        st.download_button("Download as Word", data=save_to_word(text), file_name="pdf_text.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif option == "Generate Diagram":
    st.subheader("Generate a Process Flowchart")
    process_input = st.text_area("Enter process steps (separate by commas)", "Step 1, Step 2, Step 3")

    if st.button("Generate Diagram"):
        process_steps = [step.strip() for step in process_input.split(",")]

        if process_steps:
            diagram_image = generate_diagram(process_steps)
            st.image(diagram_image, caption="Generated Process Flowchart", use_column_width=True)

            # Convert and provide download button
            pdf_file = convert_image_to_pdf(diagram_image)
            st.download_button(label="Download as PDF", data=pdf_file, file_name="flowchart.pdf", mime="application/pdf")
