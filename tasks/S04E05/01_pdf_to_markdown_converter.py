import os
import pymupdf  # Changed from fitz
from PIL import Image

import pytesseract
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class PdfToMarkdownConverter:
    def __init__(self, pdf_path, output_dir="output"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images")
        os.makedirs(self.image_dir, exist_ok=True)

    def extract_images_and_ocr(self):
        """Extract images and perform OCR, returns dict of image paths and their OCR text"""
        doc = pymupdf.open(self.pdf_path)
        images_data = {}
        processed_xrefs = set()  # Track already processed images

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            text_dict = page.get_text("dict")
            image_blocks = [b for b in text_dict["blocks"] if b.get("type") == 1]

            for img_idx, img in enumerate(image_list):
                xref = img[0]

                # Skip if this image was already processed
                if xref in processed_xrefs:
                    continue

                processed_xrefs.add(xref)
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Generate unique filename using xref
                image_filename = f"image_p{page_num + 1}_xref{xref}.{image_ext}"
                image_path = os.path.join(self.image_dir, image_filename)

                # Save image only if not already saved
                if not os.path.exists(image_path):
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                # Rest of the processing...
                position = None
                for block in image_blocks:
                    if block.get("image"):
                        position = block.get("bbox", None)
                        break

                image = Image.open(BytesIO(image_bytes))
                try:
                    ocr_text = pytesseract.image_to_string(image, lang="pol")
                except Exception as e:
                    print(f"OCR failed for image {image_filename}: {str(e)}")
                    ocr_text = ""

                images_data[image_path] = {
                    "page": page_num,
                    "ocr_text": ocr_text.strip(),
                    "position": position or (0, 0, 0, 0),
                    "xref": xref,  # Store xref for reference
                }

        doc.close()
        return images_data

    def extract_text_with_positions(self):
        """Extract text with position information using multiple methods"""
        text_blocks = []
        doc = pymupdf.open(self.pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Method 1: Get text in blocks format
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[4].strip():
                    text_blocks.append(
                        {"text": block[4], "page": page_num, "position": block[:4]}
                    )

            # Method 2: Get text in dict format to catch headers
            text_dict = page.get_text("dict")
            for span in text_dict.get("spans", []):
                if span.get("text", "").strip():
                    text_blocks.append(
                        {
                            "text": span["text"],
                            "page": page_num,
                            "position": (
                                span["bbox"][0],
                                span["bbox"][1],
                                span["bbox"][2],
                                span["bbox"][3],
                            ),
                            "font_size": span.get("size", 0),
                            "font": span.get("font", ""),
                        }
                    )

        doc.close()
        return text_blocks

    def merge_content(self, text_blocks, images_data):
        """Merge text and images with improved positioning"""
        content = []

        # Remove duplicates while preserving order
        seen_texts = set()
        unique_blocks = []
        for block in text_blocks:
            text_pos = (block["text"], block["position"])
            if text_pos not in seen_texts:
                seen_texts.add(text_pos)
                unique_blocks.append(block)

        max_page = max(
            max((block["page"] for block in unique_blocks), default=-1),
            max((data["page"] for data in images_data.values()), default=-1),
        )

        for page_num in range(max_page + 1):
            page_content = []

            # Add text blocks for this page
            page_texts = [block for block in unique_blocks if block["page"] == page_num]

            # Sort text blocks by position and font size
            for text_block in page_texts:
                page_content.append(
                    {
                        "type": "text",
                        "content": text_block["text"],
                        "position": text_block["position"],
                        "page": page_num,
                        "font_size": text_block.get("font_size", 0),
                    }
                )

            # Add images
            page_images = {
                path: data
                for path, data in images_data.items()
                if data["page"] == page_num
            }
            for img_path, img_data in page_images.items():
                page_content.append(
                    {
                        "type": "image",
                        "path": img_path,
                        "ocr_text": img_data["ocr_text"],
                        "position": img_data["position"],
                        "page": page_num,
                    }
                )

            # Sort by vertical position and font size
            if page_content:
                page_content.sort(
                    key=lambda x: (
                        x["position"][1],
                        -x.get("font_size", 0) if x["type"] == "text" else 0,
                    )
                )
                content.extend(page_content)

        return content

    def generate_markdown(self, content):
        """Generate markdown from merged content with proper formatting and page numbers"""
        markdown = ""
        current_paragraph = []
        last_y_position = None
        line_spacing_threshold = 2
        current_page = -1

        for item in content:
            # Check if we're on a new page
            page_num = item.get("page", -1)
            if page_num != current_page:
                # Flush any pending paragraph before starting new page
                if current_paragraph:
                    markdown += " ".join(current_paragraph) + "\n\n"
                    current_paragraph = []

                # Add page marker
                markdown += f"\n## Page {page_num + 1}\n\n"
                current_page = page_num
                last_y_position = None

            if item["type"] == "text":
                current_y = item["position"][1]

                if last_y_position is not None:
                    y_diff = abs(current_y - last_y_position)
                    if y_diff > line_spacing_threshold:
                        if current_paragraph:
                            markdown += " ".join(current_paragraph) + "\n\n"
                            current_paragraph = []

                current_paragraph.append(item["content"])
                last_y_position = current_y

            elif item["type"] == "image":
                if current_paragraph:
                    markdown += " ".join(current_paragraph) + "\n\n"
                    current_paragraph = []

                rel_path = os.path.relpath(item["path"], self.output_dir)
                markdown += f"![Image]({rel_path})\n\n"
                if item["ocr_text"]:
                    markdown += f"<image_ocr>\n{item['ocr_text']}\n</image_ocr>\n\n"

                last_y_position = None

        # Flush any remaining paragraph
        if current_paragraph:
            markdown += " ".join(current_paragraph) + "\n\n"

        return markdown

    def convert(self):
        """Main conversion method"""
        # Extract images and perform OCR
        images_data = self.extract_images_and_ocr()

        # Extract text with positions
        text_blocks = self.extract_text_with_positions()

        # Merge content
        content = self.merge_content(text_blocks, images_data)

        # Generate markdown
        markdown = self.generate_markdown(content)

        # Save markdown
        output_path = os.path.join(self.output_dir, "output.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        return output_path


# Usage
if __name__ == "__main__":
    # Usage
    base_path = os.getcwd()
    pdf_path = os.path.join(base_path, "notatnik-rafala.pdf")
    converter = PdfToMarkdownConverter(pdf_path)
    output_path = converter.convert()
    print(f"Conversion completed. Output saved to: {output_path}")
