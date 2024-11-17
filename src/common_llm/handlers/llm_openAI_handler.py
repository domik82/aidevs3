import os
from time import sleep
from typing import List, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger

from src.common_llm.handlers.base_model_handler import BaseModelHandler

load_dotenv()


class OpenAIHandler(BaseModelHandler):
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
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
        """Make request to OpenAI with exponential backoff retry logic."""
        retry_delay = self.initial_retry_delay

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise RuntimeError(
                        f"Failed to get OpenAI response after {self.max_retries} attempts: {e}"
                    )

    def ask(self, question: str, clear_history: bool = False) -> str:
        """
        Ask a question and get a response from OpenAI.

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
    # Initialize with API key and system prompt
    handler = OpenAIHandler(
        model_name="gpt-3.5-turbo",
        system_prompt="You are a helpful AI assistant specialized in Python programming.",
    )

    # Example usage
    try:
        # Ask a question
        response = handler.ask("What is a Python decorator?")
        print(f"Response: {response}")

        # Ask follow-up with context
        response = handler.ask("Can you show an example?")
        print(f"Follow-up response: {response}")

        # Clear conversation and ask new question
        handler.clear_conversation()
        response = handler.ask("Explain Python generators", clear_history=True)
        print(f"New topic response: {response}")

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    main()
