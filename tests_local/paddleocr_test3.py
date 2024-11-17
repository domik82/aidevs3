def perform_ocr(image_path, language="en", use_gpu=False):
    """
    Perform OCR on an image with specified language and GPU settings.

    Args:
        image_path (str): Path to the image file
        language (str): Language code (default: 'en', example: 'pl' for Polish)
        use_gpu (bool): Whether to use GPU acceleration (default: False)

    Returns:
        str: Extracted and sorted text from the image
    """
    from paddleocr import PaddleOCR

    # Initialize PaddleOCR with specified parameters
    ocr = PaddleOCR(lang=language, use_gpu=use_gpu, use_angle_cls=True)

    # Perform OCR
    result = ocr.ocr(image_path)

    # Process and sort results
    text_blocks = []
    for page in result:
        for line in page:
            coords = line[0]
            text = line[1][0]

            # Calculate average positions
            y_pos = sum(coord[1] for coord in coords) / 4
            x_pos = sum(coord[0] for coord in coords) / 4

            text_blocks.append({"text": text, "x": x_pos, "y": y_pos})

    # Sort blocks by position
    line_height = 20
    sorted_blocks = sorted(text_blocks, key=lambda b: (b["y"] // line_height, b["x"]))

    return " ".join(block["text"] for block in sorted_blocks)


def save_output_to_file(text, filename=None):
    """
    Save text to a file with optional filename.

    Args:
        text (str): Text to save
        filename (str): Output filename (default: generates timestamp-based filename)
    """
    from datetime import datetime

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ocr_output_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

    return filename


# Usage examples:
"""
# Basic usage with defaults (English, CPU)
text = perform_ocr("image.jpg")
save_output_to_file(text)

# Polish language with GPU
text = perform_ocr("image.jpg", language='pl', use_gpu=True)
save_output_to_file(text, "custom_output.txt")

# Just changing language
text = perform_ocr("image.jpg", language='pl')
save_output_to_file(text)

# Just enabling GPU
text = perform_ocr("image.jpg", use_gpu=True)
save_output_to_file(text)
"""
# Perform OCR on an image
image_to_ocr = "2024-11-12_report-13.png"

text = perform_ocr(image_to_ocr, language="pl", use_gpu=True)
save_output_to_file(text, "custom_output.txt")
