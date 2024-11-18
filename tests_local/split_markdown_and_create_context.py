import json

from src.markdown_tools.extract_context_around_embedded_file import (
    extract_file_paths_and_paragraphs,
)

# Example usage
markdown_content = """# Main Title

Some introduction text.

![](i/welcome.png)

after

## Section 1

In one of our most spectacular tests, we managed to transmit a photographic image 
to the past with exceptional accuracy and data stability.

![](i/rynek.png)

Original photo description.

### Subsection

More detailed information.

![](i/rynek_glitch.png)

Damage visible in the recovered graphic file.

## Section 2

Another section content.
![](i/rynek_no_glitch.png)

Some more
[rafal_dyktafon.mp3](i/rafal_dyktafon.mp3)
"""

output = extract_file_paths_and_paragraphs(markdown_content)
print(json.dumps(output, ensure_ascii=False, indent=2))
