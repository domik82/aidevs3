import os
from src.markdown_tools.add_description_to_markdown_by_txt_files import (
    add_file_captions,
)

# # Usage example
base_path = os.getcwd()
print(base_path)

md_file_path = os.path.join(
    base_path, "documents\centrala_ag3nts_dane_arxiv-draft\index.md"
)
print(md_file_path)

# Read the markdown file
with open(md_file_path, "r", encoding="utf-8") as file:
    md_content = file.read()

# Process the markdown
resources_root_path = os.path.join(
    base_path, "documents\centrala_ag3nts_dane_arxiv-draft"
)

result = add_file_captions(md_content, resources_root_path)

output_path = os.path.join(base_path, "documents\centrala_ag3nts_dane_arxiv-draft")
final_md_file_path = os.path.join(output_path, "final.md")
print(result)

with open(final_md_file_path, "w", encoding="utf-8") as f:
    f.write(result)
