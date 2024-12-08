import os
import re
from typing import List
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from icecream import ic

from src.common_aidevs.files_read_write_download import (
    download_file,
    get_filename_from_url,
)
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import LlamaModels, LlamaVisionModels, OpenAIVisionModels
from src.video_tools.describe_with_llm import describe_image

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")
API_URL = f"{AI_DEVS_CENTRALA_ADDRESS}/report"
API_KEY = AI_DEVS_CENTRALA_TOKEN

# Default host configuration
DEFAULT_HOST = f"{AI_DEVS_CENTRALA_ADDRESS}/dane/barbara/"


def extract_image_urls(response_text: str) -> List[str]:
    # Try to find complete URLs first
    complete_urls = re.findall(r"https://[\w\./\-]+\.PNG", response_text)
    if complete_urls:
        return complete_urls

    # Try to find base path and image names
    base_path_match = re.search(r"https://[\w\./\-]+/\w+/\w+/", response_text)
    base_path = base_path_match.group(0) if base_path_match else DEFAULT_HOST

    # Find all image names (including those with additional characters like _FGR4)
    image_names = re.findall(r"IMG_\d+(?:_[A-Z0-9]+)?\.PNG", response_text)

    if not image_names:
        return []

    # Combine base path with image names
    return [urljoin(base_path, img_name) for img_name in image_names]


def extract_and_download_images(
    response_text: str, download_dir: str = "downloaded_images"
) -> list[str]:
    result = []
    urls = extract_image_urls(response_text)
    base_path = os.getcwd()
    if not urls:
        print("No image URLs found in the response")
        return []

    os.makedirs(download_dir, exist_ok=True)

    for url in urls:
        ic(f"Attempting to download: {url}")
        success = download_file(url=url, path=download_dir, retries=3, timeout=10)
        if success:
            file_name = get_filename_from_url(url)
            print(f"Successfully downloaded: {file_name}")
            file_path = os.path.join(base_path, download_dir, file_name)
            result.append(file_path)
        else:
            print(f"Failed to download {url} after all retries")

    return result


def get_photo_details(query):
    payload = {"task": "photos", "apikey": API_KEY, "answer": query}
    response = requests.post(API_URL, json=payload)
    return response.json()


def sample1():
    response = {
        "code": 0,
        "message": "Słuchaj! mam dla Ciebie fotki o które prosiłeś. IMG_559.PNG, IMG_1410.PNG, IMG_1443.PNG, IMG_1444.PNG. "
        "Wszystkie siedzą sobie tutaj: https://centrala.ag3nts.org/dane/barbara/. "
        "Pamiętaj, że zawsze mogę poprawić je dla Ciebie (polecenia: REPAIR/DARKEN/BRIGHTEN).",
    }
    extract_and_download_images(response["message"])


def sample2():
    response = {
        "code": 0,
        "message": "No kogo ja widzę! Numer piąty!. Oto fotki, które udało nam się zdobyć. "
        "https://centrala.ag3nts.org/dane/barbara/IMG_559.PNG "
        "https://centrala.ag3nts.org/dane/barbara/IMG_1410.PNG "
        "https://centrala.ag3nts.org/dane/barbara/IMG_1443.PNG "
        "https://centrala.ag3nts.org/dane/barbara/IMG_1444.PNG. "
        "Pamiętaj, że zawsze mogę poprawić je dla Ciebie (polecenia: REPAIR/DARKEN/BRIGHTEN).",
    }

    # Execute the function
    extract_and_download_images(response["message"])


def sample3():
    response = {
        "code": 0,
        "message": "Się robi! Czekaj... czekaj... o! Usunąłem uszkodzenia. Proszę: IMG_559_FGR4.PNG",
    }
    # Execute the function
    extract_and_download_images(response["message"])


def describe_and_pick_tool(images_path, img_file):
    context = (
        "There should be visible women on the image but might be malformed due to corruption - there are options to fix it. "
        "Please describe picture and propose what SINGLE TOOL should be used out of below LIST:"
        "REPAIR, DARKEN, BRIGHTEN"
        "that should be used to describe better what is on the image."
        "Finish description with action like:"
        " <action>action-name</action>"
        "Example1:"
        "Description: The image is very bright there is visible hand and hair but it's impossible to determine fully what is on the picture"
        "<action>DARKEN</action>"
        "Example2:"
        "Description: The image is corrupted and impossible to determine what is on the picture"
        "<action>REPAIR</action>"
        "Example3:"
        "Description: The image is very dark it's visible that there are two people on the picture but details are unavailable"
        "<action>BRIGHTEN</action>"
        "Example4:"
        "Description: The image is showing ancient city with visible details of the landscape, no people are visible on the picture. No action is needed to improve picture."
        "<action>NONE</action>"
    )
    described = describe_image(
        img_file,
        prefix="with_context",
        additional_context=context,
        output_dir=images_path,
        overwrite=False,
        model_name=LlamaVisionModels.LLAMA3_2_VISION_11B_INSTRUCT_Q8_0.value,
        # model_name = OpenAIVisionModels.GPT_4O_MINI.value
        # model_name = OpenAIVisionModels.GPT_4O.value
    )
    return described


