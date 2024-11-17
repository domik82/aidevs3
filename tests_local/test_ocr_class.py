# Basic usage with defaults (English, CPU)
import os

from src.common_aidevs.files_read_write_download import build_filename
from src.tools.perform_ocr_with_format import ImageOCR

# from src.tools.perform_ocr import ImageOCR
# # Perform OCR on an image
image_to_ocr = "2024-11-12_report-13.png"

#
ocr_processor = ImageOCR(image_to_ocr)
text = ocr_processor.perform_ocr_raw()
# don't provide output file name - will be generated automatically
ocr_processor.save_output(text)


# Get filename with extension
filename = os.path.basename(image_to_ocr)
# Get filename without extension
filename_no_ext = os.path.splitext(os.path.basename(filename))[0]
output_file_pattern = build_filename(filename_no_ext, "", suffix="ocr_raw.txt")

# Polish language with GPU
ocr_processor = ImageOCR(image_to_ocr, language="pl", use_gpu=True)
ocr_processor.process_and_save_raw_text(output_file_pattern)


output_file_pattern = build_filename(filename_no_ext, "", suffix="ocr_formatted.txt")

# For formatted output
formatted_output_file = ocr_processor.process_and_save_formatted(output_file_pattern)
