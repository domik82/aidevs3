from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
import os

base_path = os.getcwd()
images_path = os.path.join(base_path, "lab_data")
verify = os.path.join(images_path, "verify.txt")


def read_file_lines(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]


def validate_data(data):
    question_system_prompt = "Classify data"
    llm_handler = ModelHandlerFactory.create_handler(
        model_name=OpenAIModels.GPT_4o_MINI_FT_s04e02.value,
        system_prompt=question_system_prompt,
    )
    llm_response = llm_handler.ask(data)
    return llm_response


def process_dataset():
    # Read data from files
    correct_data = read_file_lines(verify)
    # Prepare verification data
    valid_data = []
    for line in correct_data:
        split_result = line.split("=")
        # Access first part (before =)
        left_side = split_result[0]  # returns '01'

        # Access second part (after =)
        right_side = split_result[1]
        response = validate_data(right_side)
        if response == "1":
            valid_data.append(left_side)

    return valid_data


# print(process_dataset())
