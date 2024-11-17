import json
import os

from icecream import ic

from src.audio_tools.convert_mp3_using_whisper import convert_mp3_to_txt
from src.common_aidevs.files_read_write_download import (
    save_file,
    read_txt_file,
    build_filename,
)
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)
from src.video_tools.use_ocr_with_llm import ocr_image


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
