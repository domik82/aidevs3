import os
import json
from icecream import ic

from src.audio_tools.convert_mp3_using_whisper import convert_mp3_to_txt
from src.markdown_tools.extract_context_around_embedded_file import (
    extract_file_paths_and_paragraphs,
)
from src.video_tools.describe_with_llm import describe_image


def read_description_file(description_path):
    try:
        with open(description_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        ic(f"Error reading description file {description_path}: {str(e)}")
        return None


def process_files_recursively(root_folder, context):
    results = {}

    # Walk through all subdirectories
    for root, dirs, files in os.walk(root_folder):
        for filename in files:
            # Skip description files
            if "_description.txt" in filename:
                continue

            file_path = os.path.join(root, filename)
            output_dir = root
            extension = os.path.splitext(filename)[1].replace(".", "")
            suffix = f"{extension}_description"
            description_filename = f"{os.path.splitext(filename)[0]}_{suffix}.txt"
            description_path = os.path.join(output_dir, description_filename)

            # Create relative path from root folder using forward slashes
            relative_path = os.path.relpath(file_path, root_folder).replace("\\", "/")

            try:
                # Process file based on extension if description doesn't exist
                if filename.endswith(".txt"):
                    # text = read_txt_file(file_path)
                    pass
                elif filename.endswith(".mp3"):
                    convert_mp3_to_txt(
                        file_path=file_path,
                        output_dir=output_dir,
                        suffix=suffix,
                        overwrite=False,
                    )
                    description = read_description_file(description_path)
                    if description is not None:
                        results[relative_path] = description
                elif filename.endswith(".png"):
                    additional_context = context.get(relative_path)
                    describe_image(
                        file_path,
                        output_dir=output_dir,
                        suffix=suffix,
                        additional_context=additional_context,
                        overwrite=False,
                    )
                    description = read_description_file(description_path)
                    if description is not None:
                        results[relative_path] = description

            except Exception as e:
                ic(f"Error processing {file_path}: {str(e)}")
                results[relative_path] = f"Error processing file: {str(e)}"

    return results


def save_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, ensure_ascii=False, indent=2, fp=f)


def main():
    try:
        # Get base path and construct root folder path
        base_path = os.getcwd()
        root_folder = os.path.join(
            base_path, "output", "documents", "centrala_ag3nts_dane_arxiv-draft"
        )
        md_file_path = os.path.join(root_folder, "index.md")
        with open(md_file_path, "r", encoding="utf-8") as file:
            md_content = file.read()

        # Extract context around all files
        output = extract_file_paths_and_paragraphs(md_content)

        # Process all files with context
        results = process_files_recursively(root_folder, output)

        # Save results to JSON file
        output_file = os.path.join(root_folder, "file_descriptions.json")
        save_json(results, output_file)

        # Print results
        ic(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
