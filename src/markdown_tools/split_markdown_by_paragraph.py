import re


def split_by_headers(content):
    sections = re.split(r"(?:^|\n)#{1,6}\s+", content)
    sections = [section.strip() for section in sections if section.strip()]
    return sections