def describe_barbara_images(images_path, img_file):
    context = (
        "Your task is to describe a fictional character from movie. "
        "There should be visible women on the image prepare her very detailed description."
        "We are interested in her face and other details that are typical for any human. "
        "We are not interested in any scene details."
        "Describe hair colour, color of the eyes, any tattos, glasses, etc"
        'If image doesn\'t contain interesting information about that woman it just return "No Woman no cry"'
    )
    described = describe_image(
        img_file,
        prefix="with_context",
        additional_context=context,
        output_dir=images_path,
        overwrite=True,
        # model_name=LlamaVisionModels.LLAMA3_2_VISION_11B_INSTRUCT_Q8_0.value
        # model_name = OpenAIVisionModels.GPT_4O_MINI.value
        model_name=OpenAIVisionModels.GPT_4O.value,
    )
    return described


def return_tool_based_on_description(described):
    question_system_prompt = (
        "Your task is to categorize tool that should be used to fix an image."
        "Propose what SINGLE TOOL should be used out of below LIST:"
        "REPAIR, DARKEN, BRIGHTEN"
        "Think about given description, respond with action."
        " <action>action-name</action>"
        "Example1:"
        "Description: The image is very bright there is visible hand and hair but it's impossible to determine fully what is on the picture"
        "<action>DARKEN</action>"
        "Example2:"
        "Description: The image is corrupted and impossible to determine what is on the picture"
        "<action>REPAIR</action>"
        "Example3:"
        "Description: The image is very dark it's visible that there are two people on the picture but details are unavailable"
        "<action>BRIGHTEN</action>"
        "Example4:"
        "Description: The image is showing ancient city with visible details of the landscape, no people are visible on the picture. No action is needed to improve picture."
        "<action>NONE</action>"
    )
    llm_handler = ModelHandlerFactory.create_handler(
        # model_name=OpenAIModels.GPT_35_TURBO.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        model_name=LlamaModels.GEMMA2_9B_INSTRUCT.value,
        # model_name=OpenAIModels.GPT_4o_MINI.value,
        # model_name=OpenAIModels.GPT_4o.value,
        system_prompt=question_system_prompt,
    )
    llm_response = llm_handler.ask(
        f"Based on context:{described} Answer what is on the picture"
    )
    return llm_response


def describe_barbara(described):
    question_system_prompt = (
        "Your task is to figure out description of fictional woman named Barbara"
        "You will be given list of description of images"
        "Find commonality between them and provide as a response"
        "Describe hair colour, color of the eyes, any tattos, glasses, etc"
        "Provide final description in Polish"
    )
    llm_handler = ModelHandlerFactory.create_handler(
        # model_name=OpenAIModels.GPT_35_TURBO.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        model_name=LlamaModels.GEMMA2_9B_INSTRUCT.value,
        # model_name=OpenAIModels.GPT_4o_MINI.value,
        # model_name=OpenAIModels.GPT_4o.value,
        system_prompt=question_system_prompt,
    )
    llm_response = llm_handler.ask(
        f"Based on context:{described} Answer how Barbara looks like"
    )
    return llm_response


def main():
    # sample1()
    # sample2()
    # sample3()
    response = get_photo_details("START")
    extract_and_download_images(response["message"])
    response = get_photo_details("BRIGHTEN IMG_1444.PNG")
    # Execute the function
    # print(response)

    base_path = os.getcwd()

    images_path = os.path.join(base_path, "downloaded_images")
    for image_file in os.listdir(images_path):
        # image_file = 'IMG_559_FGR4.PNG'
        # image_file = 'IMG_1410.PNG'
        # image_file = 'IMG_1443.PNG'
        # image_file = 'IMG_1444.PNG'
        img_file = os.path.join(images_path, image_file)
        described = describe_and_pick_tool(images_path, img_file)
        llm_response = return_tool_based_on_description(described)
        print(llm_response)


if __name__ == "__main__":
    main()
