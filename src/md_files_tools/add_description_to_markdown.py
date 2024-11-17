import re
from pathlib import Path


def get_description_path(file_path):
    """Convert image path to description file path"""
    # Normalize path separators
    file_path = Path(file_path)
    # Create description filename by replacing image extension with _jpg_description.txt
    desc_filename = f"{file_path.stem}_{file_path.suffix[1:]}_description.txt"
    return file_path.parent / desc_filename


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
            # Remove _jpg to get the real name
            image_name = original_name.rsplit("_", 1)[0]
            # Reconstruct extension
            extension = "." + original_name.rsplit("_", 1)[1]

            # Create image path relative to base_path
            relative_path = desc_file.parent.relative_to(base_path)
            # TODO: This could be windows thing
            # image_path = str(relative_path / f"{image_name}{extension}").replace('\\', '/')
            image_path = str(relative_path / f"{image_name}{extension}")

            descriptions[image_path] = description

        except Exception as e:
            print(f"Error loading description from {desc_file}: {str(e)}")

    return descriptions


def add_file_captions(md_content, base_path):
    # Load all available descriptions
    descriptions = load_descriptions(base_path)

    # Print descriptions for debugging
    print("Loaded descriptions:", descriptions)

    # Patterns to match both image and regular file syntax in markdown
    patterns = {
        "image": r"!\[(.*?)\]\((.*?)\)",  # For image syntax: ![alt](path)
        "file": r"\[([^\]]+)\]\(([^)]+)\)",  # For regular file syntax: [text](path)
    }

    def replace_match(match, pattern_type):
        original_tag = match.group(0)
        print(f"original_tag: {original_tag}")
        file_path = match.group(2)
        print(f"file_path: {file_path}")

        print(f"Available keys in descriptions: {list(descriptions.keys())}")

        # Try to get description for this file
        description = descriptions.get(file_path, "No description available.")

        # Determine caption prefix based on file type
        file_ext = Path(file_path).suffix.lower()
        if file_ext in [".jpg", ".png", ".gif", ".jpeg"]:
            caption_type = "image_caption"
        elif file_ext in [".mp3", ".wav", ".ogg"]:
            caption_type = "audio_caption"
        elif file_ext in [".mp4", ".avi", ".mov"]:
            caption_type = "video_caption"
        else:
            caption_type = "file_caption"

        return f"{original_tag}\n*{caption_type}: {description}*"

    # Process the content for both patterns
    modified_content = md_content
    for pattern_type, pattern in patterns.items():
        modified_content = re.sub(
            pattern, lambda m: replace_match(m, pattern_type), modified_content
        )

    return modified_content
