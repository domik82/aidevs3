from paddleocr import PaddleOCR
from datetime import datetime

# Perform OCR on an image
image_to_ocr = "2024-11-12_report-13.png"


def sort_ocr_results(result):
    # Flatten and extract coordinates and text
    text_blocks = []
    for page in result:
        for line in page:
            coords = line[0]  # Gets coordinates
            text = line[1][0]  # Gets text
            confidence = line[1][1]  # Gets confidence score

            # Calculate average y position for the text block
            y_pos = sum(coord[1] for coord in coords) / 4
            # Calculate average x position for the text block
            x_pos = sum(coord[0] for coord in coords) / 4

            text_blocks.append(
                {"text": text, "x": x_pos, "y": y_pos, "confidence": confidence}
            )

    # Define line height tolerance
    line_height = 20  # Adjust this value based on your document

    # Sort blocks first by y-position (with tolerance), then by x-position
    sorted_blocks = sorted(text_blocks, key=lambda b: (b["y"] // line_height, b["x"]))

    return sorted_blocks


# Initialize PaddleOCR
ocr = PaddleOCR(lang="pl", use_gpu=True)

# Process image
image_path = image_to_ocr
result = ocr.ocr(image_path)

# Sort the results
sorted_blocks = sort_ocr_results(result)

# Create filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"ocr_output_{timestamp}.txt"

# Write to file
with open(output_file, "w", encoding="utf-8") as file:
    current_line = None
    for block in sorted_blocks:
        # If we're on a new line (based on y-position), add a line break
        if current_line is not None and abs(block["y"] - current_line) > 20:
            file.write("\n")
        file.write(f"{block['text']} ")
        current_line = block["y"]

# # Optional: Create detailed output with coordinates and confidence
# detailed_output = f'ocr_detailed_{timestamp}.txt'
# with open(detailed_output, 'w', encoding='utf-8') as file:
#     for block in sorted_blocks:
#         file.write(f"Text: {block['text']}\n")
#         file.write(f"Position: X={block['x']:.2f}, Y={block['y']:.2f}\n")
#         file.write(f"Confidence: {block['confidence']:.4f}\n")
#         file.write("-" * 50 + "\n")
