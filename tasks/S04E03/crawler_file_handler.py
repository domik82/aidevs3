import os
from pathlib import Path


class CrawlerFileHandler:
    def __init__(self, output_dir):
        # self.output_dir = output_dir
        pass

    def save_markdown(self, content: str, page_dir: Path) -> None:
        """
        Save markdown content to a file

        Args:
            content: Markdown content to save
            page_dir: Directory to save the file in
        """
        md_path = page_dir / "index.md"
        self._write_file(md_path, content)

    def save_html(self, content: str, page_dir: Path) -> None:
        """
        Save HTML content to a file

        Args:
            content: HTML content to save
            page_dir: Directory to save the file in
        """
        if page_dir is None:
            html_path = os.path.join("index.html")
        else:
            html_path = os.path.join(page_dir, "index.html")
        self._write_file(html_path, content)

    @staticmethod
    def _write_file(path, content: str) -> None:
        """
        Write content to a file with proper encoding

        Args:
            path: Path to save the file
            content: Content to write
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
