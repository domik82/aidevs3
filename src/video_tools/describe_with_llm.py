import os

from icecream import ic
from loguru import logger

from src.common_aidevs.files_read_write_download import (
    save_file,
    build_filename,
)
from src.common_llm.factory.llm_vision_model_factory import VisionModelHandlerFactory
from src.tools.find_project_root import find_project_root


def describe_image(
    filepath="",
    output_dir="",
    prefix="",
    suffix="",
    overwrite=False,
    additional_context="",
    model_name="minicpm-v:8b-2.6-q5_K_M",
):
    print(f"Reading the image file: {filepath}")

    save_format = "txt"
    # Get filename with extension
    filename = os.path.basename(filepath)
    # Get filename without extension
    filename_no_ext = os.path.splitext(os.path.basename(filename))[0]

    output_file = os.path.join(
        output_dir, f"{build_filename(filename_no_ext, prefix, suffix)}.{save_format}"
    )
    if os.path.exists(output_file):
        if overwrite:
            os.remove(output_file)
        else:
            print(f"File {output_file} already exists. \n Skipping..")
            return

    vision_handler = VisionModelHandlerFactory.create_handler(
        # model_name="llava:13b", # don't use it
        # model_name="llava:34b", # same wasn't able to recognize text
        # model_name="minicpm-v:8b-2.6-q5_K_M",
        model_name=model_name,
        system_prompt="You are an expert in image analysis.",
    )
    logger.info(f"Analyzing image: {filepath}")

    question = """
                Please describe what you see on the image. 
                Respond in English only.
                """

    if additional_context != "":
        question = f"{question}. Take into consideration additional context about picture {additional_context}."

    result = vision_handler.ask(
        # question="Please do OCR of the image. It contains polish text, make sure you properly read it",
        question=question,
        images=[filepath],
    )

    print("\nImage Analysis Results")
    print(f"{result}")
    save_file(result, output_file)

    return result


def main():
    try:
        # Get paths

        # Single image analysis
        sample_file = "sample1.png"

        resources_path = os.path.join(find_project_root(__file__), "resources")
        output_path = os.path.join(find_project_root(__file__), "output")

        resources_file = os.path.join(resources_path, sample_file)
        describe_image(resources_file, output_dir=output_path)
        context = "It was middle of the day when cyber attack was happening."
        describe_image(
            resources_file,
            prefix="with_context",
            additional_context=context,
            output_dir=output_path,
        )

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
