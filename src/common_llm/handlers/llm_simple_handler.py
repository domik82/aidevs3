from time import sleep

import ollama
from loguru import logger

from src.common_llm.llm_enums import LlamaModels


class SimpleLLMHandler:
    def __init__(self, model_name: str = LlamaModels.LLAMA3_1.value):
        self.model = model_name

    def ask(self, question: str) -> str:
        logger.info(f"Querying {self.model} for question: {question}")
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = ollama.chat(
                    model=self.model, messages=[{"role": "user", "content": question}]
                )
                return response["message"]["content"].strip()
            except ollama.ResponseError as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise RuntimeError(
                        f"Failed to get LLM response after {max_retries} attempts: {e}"
                    )
