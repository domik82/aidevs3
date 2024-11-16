import os
from typing import Optional, List, Dict
import base64

from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger

from tasks.common.base_vision_model_handler import VisionModelHandler

load_dotenv()


class VisionOpenAIHandler(VisionModelHandler):
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        self.client = OpenAI()
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

    def _prepare_image_content(self, image_source: str) -> Dict:
        """Prepare image content for API request."""
        if image_source.startswith(("http://", "https://")):
            return {"type": "image_url", "image_url": {"url": image_source}}
        else:
            base64_image = self._encode_image(image_source)
            return {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            }

    def ask(
        self,
        question: str,
        clear_history: bool = False,
        images: Optional[List[str]] = None,
        max_response_tokens: Optional[int] = 300,
    ) -> str:
        """
        Ask a question, supporting both regular text and image analysis queries.

        Args:
            question: The question to ask
            clear_history: Whether to clear conversation history after this question
            images: Optional list of image paths or URLs to analyze
            max_response_tokens: Optional maximum number of tokens in the response (default: 300)
        """
        try:
            if images:
                # Prepare content with images
                content = [{"type": "text", "text": question}]
                for image_source in images:
                    content.append(self._prepare_image_content(image_source))
            else:
                # Regular text question
                content = question

            messages = self.conversation_history + [
                {"role": "user", "content": content}
            ]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=max_response_tokens
            )

            result = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": content})
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
        vision_handler = VisionOpenAIHandler(
            model_name="gpt-4o-mini",
            system_prompt="You are an expert in image analysis.",
        )

        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        sample1_path = os.path.join(base_path, "resources", "sample1.png")
        logger.info(f"Analyzing image: {sample1_path}")

        result = vision_handler.ask(
            question="What objects can you see in this image? Please describe in detail.",
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


if __name__ == "__main__":
    main()
