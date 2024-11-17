import os


# This file was used only to generate the structure of the folders so I could test an idea


def create_project_structure():
    # Define the base directory
    base_dir = "project_root"

    # Create directory structure
    directories = ["reports/data", "images/data"]

    # Create directories
    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)

    # Sample descriptions for images
    sample_descriptions = {
        "images/data/sample1.png": "This is image of a single person",
        "reports/data/sample2.png": "This is image of a two people",
    }

    # Create the description text files
    for image_path, description in sample_descriptions.items():
        # Get the corresponding description file path
        # Replace the image file extension with a description file extension
        extension = "png"
        description_file = os.path.join(
            base_dir,
            image_path.replace(f".{extension}", f"_{extension}_description.txt"),
        )

        # Create the directory for the description file if it doesn't exist
        os.makedirs(os.path.dirname(description_file), exist_ok=True)

        # Write the description to the file
        with open(description_file, "w", encoding="utf-8") as f:
            f.write(description)

        # # Create an empty placeholder for the jpg file
        # image_file = os.path.join(base_dir, image_path)
        # with open(image_file, 'w') as f:
        #     f.write('# This is a placeholder for the actual image file')

    print("Created directory structure:")
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


if __name__ == "__main__":
    create_project_structure()
