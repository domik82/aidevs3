import os

from src.markdown_tools.add_description_to_markdown_by_txt_files import (
    add_file_captions,
    get_description_path,
)

# Example usage
markdown_content = """
# Sample Document

![](reports/data/sample2.png)
Some text here.

![](images/data/sample1.png)

# Audio Sample
[sample.mp3](reports/data/sample.mp3)
Text here.

"""

# Sample descriptions for images
# sample_descriptions = {
#     'images/data/sample1.png': 'This is image of a single person',
#     'reports/data/sample2.png': 'This is image of a two people'
#
# }

# Example of how the directory structure should look:
"""
project_root/
    ├── reports/
    │   └── data/
    │       ├── sample1.png
    │       └── sample1_png_description.txt
    │       └── sample.mp3
    │       └── sample_mp3_description.txt
    └── images/
        └── data/
    │       ├── sample2.png
    │       └── sample2_png_description.txt
"""

root_path = os.getcwd()

# Single image analysis
# tasks/S02E05/documents/centrala_ag3nts_dane_arxiv-draft/i
resources_path = os.path.join(root_path, "project_root")
# Process the markdown
result = add_file_captions(markdown_content, resources_path)
print(result)


# Helper function to create a description file
def create_description_file(image_path, description):
    desc_path = get_description_path(image_path)
    desc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write(description)


# Example of creating description files

# create_description_file(
#     'images/data/sample1.png',
#     'This is image of a two people'
# )


# create_description_file(
#     'reports/data/sample2.png',
#     'his is image of a single person'
# )
