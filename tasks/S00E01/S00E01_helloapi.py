from loguru import logger
from src.common_aidevs.aidevs3_taskhandler import TaskHandler
from src.common_aidevs.files_read_write_download import get_data_from_url


def hello_api_task():
    try:
        task_name = "POLIGON"
        handler = TaskHandler()
        data_url = "https://poligon.aidevs.pl/dane.txt"
        byte_string_dataset = get_data_from_url(data_url)
        logger.info(byte_string_dataset)
        string_table = byte_string_dataset.decode("utf-8").strip().split("\n")

        answer_response = handler.post_answer(task_name, string_table)
        logger.info(f"hello_api_task answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        assert (
            answer_response.message == "Super. Wszystko OK!"
        ), "We have proper response msg"

    except Exception as e:
        logger.error(f"Exception {e}")


if __name__ == "__main__":
    hello_api_task()
