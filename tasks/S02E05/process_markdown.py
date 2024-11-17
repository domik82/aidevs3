import os

from markdownify import markdownify as md

from src.md_files_tools.add_description_to_markdown import add_file_captions


def process_markdown_file(file_path):
    # Read the markdown file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Convert to ensure consistent markdown formatting
    markdown_content = md(content)

    # Split by headers (##)
    paragraphs = [p.strip() for p in markdown_content.split("##") if p.strip()]

    # Process each paragraph
    for i, paragraph in enumerate(paragraphs, 1):
        # Get the first line as header
        header = paragraph.split("\n")[0].strip()
        print(f"Processing paragraph {i}: {header}")

        # Find media files
        media_files = []
        for line in paragraph.split("\n"):
            words = line.split()
            for word in words:
                if word.lower().endswith((".jpg", ".mp3")):
                    media_files.append(word)

        if media_files:
            print(f"Found media files in paragraph {i}:")
            for media_file in media_files:
                print(f"- {media_file}")
        print()


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

#
# process_markdown_file(output_file)
# root_path = os.getcwd()

# Single image analysis
# tasks/S02E05/documents/centrala_ag3nts_dane_arxiv-draft/i

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
