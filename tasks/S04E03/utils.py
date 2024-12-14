from urllib.parse import urlparse

from pathvalidate import sanitize_filename
from markdownify import markdownify


def url_to_foldername(url: str, max_length: int = 50) -> str:
    parsed = urlparse(url)
    name_parts = []

    # Process domain
    domain = parsed.netloc.split(":")[0].split(".")[:-1]
    name_parts.extend(domain)

    # Process path
    path = parsed.path.strip("/")
    if path:
        path = path.replace(".html", "").replace(".htm", "")
        name_parts.extend(path.split("/"))

    folder_name = "_".join(name_parts)
    folder_name = sanitize_filename(folder_name)

    if len(folder_name) > max_length:
        folder_name = folder_name[: max_length - 3] + "..."

    return folder_name or "index"


def html_to_markdown(html_content: str, metadata: dict = None) -> str:
    try:
        markdown_content = markdownify(html_content, heading_style="ATX", bullets="*")
        markdown_content = markdown_content.replace("\\", "/")

        if metadata:
            header = "---\n"
            for key, value in metadata.items():
                header += f"{key}: {value}\n"
            header += "---\n\n"
            return header + markdown_content

        return markdown_content
    except Exception as e:
        print(f"Failed to convert HTML to Markdown: {str(e)}")
        return None
