import json
import os

from dotenv import load_dotenv
from pathlib import Path

from loguru import logger

from common.aidevs3_taskhandler import TaskHandler
from common.files_read_write_download import download_file, get_filename_from_url
from tasks.S01E03.fix_json_data import update_api_key, validate_test_data
from tasks.common.llm_handler import LLMHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def check_file_exists(filename: str) -> bool:
    """
    Check if file exists in current directory using multiple methods.
    Returns True if file exists, False otherwise.
    """
    # Method 1: Using pathlib (modern approach)
    file_path = Path(filename)
    return file_path.is_file()


def main():
    dl_url = f"{AI_DEVS_CENTRALA_ADDRESS}/data/{AI_DEVS_CENTRALA_TOKEN}/json.txt"

    filename = get_filename_from_url(dl_url)
    if not check_file_exists(filename):
        success: bool = download_file(dl_url, retries=5, timeout=10)
        logger.info(f"Download status {success}")

    # Initialize LLM handler
    llm = LLMHandler()

    # Read JSON data
    with open(filename, "r") as f:
        data = json.load(f)

    # Update API key
    updated_data = update_api_key(data, AI_DEVS_CENTRALA_TOKEN)

    # Validate and update data
    validated_data = validate_test_data(updated_data, llm)

    # Save updated data
    with open(filename, "w") as f:
        json.dump(validated_data, f, indent=2)

    # report_link = f"{AI_DEVS_CENTRALA_ADDRESS}/report"

    task_name = "JSON"
    handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
    answer_response = handler.post_answer(task_name, validated_data)

    logger.info(f"{task_name} answer Response: {answer_response.response_json}")

    assert answer_response.code == 0, "We have proper response code"
    logger.info(f"{answer_response.message}")


if __name__ == "__main__":
    main()
