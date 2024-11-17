from paddleocr import PaddleOCR
from datetime import datetime
from typing import List, Dict, Optional


class ImageOCR:
    def __init__(self, image_path: str, language: str = "en", use_gpu: bool = True):
        """
        Initialize ImageOCR with configuration parameters.

        Args:
            image_path (str): Path to the image file
            language (str): Language code (default: 'en', example: 'pl' for Polish)
            use_gpu (bool): Whether to use GPU acceleration (default: True)
        """
        self.image_path = image_path
        self.language = language
        self.use_gpu = use_gpu
        self.ocr_instance = PaddleOCR(
            lang=language, use_gpu=use_gpu, use_angle_cls=True
        )
        self.line_height = 20  # Default line height for text sorting

    def _extract_text_blocks(self, ocr_result: List) -> List[Dict]:
        """
        Extract and process text blocks from OCR result.

        Args:
            ocr_result (List): Raw OCR result from PaddleOCR

        Returns:
            List[Dict]: List of processed text blocks with position information
        """
        text_blocks = []
        for page in ocr_result:
            for line in page:
                coords = line[0]
                text = line[1][0]
                confidence = line[1][1]

                # Calculate average positions
                y_pos = sum(coord[1] for coord in coords) / 4
                x_pos = sum(coord[0] for coord in coords) / 4

                text_blocks.append(
                    {"text": text, "x": x_pos, "y": y_pos, "confidence": confidence}
                )
        return text_blocks

    def _sort_blocks_raw(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Sort text blocks by their position for raw text output.

        Args:
            text_blocks (List[Dict]): List of text blocks to sort

        Returns:
            List[Dict]: Sorted text blocks
        """
        return sorted(text_blocks, key=lambda b: (b["y"] // self.line_height, b["x"]))

    def _sort_blocks_formatted(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Sort text blocks preserving formatting.

        Args:
            text_blocks (List[Dict]): List of text blocks to sort

        Returns:
            List[Dict]: Sorted text blocks with formatting preservation
        """
        return sorted(text_blocks, key=lambda b: (b["y"] // self.line_height, b["x"]))

    def perform_ocr_raw(self) -> str:
        """
        Perform OCR and return raw text.

        Returns:
            str: Extracted and sorted text from the image
        """
        result = self.ocr_instance.ocr(self.image_path)
        text_blocks = self._extract_text_blocks(result)
        sorted_blocks = self._sort_blocks_raw(text_blocks)
        return " ".join(block["text"] for block in sorted_blocks)

    def perform_ocr_formatted(self) -> List[Dict]:
        """
        Perform OCR and return formatted blocks.

        Returns:
            List[Dict]: Sorted text blocks with formatting information
        """
        result = self.ocr_instance.ocr(self.image_path)
        text_blocks = self._extract_text_blocks(result)
        return self._sort_blocks_formatted(text_blocks)

    def save_output(self, text: str, filename: Optional[str] = None) -> str:
        """
        Save OCR output to a file.

        Args:
            text (str): Text to save
            filename (Optional[str]): Output filename (default: generates timestamp-based filename)

        Returns:
            str: Name of the file where text was saved
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_output_{timestamp}.txt"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)

        return filename

    def process_and_save_raw_text(self, output_filename: Optional[str] = None) -> str:
        """
        Perform OCR and save raw text results in one step.

        Args:
            output_filename (Optional[str]): Output filename (default: generates timestamp-based filename)

        Returns:
            str: Name of the file where text was saved
        """
        text = self.perform_ocr_raw()
        return self.save_output(text, output_filename)

    def process_and_save_formatted(self, output_filename: Optional[str] = None) -> str:
        """
        Perform OCR and save formatted results in one step.

        Args:
            output_filename (Optional[str]): Output filename (default: generates timestamp-based filename)

        Returns:
            str: Name of the file where text was saved
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ocr_output_formatted_{timestamp}.txt"

        sorted_blocks = self.perform_ocr_formatted()

        with open(output_filename, "w", encoding="utf-8") as file:
            current_line = None
            for block in sorted_blocks:
                # If we're on a new line (based on y-position), add a line break
                if (
                    current_line is not None
                    and abs(block["y"] - current_line) > self.line_height
                ):
                    file.write("\n")
                file.write(f"{block['text']} ")
                current_line = block["y"]

        return output_filename


# Usage example:
"""
ocr = ImageOCR("image.jpg", language='pl', use_gpu=True)

# For raw text output
raw_output_file = ocr.process_and_save_raw_text("raw_output.txt")

# For formatted output
formatted_output_file = ocr.process_and_save_formatted("formatted_output.txt")
"""
