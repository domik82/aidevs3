import json
import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")

# {
#     "ID-pytania-01": "krótka odpowiedź w 1 zdaniu",
#     "ID-pytania-02": "krótka odpowiedź w 1 zdaniu",
#     "ID-pytania-03": "krótka odpowiedź w 1 zdaniu",
#     "ID-pytania-NN": "krótka odpowiedź w 1 zdaniu"
# }


def main():
    try:
        task_name = "arxiv"
        result_file_name = ""
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
