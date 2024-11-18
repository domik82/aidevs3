from typing import Dict, Match, Iterator, List
import re

from src.markdown_tools.split_markdown_by_paragraph import split_by_headers


def extract_file_paths_and_paragraphs(content: str) -> Dict[str, str]:
    """
    Extract file paths and their associated paragraphs from markdown content.

    Args:
        content: The markdown content as a string

    Returns:
        A dictionary mapping file paths to their context paragraphs
    """
    sections: List[str] = split_by_headers(content)
    results: Dict[str, str] = {}

    for section in sections:
        paragraphs: List[str] = [p.strip() for p in section.split("\n\n") if p.strip()]

        for para in paragraphs:
            # Check for image markdown
            if "![](" in para:
                file_path_match: Match[str] | None = re.search(r"\!\[\]\((.*?)\)", para)
                if file_path_match:
                    file_path: str = file_path_match.group(1)
                    section_text: str = "\n\n".join(paragraphs)
                    results[file_path] = section_text

            # Check for markdown links (including audio files)
            link_matches: Iterator[Match[str]] = re.finditer(
                r"\[([^\]]+)\]\(([^)]+)\)", para
            )
            for match in link_matches:
                file_path = match.group(2)
                section_text = "\n\n".join(paragraphs)
                results[file_path] = section_text

    return results
