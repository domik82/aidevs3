import os

from loguru import logger

from src.common_aidevs.files_read_write_download import (
    read_txt_file,
    save_file,
    build_filename,
)
from src.common_llm.factory.llm_vision_model_factory import VisionModelHandlerFactory
from src.common_llm.llm_enums import LlamaVisionModels
from src.tools.perform_ocr import ImageOCR


def ocr_image(
    filepath="",
    output_dir="",
    prefix="",
    suffix="ocr",
    overwrite_ocr=False,
    use_llm=True,
    overwrite_llm=False,
):
    print(f"Reading the image file: {filepath}")

    save_format = "txt"
    # Get filename with extension
    filename = os.path.basename(filepath)
    # Get filename without extension
    filename_no_ext = os.path.splitext(os.path.basename(filename))[0]
    pure_ocr = os.path.join(
        output_dir,
        f"{build_filename(filename_no_ext, prefix, 'pure_ocr')}.{save_format}",
    )

    if os.path.exists(pure_ocr):
        if overwrite_ocr:
            os.remove(pure_ocr)
            ocr_processor = ImageOCR(filepath, language="pl", use_gpu=True)
            ocr_processor.process_and_save_formatted(output_filename=pure_ocr)
        else:
            if not use_llm:
                return read_txt_file(pure_ocr)

    output_file = os.path.join(
        output_dir, f"{build_filename(filename_no_ext, prefix, suffix)}.{save_format}"
    )
    if use_llm:
        if os.path.exists(output_file):
            if overwrite_llm:
                os.remove(output_file)
            else:
                return read_txt_file(output_file)
        # Create handler for OpenAI model
        ocr_text = read_txt_file(pure_ocr)
        vision_handler = VisionModelHandlerFactory.create_handler(
            # model_name=LlamaVisionModels.LLAVA_13B.value, # don't use it
            # model_name=LlamaVisionModels.LLAVA_34B.value, # same wasn't able to recognize text
            model_name=LlamaVisionModels.MINICPM.value,
            system_prompt="You are an expert in image analysis.",
        )
        logger.info(f"Analyzing image: {filepath}")
        question = f"""Please do OCR on the image. 
                    Image contains polish text. 
                    I was able to read it partially please correct any mistakes. 
                    Here is my text: {ocr_text}
                    Return text ONLY
                    """

        result = vision_handler.ask(
            # question="Please do OCR of the image. It contains polish text, make sure you properly read it",
            question=question,
            images=[filepath],
        )
    else:
        result = read_txt_file(pure_ocr)

    print("\nImage Analysis Results:")

    save_file(result, output_file)

    print(f"{result}")
    return result
