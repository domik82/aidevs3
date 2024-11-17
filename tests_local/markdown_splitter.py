def analyze_md_file(content):
    paragraphs = []
    media_files = []

    # Split content by paragraphs (indicated by ##)
    sections = content.split("## ")
    for section in sections:
        # Trim section to remove leading/trailing whitespace
        trimmed_section = section.strip()
        if trimmed_section:
            paragraphs.append(trimmed_section)
        # Check for .jpg and .mp3 files
        media_candidates = trimmed_section.split()
        media_files.extend(
            [file for file in media_candidates if file.endswith(("jpg", "mp3"))]
        )

    return paragraphs, media_files


def process_paragraphs(paragraphs):
    for i, paragraph in enumerate(paragraphs):
        print(f"Processing paragraph {i + 1}: {paragraph[:30]}...")


def print_media_files(media_files):
    if media_files:
        print("\nFound media files:")
        for file in media_files:
            print(f"- {file}")


# Usage example
content = """## Introduction
This is the first paragraph with image.jpg
## Methods
Here's another image2.jpg and song.mp3
## Results
Final paragraph"""

paragraphs, media_files = analyze_md_file(content)
process_paragraphs(paragraphs)
print_media_files(media_files)
