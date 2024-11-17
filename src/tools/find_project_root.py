import os


def find_project_root(current_file, marker=".project_root"):
    current_path = os.path.abspath(os.path.dirname(current_file))
    while current_path != "/":
        if os.path.exists(os.path.join(current_path, marker)):
            return current_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError(f"Project root marker '{marker}' not found")
