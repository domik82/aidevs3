import cv2
from paddleocr import PaddleOCR


def preprocess_image(image_path):
    # Read image
    img = cv2.imread(image_path)

    # Resize to optimal resolution (300 DPI)
    scale_percent = 300
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    img = cv2.resize(img, (width, height))

    # Enhance contrast
    alpha = 1  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Binarization
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary)

    return denoised


def perform_enhanced_ocr(image_path, language="pl"):
    # Preprocess image
    processed_image = preprocess_image(image_path)

    # Initialize PaddleOCR with specific parameters
    ocr = PaddleOCR(
        lang=language,
        # use_angle_cls=True,  # Enable rotation detection
        # rec_char_dict_path=None,  # Use default dictionary for Polish
        rec_image_shape="3, 48, 320",  # Optimize for text recognition
        # rec_batch_num=8,
        det_db_thresh=0.3,  # Adjust detection threshold
        det_db_box_thresh=0.5,  # Adjust box threshold
        det_db_unclip_ratio=1.6,  # Adjust unclip ratio
    )

    # Perform OCR
    result = ocr.ocr(processed_image)

    # Process results
    text_blocks = []
    for page in result:
        for line in page:
            coords = line[0]
            text = line[1][0]
            confidence = line[1][1]

            # Calculate average positions
            y_pos = sum(coord[1] for coord in coords) / 4
            x_pos = sum(coord[0] for coord in coords) / 4

            text_blocks.append(
                {"text": text, "confidence": confidence, "x": x_pos, "y": y_pos}
            )

    # Sort by position
    line_height = 20
    sorted_blocks = sorted(text_blocks, key=lambda b: (b["y"] // line_height, b["x"]))

    return " ".join(block["text"] for block in sorted_blocks)


def save_denoised_image(denoised_image, output_path):
    """
    Save denoised image to file

    Args:
        denoised_image (numpy.ndarray): Preprocessed image array
        output_path (str): Path where to save the image

    Returns:
        str: Path to saved image
    """
    cv2.imwrite(output_path, denoised_image)
    return output_path


# Usage example:
"""
# Process image and save separately
image_path = "document.jpg"
processed_image = preprocess_image(image_path)
save_denoised_image(processed_image, "document_preprocessed.jpg")
"""

# Complete workflow
# Perform OCR on an image
image_to_ocr = "2024-11-12_report-13.png"

image_path = image_to_ocr
text = perform_enhanced_ocr(image_path)
print(text)

# processed_image = preprocess_image(image_to_ocr)
# save_denoised_image(processed_image, "document_preprocessed.jpg")
