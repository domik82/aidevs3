import json
from typing import Any

import requests

from src.common_aidevs.aidevs3_responsehandler import ResponseBaseHandler

from src.common_aidevs.constants import AI_DEVS_SERVER, AI_DEVS_USER_TOKEN
from loguru import logger

logger.add("default_{time}.log", diagnose=True)


class TaskHandler:
    def __init__(
        self, base_url: str = AI_DEVS_SERVER, user_api_key: str = AI_DEVS_USER_TOKEN
    ):
        self.base_url: str = base_url
        self.user_api_key: str = user_api_key
        self.log = logger
        self._last_response = None

    def post_answer(self, task_name, answer: Any, as_data=False) -> ResponseBaseHandler:
        self.log.info(f"Task Name: {task_name}")
        if self.base_url is not None and self.user_api_key is not None:
            answer_request = {
                "task": task_name,
                "apikey": self.user_api_key,
                "answer": answer,
            }
            self.log.info(f"task_answer: {json.dumps(answer_request)}")

            if as_data:
                response = requests.post(f"{self.base_url}/verify", data=answer_request)
            else:
                response = requests.post(f"{self.base_url}/verify", json=answer_request)
            self._last_response = response
            if response.status_code == 200:
                self.log.info(f"post_answer response: {response.json()}")
                return ResponseBaseHandler(response.json())
            else:
                raise Exception(
                    f"Failed to post answer. Status code: {response.status_code}, body: {response.json()}"
                )
        else:
            raise RuntimeError("Base url or user token doesn't exist")
