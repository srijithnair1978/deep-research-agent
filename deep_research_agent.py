import streamlit as st
import requests
import PyPDF2  # For PDF processing

# ========================== GEMINI AI SETUP ==========================
GEMINI_API_KEY = "AIzaSyCyn5LuSyrKuXMKsjNsvcP03meyhCuEMO4"  # Replace with your actual API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

# ========================== FUNCTION TO QUERY GEMINI ==========================
def search_gemini(query):
    """Sends a query to Google Gemini AI and returns the response."""
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": query}]}]}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        response_data = response.json()
        
        if "candidates" in response_data:
            return response_data["candidates"][0]["output"]
        else:
            return "❌ No valid response received from Gemini API. Please check API key."
    
    except Exception as e:
        return f"❌ Error fetching data from Gemini AI: {str(e)}"

# ========================== MERMAID.JS DIAGRAM RENDER ==========================
def render_mermaid_diagram(mermaid_code):
    """Embeds Mermaid.js in Streamlit to generate diagrams."""
    mermaid_html = f"""
    <script type="module">
        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
        mermaid.initialize({{startOnLoad:true}});
    </script>
    <div class="mermaid">
        {mermaid_code}
    </div>
    """
    st.components.v1.html(mermaid_html, height=500)

# ========================== PDF UPLOAD & ANALYSIS ==========================
def extract_text_from_pdf(uploaded_file):
    """Extracts text from uploaded PDF files."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}"

# ========================== STREAMLIT UI ==========================
st.title("📚 Deep Research AI Agent by **Srijith Nair**")
st.subheader("🔍 AI-Powered Research with Gemini & Diagram Visualization using Mermaid.js")

# ------------------ Gemini AI Search ------------------
st.write("### 🤖 Ask Gemini AI:")
query = st.text_input("Enter your query for Gemini AI:")
if st.button("Ask Gemini AI"):
    if query.strip():
        response = search_gemini(query)
        st.write("### Gemini AI Response:")
        st.success(response)
    else:
        st.error("⚠️ Please enter a question!")

# ------------------ PDF Upload & Analysis ------------------
st.write("### 📄 Upload a PDF for Analysis:")
uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded_pdf:
    st.write("✅ PDF Uploaded Successfully! Extracted Text Below:")
    extracted_text = extract_text_from_pdf(uploaded_pdf)
    st.text_area("Extracted Text:", extracted_text, height=300)

# ------------------ Mermaid.js Diagram Generator ------------------
st.write("### 📊 Generate a Diagram with Mermaid.js:")
mermaid_code = st.text_area("Enter Mermaid.js Code Below:", """
graph TD;
A[Start] --> B{Decision};
B -->|Yes| C[Continue];
B -->|No| D[Stop];
""")

if st.button("Generate Diagram"):
    render_mermaid_diagram(mermaid_code)
