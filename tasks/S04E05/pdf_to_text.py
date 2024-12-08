import os
from pypdf import PdfReader
import pymupdf
from PIL import Image
import pytesseract
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_with_ocr(pdf_path):
    # Extract regular text
    basic_text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        basic_text += page.extract_text()

    # Extract and process images
    doc = pymupdf.open(pdf_path)
    image_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()

        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert image bytes to PIL Image
            image = Image.open(BytesIO(image_bytes))

            # Perform OCR on the image
            image_text += pytesseract.image_to_string(image)

    doc.close()  # Close the document
    return basic_text + "\n" + image_text


# Usage
base_path = os.getcwd()
pdf_path = os.path.join(base_path, "notatnik-rafala.pdf")
extracted_text = extract_text_with_ocr(pdf_path)

# Save to file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)  # Removed the [2][3]
