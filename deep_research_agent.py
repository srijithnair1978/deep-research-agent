import streamlit as st
from PIL import Image, ImageDraw
import io

# Function to generate a simple diagram
def generate_diagram(process_steps):
    # Create a blank image
    img_width, img_height = 800, 400
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Draw simple flowchart-like elements
    y_position = 50
    for step in process_steps:
        draw.rectangle([(100, y_position), (700, y_position + 50)], outline="black", width=3)
        draw.text((120, y_position + 15), step, fill="black")
        y_position += 70  # Space between steps

    return img

# Function to convert image to PDF
def convert_image_to_pdf(img):
    pdf_io = io.BytesIO()
    img.convert("RGB").save(pdf_io, format="PDF")
    pdf_io.seek(0)
    return pdf_io

# Streamlit UI
st.title("Deep Research AI Agent created by Srijith Nair")

# Diagram Generation Section
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
