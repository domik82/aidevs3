import os

import requests

from typing import Dict, Optional
from time import sleep

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

BASE_URL = os.getenv("AG3NTS_PAGE_ADRESS")


class Message:
    def __init__(self, text: str, msg_id: str):
        self.text = text
        self.msg_id = msg_id

    def set_msg_context(self, msg_id: str):
        self.msg_id = msg_id

    def set_msg_text(self, text: str):
        self.text = text

    def generate_payload(self) -> Optional[Dict]:
        return {"text": self.text, "msgID": self.msg_id}


class Conversation:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.verify_endpoint = f"{self.base_url}/verify"
        self.conversation_id = "0"
        self.last_sent_message = Message("", self.conversation_id)
        self.last_response_message = Message("", self.conversation_id)
        self.history = []
        # init conversation
        self._initiate_conversation()

    def _initiate_conversation(self):
        logger.debug("Initiate_conversation")
        self.send_next_message("READY")

    def send_next_message(self, text: str):
        self.last_sent_message.text = text
        self.last_sent_message.msg_id = self.conversation_id
        self.history.append(self.last_sent_message.generate_payload())

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                logger.debug(
                    f"Sending payload: {self.last_sent_message.generate_payload()}"
                )
                response = requests.post(
                    self.verify_endpoint,
                    json=self.last_sent_message.generate_payload(),
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    timeout=10,
                )
                logger.debug(f"Response payload: {response.content}")
                resp_data = response.json()
                response_msg_id = resp_data.get("msgID")
                response_text = resp_data.get("text")
                if resp_data.get("msgID") is not None:
                    if self.conversation_id == "0":
                        self.conversation_id = response_msg_id

                self.last_response_message.msg_id = self.conversation_id
                self.last_response_message.text = response_text

                self.history.append(self.last_response_message.generate_payload())

                if response.status_code != 200:
                    if (
                        response.status_code == 400
                        and resp_data.get("message")
                        == "Haha! Gotcha! Guards! We have an intruder here!"
                    ):
                        logger.debug(f"Bot caught us: {response.content}")
                        self.conversation_id = resp_data.get("code")
                        RuntimeError(f"Bot caught us: {response.content}")
                        self.last_response_message.msg_id = self.conversation_id
                        self.last_response_message.text = resp_data.get("message")
                        self.history.append(
                            self.last_response_message.generate_payload()
                        )
                        break
                    else:
                        response.raise_for_status()
                break

            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise RuntimeError(
                        f"Failed to communicate with server after {max_retries} attempts: {e}"
                    )

    def get_history(self):
        return self.history


def main():
    conversation = Conversation(BASE_URL)
    conversation.send_next_message("test")
    for message in conversation.get_history():
        print(f"Message {message['msgID']}: {message['text']}")


if __name__ == "__main__":
    main()
