import os
from typing import Dict, List


def combine_files_in_folder(folder_path: str, output_file: str) -> None:
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")

    # Dictionary to store folder contents
    folder_contents: Dict[str, List[tuple[str, str]]] = {}

    # Read all files and organize by folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read()
                if "entry deleted" in content:
                    continue
                folder_name = os.path.basename(folder_path)
                if folder_name not in folder_contents:
                    folder_contents[folder_name] = []
                folder_contents[folder_name].append((filename, content))

    # Write organized content to output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        for folder_name, files in folder_contents.items():
            outfile.write(f"<{folder_name}>\n")
            for filename, content in files:
                outfile.write(f"<{filename}>\n{content}\n</{filename}>\n")
            outfile.write(f"</{folder_name}>\n")


def main() -> None:
    try:
        base_path = os.getcwd()
        print(base_path)
        facts_path = os.path.join(base_path, "pliki_z_fabryki/facts")
        output_file = os.path.join(base_path, "combined_facts.json")

        combine_files_in_folder(facts_path, output_file)
        print("Files have been combined successfully.")
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
