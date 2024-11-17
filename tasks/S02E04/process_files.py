import json
import os

from icecream import ic
from loguru import logger

from src.common_aidevs.files_read_write_download import (
    save_file,
    read_file,
    read_txt_file,
    build_filename,
)
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.factory.llm_vision_model_factory import VisionModelHandlerFactory
from src.common_llm.handlers.sound.llm_whisper_handler import AudioTranscriber
from src.tools.perform_ocr import ImageOCR


def extract_json_from_wrapped_response(response):
    start = response.index("{")
    end = response.index("}") + 1
    json_str = response[start:end]
    return json.loads(json_str)


def process_files_in_folder(folder_path):
    output_path = os.path.join(folder_path, "")
    # Initialize dictionary with empty lists for each category
    result_data = {
        "people": [],
        "hardware": [],
    }
    classification = {}
    for filename in os.listdir(folder_path):
        # Skip files containing "transcribe" or "ocr"
        if "transcribe" in filename or "ocr" in filename or "facts" in filename:
            continue

        file_path = os.path.join(folder_path, filename)
        # Process file based on type and get classification
        if filename.endswith(".txt"):
            text = read_txt_file(file_path)
            classification = ask_question(file_path, text)
        elif filename.endswith(".mp3"):
            text = convert_mp3_to_txt(
                file_path=file_path, output_dir=output_path, suffix="transcribe"
            )
            classification = ask_question(filename, text)
        elif filename.endswith(".png"):
            text = ocr_image(file_path, output_dir=output_path, suffix="ocr")
            classification = ask_question(filename, text)

        # Extract classification results
        json_object = extract_json_from_wrapped_response(classification)

        # Add file to appropriate category based on True values
        for category in ["people", "hardware"]:
            # Handle both string and boolean values
            value = json_object[category]
            is_true = (isinstance(value, str) and value.lower() == "true") or (
                isinstance(value, bool) and value is True
            )
            if is_true:
                result_data[category].append(filename)
                break

    return json.dumps(result_data, indent=2)


def ask_question(filename, text):
    print(f"Question about the text file: {filename}")
    try:
        print(f"\n\n-------------\nAnalysing text:\n\n {text}")
        # # Create handler for OpenAI model
        # llm_handler = ModelHandlerFactory.create_handler(
        #     model_name="gpt-3.5-turbo",
        #     system_prompt="You are a helpful AI assistant."
        # )

        categorization_system_prompt = """
        You are tasked with processing data reports. The input consists of daily reports from multiple departments, 
        including technical reports and security reports. Not all contain useful information.

        Your task is to:
        1. Extract only notes containing:
           - Information about captured individuals
           - Evidence of human presence
           - Hardware malfunction repairs (exclude software-related issues)
        2. Your task is ONLY to categorize document based on two categories "people", "hardware" and "other". 
        
        Please process the data according to these requirements.
        Respond ONLY with valid JSON. Do not write an introduction or summary.
        
        Result should be in tag <answer> and have below JSON format:
        {
        "people": "value",
        "hardware": "value",
        "other": "value"
        }
        
        Sample input 1:
        "entry deleted"
        
        Sample result:
        {
        "people": "False",
        "hardware": "False",
        "other": "True"
        }
        
        Sample input 2:
        Fingerprint analysis identified subject: Jan Nowak (correlated with birth records database)
        
        Sample result:
        {
        "people": "True",
        "hardware": "False",
        "other": "False"
        }
        
        Sample input 3:
        Repair note: Fingerprint malfunction detected. Scheduled repair: 12/03/2023 15:48:37 
        
        Sample result:
        {
        "people": "False",
        "hardware": "True",
        "other": "False"
        }
        
        Sample input 4:
        Boss, as directed, we searched the tenements in the nearby town for rebels. We were unable to find anyone. Sensor dźwiękowy i detektory ruchu w pełnej gotowości.
        
        Sample result:
        {
        "people": "False",
        "hardware": "False",
        "other": "True"
        }
        
        Sample input 5:
        Wstępny alarm wykrycia – ruch organiczny. Czujniki pozostają aktywne, a wytyczne dotyczące wykrywania życia organicznego – bez rezultatów. Stan patrolu bez zakłóceń.
        
        Sample result:
        {
        "people": "False",
        "hardware": "False",
        "other": "True"
        }
        
        Sample input 6:
        We met a guy named Dominik, he is good with preparing pizza.
        
        Sample result:
        {
        "people": "False",
        "hardware": "False",
        "other": "True"
        }
        Reason: It doesn't talk about person being captured or threat.
        """
        # Create handler for Llama model
        llm_handler = ModelHandlerFactory.create_handler(
            # model_name="gpt-3.5-turbo",
            # model_name="llama3.1",
            model_name="gpt-4o-mini",
            # model_name="gpt-4o",
            system_prompt=categorization_system_prompt,
        )

        llm_response = llm_handler.ask(
            f"What is the document category type?, document: {text} "
        )
        print(f"\n\nResponse for file {filename}: {llm_response}")
        return llm_response

    except Exception as e:
        print(f"Error: {str(e)}")


def convert_mp3_to_txt(
    file_path="", output_dir="", prefix="", suffix="", overwrite=False
):
    print(f"Convert mp3 to txt for: {file_path}")

    save_format = "txt"
    # Get filename with extension
    filename = os.path.basename(file_path)
    # Get filename without extension
    filename_no_ext = os.path.splitext(os.path.basename(filename))[0]
    output_file_pattern = build_filename(filename_no_ext, prefix, suffix)
    if output_dir == "":
        output_dir = os.getcwd()

    # Check if output dir exists and create it otherwise
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get output file path with extension
    save_file_path = os.path.join(output_dir, f"{output_file_pattern}.{save_format}")

    if os.path.exists(save_file_path):
        if overwrite is True:
            os.remove(save_file_path)
        else:
            return read_file(save_file_path)

    # Initialize transcriber with model settings
    transcriber = AudioTranscriber(model_size="large", language="en")

    # Transcribe with file output
    result = transcriber.transcribe_audio(
        audio_path=file_path,
        output_dir=output_dir,
        output_filename=output_file_pattern,
        save_formats=[save_format],
    )

    if result:
        print("\nTranscription:\n", result.text)
        return result.text
    else:
        print("Transcription failed")


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
            # model_name="llava:13b", # don't use it
            # model_name="llava:34b", # same wasn't able to recognize text
            model_name="minicpm-v:8b-2.6-q5_K_M",
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


def main():
    try:
        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        resources_path = os.path.join(base_path, "resources")
        final_result = process_files_in_folder(resources_path)

        final_result_file = os.path.join(
            base_path, f"{build_filename('final_result_file', '', 'llm')}.json"
        )
        save_file(final_result, final_result_file)
        print("\n------------------------------------\nFinal result:\n", final_result)

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
