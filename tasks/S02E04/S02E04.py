import json
import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


# The process files executes 99% of things locally. I'm able to do OCR , OCR using LLM and I'm using whisper
# to convert audio to file.
# The process wasn't tested with openAI or anything like that (potentially should).
# once the files are generated there is option to simply leave them and reuse
# The OCR process causes majority of errors
# I wasn't able to do the task using llama.


def main():
    try:
        task_name = "kategorie"
        result_file_name = "final_result_file_llm.json"
        base_path = os.getcwd()
        result_file = os.path.join(base_path, result_file_name)
        with open(result_file, "r") as f:
            file_contents = f.read()
        result = json.loads(file_contents)

        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, result)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
