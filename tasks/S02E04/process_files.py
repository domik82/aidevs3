import os

from icecream import ic


def process_files_in_folder(folder_path):
    # Iterate over files in the given folder
    for filename in os.listdir(folder_path):
        # file_path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            # Handle txt files
            ask_question(filename)
        elif filename.endswith(".mp3"):
            # Handle mp3 files
            convert_mp3_to_txt(filename)
            ask_question(f"Converted to text from sound file: {filename}")
        elif filename.endswith(".png"):
            # Handle png files
            read_image_and_ask_question(filename)


def ask_question(filename):
    print(f"Question about the text file: {filename}")


def convert_mp3_to_txt(filename):
    print(f"Convert mp3 to txt for: {filename}")


def read_image_and_ask_question(filename):
    print(f"Reading the image file: {filename}")


def main():
    try:
        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        resources_path = os.path.join(base_path, "resources")
        process_files_in_folder(resources_path)

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
