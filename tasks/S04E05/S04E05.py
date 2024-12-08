import json
import os
from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler
from src.common_aidevs.files_read_write_download import read_txt_file

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    try:
        task_name = "notes"
        base_path = os.getcwd()
        response_file = os.path.join(base_path, "response_json.json")
        result = read_txt_file(response_file)
        result_json = json.loads(result)

        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, result_json)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
