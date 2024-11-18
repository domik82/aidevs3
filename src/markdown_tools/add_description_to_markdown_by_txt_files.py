import re
from pathlib import Path


def get_description_path(file_path):
    """Convert image path to description file path"""
    file_path = Path(file_path)
    desc_filename = f"{file_path.stem}_{file_path.suffix[1:]}_description.txt"
    # Ensure forward slashes in the result
    return str(file_path.parent / desc_filename).replace("\\", "/")


def load_descriptions(base_path):
    """Load all available descriptions from text files"""
    descriptions = {}
    base_path = Path(base_path)

    # Find all description files
    desc_files = list(base_path.rglob("*_description.txt"))

    for desc_file in desc_files:
        try:
            with open(desc_file, "r", encoding="utf-8") as f:
                description = f.read().strip()

            # Reconstruct original image path
            original_name = desc_file.stem.rsplit("_description", 1)[0]
            image_name = original_name.rsplit("_", 1)[0]
            extension = "." + original_name.rsplit("_", 1)[1]

            # Create image path relative to base_path and ensure forward slashes
            relative_path = desc_file.parent.relative_to(base_path)
            image_path = str(relative_path / f"{image_name}{extension}").replace(
                "\\", "/"
            )

            # Store both forward and backslash versions in descriptions
            descriptions[image_path] = description
            descriptions[image_path.replace("/", "\\")] = description

        except Exception as e:
            print(f"Error loading description from {desc_file}: {str(e)}")

    return descriptions


def replace_match(match, pattern_type, descriptions):
    original_tag = match.group(0)
    file_path = match.group(2)

    # Normalize file path to forward slashes for lookup
    normalized_path = file_path.replace("\\", "/")

    # Try to get description using both path formats
    description = descriptions.get(normalized_path) or descriptions.get(
        file_path, "No description available."
    )

    file_ext = Path(file_path).suffix.lower()
    if file_ext in [".jpg", ".png", ".gif", ".jpeg"]:
        caption_type = "image-caption"
    elif file_ext in [".mp3", ".wav", ".ogg"]:
        caption_type = "audio-transcription"
    elif file_ext in [".mp4", ".avi", ".mov"]:
        caption_type = "video-description"
    else:
        caption_type = "file_caption"

    return f"{original_tag}\n*<{caption_type}> {description} </{caption_type}>*"


def add_file_captions(md_content, base_path):
    descriptions = load_descriptions(base_path)

    # Normalize all paths in markdown content to forward slashes
    md_content = md_content.replace("\\", "/")

    patterns = {
        "image": r"!\[(.*?)\]\((.*?)\)",
        "file": r"\[([^\]]+)\]\(([^)]+)\)",
    }

    modified_content = md_content
    for pattern_type, pattern in patterns.items():
        modified_content = re.sub(
            pattern,
            lambda m: replace_match(m, pattern_type, descriptions),
            modified_content,
        )

    return modified_content
