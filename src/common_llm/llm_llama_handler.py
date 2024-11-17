from time import sleep
from typing import List, Dict, Optional
import ollama
from loguru import logger

from src.common_llm.base_model_handler import BaseModelHandler


class LlamaHandler(BaseModelHandler):
    def __init__(
        self,
        model_name: str = "llama3.1",
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        self.model = model_name
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.conversation_history = []

        if system_prompt:
            self.set_system_prompt(system_prompt)

    def set_system_prompt(self, system_prompt: str) -> None:
        """Set or update the system prompt for the conversation."""
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        logger.info("System prompt set successfully")

    def _make_request(self, messages: List[Dict[str, str]]) -> str:
        """Make request to LLM with exponential backoff retry logic."""
        retry_delay = self.initial_retry_delay

        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(model=self.model, messages=messages)
                return response["message"]["content"].strip()
            except ollama.ResponseError as e:
                logger.error(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise RuntimeError(
                        f"Failed to get LLM response after {self.max_retries} attempts: {e}"
                    )

    def ask(self, question: str, clear_history: bool = False) -> str:
        """
        Ask a question and get a response from the LLM.

        Args:
            question: The question to ask
            clear_history: Whether to clear conversation history after this question
        """
        logger.info(f"Querying {self.model} for question: {question}")

        # Add user question to conversation history
        self.conversation_history.append({"role": "user", "content": question})

        # Get response
        response = self._make_request(self.conversation_history)

        # Add assistant's response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        # Clear history if requested
        if clear_history:
            self.conversation_history = self.conversation_history[
                :1
            ]  # Keep system prompt

        return response

    def clear_conversation(self) -> None:
        """Clear the conversation history while preserving system prompt."""
        system_prompt = (
            self.conversation_history[0] if self.conversation_history else None
        )
        self.conversation_history = [system_prompt] if system_prompt else []
        logger.info("Conversation history cleared")


def main():
    # Initialize with a system prompt
    llm = LlamaHandler(
        model_name="llama3.1",
        system_prompt="You are a helpful AI assistant specialized in Python programming.",
    )

    # Ask questions
    response1 = llm.ask("What is a Python decorator?")
    print(response1)

    # Ask follow-up question (maintains context)
    response2 = llm.ask("Can you show an example?")
    print(response2)

    # Clear conversation history
    llm.clear_conversation()

    # Or ask a question and clear history afterward
    response3 = llm.ask("What is Python GIL?", clear_history=True)
    print(response3)

    # Change system prompt
    llm.set_system_prompt("You are now a data science expert.")


if __name__ == "__main__":
    main()
