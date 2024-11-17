import os

from icecream import ic

from src.audio_tools.convert_mp3_using_whisper import convert_mp3_to_txt

from src.video_tools.describe_with_llm import describe_image


def process_files_in_folder(folder_path):
    output_path = os.path.join(folder_path, "")

    for filename in os.listdir(folder_path):
        # Skip files containing "transcribe" or "ocr"
        suffix = "description"
        if f"_{suffix}.txt" in filename:
            continue

        file_path = os.path.join(folder_path, filename)
        # Process file based on type and get classification
        # TODO: handle that in better way

        extension = os.path.splitext(filename)[1].replace(".", "")

        full_suffix = f"{extension}_{suffix}"

        if filename.endswith(".txt"):
            # text = read_txt_file(file_path)
            pass
        elif filename.endswith(".mp3"):
            convert_mp3_to_txt(
                file_path=file_path, output_dir=output_path, suffix=full_suffix
            )
        elif filename.endswith(".png"):
            describe_image(file_path, output_dir=output_path, suffix=full_suffix)


def main():
    try:
        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        # tasks/S02E05/documents/centrala_ag3nts_dane_arxiv-draft/i
        resources_path = os.path.join(
            base_path, "documents\centrala_ag3nts_dane_arxiv-draft\i"
        )
        process_files_in_folder(resources_path)

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
