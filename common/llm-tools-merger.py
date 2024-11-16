# this is a direct rewrite using llm of https://github.com/iceener/llm-tools-merger/blob/main/index.ts
# Needs testing

import os
import re
import sys
from typing import List


def is_text_file(filename: str) -> bool:
    binary_extensions = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".class",
        ".jar",
        ".war",
        ".ear",
        ".bin",
        ".dat",
        ".db",
        ".sqlite",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".ico",
        ".svg",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
        ".eot",
        ".fon",
        ".fnt",
        ".pfb",
        ".pfm",
        ".afm",
        ".bdf",
    }
    return (
        os.path.splitext(filename.lower())[1] not in binary_extensions
        and filename != ".DS_Store"
    )


def load_ignore_patterns(directory: str) -> List[str]:
    try:
        with open(os.path.join(directory, ".mergeignore"), "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return []


def should_ignore(file_path: str, ignore_patterns: List[str]) -> bool:
    relative_path = os.path.relpath(file_path, os.getcwd())
    ignore_dirs = {
        ".git",
        ".github",
        "node_modules",
        "vendor",
        "bower_components",
        "packages",
        "dist",
        "build",
        "target",
        "out",
        "output",
        "venv",
        "env",
        ".venv",
        ".env",
        "virtualenv",
        "jspm_packages",
        "lib",
        "libs",
        "third-party",
        "third_party",
        "externals",
        "external",
        "assets",
        "static",
        "public",
        "resources",
    }

    for pattern in ignore_patterns:
        regex_pattern = f"^{pattern.replace('*', '.*')}$"
        if re.match(regex_pattern, relative_path):
            return True

    path_parts = file_path.split(os.sep)
    return any(dir_name in ignore_dirs for dir_name in path_parts)


def merge_files(directory: str, ignore_patterns: List[str], should_log: bool) -> str:
    content = []

    for entry in os.scandir(directory):
        full_path = entry.path
        if should_ignore(full_path, ignore_patterns):
            if should_log:
                print(f"Ignoring: {full_path}")
            continue

        if entry.is_dir():
            content.append(merge_files(full_path, ignore_patterns, should_log))
        elif entry.is_file() and is_text_file(entry.name):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                content.append(
                    f'<file location="{directory}" name="{entry.name}">\n{file_content}\n</file>\n\n'
                )
                if should_log:
                    print(f"Merged: {full_path}")
            except Exception as e:
                if should_log:
                    print(f"Skipping file {full_path}: {str(e)}", file=sys.stderr)

    return "".join(content)


def is_path_safe(input_path: str) -> bool:
    normalized_path = os.path.normpath(input_path)
    resolved_path = os.path.abspath(normalized_path)
    return resolved_path.startswith(os.getcwd())


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = current_dir

    try:
        path_arg_index = sys.argv.index("--path")
        if path_arg_index + 1 < len(sys.argv):
            custom_path = sys.argv[path_arg_index + 1]
            if is_path_safe(custom_path):
                target_dir = os.path.abspath(custom_path)
            else:
                print(
                    "Error: The provided path is not safe or is outside the current working directory.",
                    file=sys.stderr,
                )
                sys.exit(1)
    except ValueError:
        pass

    output_file = os.path.join(target_dir, "merged_output.md")
    ignore_patterns = load_ignore_patterns(target_dir)
    should_log = "--log" in sys.argv

    merged_content = merge_files(target_dir, ignore_patterns, should_log)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged_content)

    if should_log:
        print(f"Merged files into {output_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)
