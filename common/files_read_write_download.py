import requests
from icecream import ic
from requests import Response
from requests.exceptions import RequestException
import os
from urllib.parse import urlparse
from typing import Optional, Union


def get_data_from_url(url: str, retries: int = 3, timeout: int = 5) -> Response.content:
    attempt = 0
    while attempt < retries:
        try:
            ic(f"Request attempt: {attempt}")
            response = requests.get(url, timeout=timeout)
            ic(f"Request status code: {response.status_code}")
            response.raise_for_status()  # Raise an error for bad responses
            return response.content  # Return success
        except RequestException as e:
            attempt += 1
            ic(f"Attempt {attempt} failed: {e}")
    return None  # Return failure after retries


def download_file(
    url: str,
    path: Optional[str] = None,
    file_name: Optional[str] = None,
    retries: int = 3,
    timeout: int = 5,
) -> bool:
    if path is None:
        path = os.getcwd()  # current directory

    if file_name is None:
        file_name = get_filename_from_url(url)

    file_path = os.path.join(path, file_name)

    attempt = 0
    while attempt < retries:
        try:
            ic(f"Downloading attempt: {attempt}")
            response = requests.get(url, timeout=timeout)
            ic(f"Downloading status_code: {response.status_code}")
            response.raise_for_status()  # Raise an error for bad responses
            ic(f"Will save to: {file_path}")
            save_file(response.content, file_path)
            return True  # Return success
        except RequestException as e:
            attempt += 1
            ic(f"Attempt {attempt} failed: {e}")
    return False  # Return failure after retries


def save_file(content: Union[str, bytes], filepath: str) -> None:
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(filepath, mode) as file:
        file.write(content)


def read_file(filepath: str) -> bytes:
    with open(filepath, "rb") as file:
        return file.read()


def get_filename_from_url(url: str) -> str:
    return urlparse(url).path.split("/")[-1]


if __name__ == "__main__":
    dl_url: str = "https://poligon.aidevs.pl/dane.txt"
    response = get_data_from_url(dl_url)
    ic(response)

    success: bool = download_file(dl_url, retries=5, timeout=10)
    if success:
        data: bytes = read_file(get_filename_from_url(dl_url))
        ic(f"Downloaded and read file content: {data[:100]}...")
