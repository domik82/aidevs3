from paddleocr import PaddleOCR

# pip install paddlepaddle paddleocr


from paddleocr import draw_ocr
from PIL import Image

# Perform OCR on an image
image_to_ocr = "2024-11-12_report-13.png"


# Initialize with additional parameters
ocr = PaddleOCR(
    lang="pl",
    use_angle_cls=True,  # Enable angle classification for rotated text
    use_gpu=True,
)  # Set to True if GPU is available


# Process image
image_path = image_to_ocr
result = ocr.ocr(image_path)
image = Image.open(image_path).convert("RGB")

# Correct way to extract boxes, texts, and scores
boxes = [line[0] for line in result[0]]  # Get coordinates
texts = [line[1][0] for line in result[0]]  # Get texts
scores = [line[1][1] for line in result[0]]  # Get confidence scores

# Specify a system font path for visualization
# On Windows, you can use Arial or another system font
font_path = "C:\\Windows\\Fonts\\Arial.ttf"  # Windows path
# For Linux: font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Draw results
result_image = draw_ocr(image, boxes, texts, scores, font_path=font_path)
result_image = Image.fromarray(result_image)
result_image.save("result.jpg")

# Print recognized text
for idx in range(len(result)):
    for line in result[idx]:
        print(f"Text: {line[1][0]}, Confidence: {line[1][1]}")
