import json
import os

from src.markdown_tools.extract_context_around_embedded_file import (
    extract_file_paths_and_paragraphs,
)


# Example usage:
def process_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    output = extract_file_paths_and_paragraphs(content)
    return json.dumps(output, ensure_ascii=False, indent=4)


# # Usage example
base_path = os.getcwd()
md_file_path = os.path.join(os.path.join(base_path, "output", "output.md"))
print(md_file_path)

# For file input
json_output = process_markdown_file(md_file_path)
print(json_output)
