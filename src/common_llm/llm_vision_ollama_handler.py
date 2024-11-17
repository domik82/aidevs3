# llm_vision_ollama_handler.py

import base64
import os
from typing import Optional, List
from loguru import logger
import requests

from src.common_llm.base_vision_model_handler import VisionModelHandler


class VisionOllamaHandler(VisionModelHandler):
    def __init__(
        self,
        model_name: str = "minicpm-v:8b-2.6-q5_K_M",
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        host: str = "http://localhost:11434",
    ):
        self.model = model_name
        self.host = host
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.conversation_history = []

        if system_prompt:
            self.set_system_prompt(system_prompt)

    def set_system_prompt(self, system_prompt: str) -> None:
        """Set or update the system prompt for the conversation."""
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        logger.info("System prompt set successfully")

    def clear_conversation(self) -> None:
        """Clear the conversation history while preserving system prompt."""
        system_prompt = (
            self.conversation_history[0] if self.conversation_history else None
        )
        self.conversation_history = [system_prompt] if system_prompt else []
        logger.info("Conversation history cleared")

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise

    def ask(
        self,
        question: str,
        clear_history: bool = False,
        images: Optional[List[str]] = None,
        max_response_tokens: Optional[int] = None,
    ) -> str:
        """
        Ask a question with image analysis using Ollama API.
        """
        try:
            if not images:
                raise ValueError("At least one image is required for vision analysis")

            # Prepare messages with conversation history
            messages = self.conversation_history.copy()

            # Add images and question
            base64_images = []
            for image_path in images:
                base64_image = self._encode_image(image_path)
                base64_images += [base64_image]

            user_message = {
                "role": "user",
                "content": f"{question}",
                "images": base64_images,
            }

            messages.append(user_message)

            # Make request to Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    **(
                        {"max_tokens": max_response_tokens}
                        if max_response_tokens
                        else {}
                    ),
                },
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")

            result = response.json()["message"]["content"]

            # Update conversation history
            self.conversation_history.append(user_message)
            self.conversation_history.append({"role": "assistant", "content": result})

            if clear_history:
                self.clear_conversation()

            return result

        except Exception as e:
            logger.error(f"Error in processing query: {str(e)}")
            raise


def main():
    try:
        # Initialize the vision handler
        vision_handler = VisionOllamaHandler(
            model_name="minicpm-v:8b-2.6-q5_K_M",
            system_prompt="You are an expert in image analysis.",
        )

        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        sample1_path = os.path.join(base_path, "resources", "sample1.png")
        logger.info(f"Analyzing image: {sample1_path}")

        result = vision_handler.ask(
            question="What do you see in this image? Please describe shortly",
            images=[sample1_path],
        )
        print("\nImage Analysis Results:")
        print(f"{result}")

        # Multiple image analysis
        sample2_path = os.path.join(base_path, "resources", "sample2.png")
        logger.info(f"Analyzing multiple images: {sample1_path}, {sample2_path}")

        multi_result = vision_handler.ask(
            question="Compare these two images and describe their differences.",
            images=[sample1_path, sample2_path],
            clear_history=True,
        )
        print("\nMultiple Image Analysis Results:")
        print(f"{multi_result}")

    except FileNotFoundError as e:
        logger.error(f"Image file not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")


def simple_test_vision_model():
    try:
        # Create a simple test image
        from PIL import Image

        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        # Create a test image with some basic shapes

        img = Image.new("RGB", (100, 100), color="white")
        test_image_path = "test_image.png"
        sample_path = os.path.join(base_path, "resources", test_image_path)
        img.save(sample_path)

        # Initialize the vision handler
        vision_handler = VisionOllamaHandler(
            # model_name="llava:13b",
            model_name="minicpm-v:8b-2.6-q5_K_M",
            system_prompt="You are an expert in image analysis.",
        )

        # Test the model
        result = vision_handler.ask(
            question="What do you see in this image?",
            images=[sample_path],
        )
        print(f"Test result: {result}")

        # Clean up
        os.remove(sample_path)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    main()
    # simple_test_vision_model()
