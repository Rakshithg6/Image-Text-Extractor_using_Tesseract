import streamlit as st
import fitz
from PIL import Image
import pytesseract
import io
import os
import ctypes

# Configure Tesseract-OCR path (if required)
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def extract_images_from_pdf(pdf_file):
    images = []
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img = Image.open(io.BytesIO(image_bytes))
            images.append(img)
    return images

def extract_text_from_images(images):
    text_list = []
    for img in images:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        try:
            text = pytesseract.image_to_string(Image.open(img_bytes))
            text_list.append(text)
        except Exception as e:
            st.error(f"An error occurred while processing an image: {e}")
    return text_list

st.title('PDF Image Text Extraction')

uploaded_pdf = st.file_uploader("Choose a PDF file...", type=["pdf"])

if uploaded_pdf is not None:
    if st.button('Upload and Process'):
        # Remove the admin check
        # if not is_admin():
        #     st.error("This application requires administrator privileges. Please run it as an administrator.")
        # else:
        images = extract_images_from_pdf(uploaded_pdf)
        if images:
            try:
                text_list = extract_text_from_images(images)
                st.success("Text extracted successfully.")
                for i, text in enumerate(text_list):
                    st.write(f"Image {i+1} Text:")
                    st.text(text)
            except Exception as e:
                st.error(f"Failed to process images due to: {e}")
        else:
            st.write("No images found in the PDF.")