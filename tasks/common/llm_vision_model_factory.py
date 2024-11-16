import os
from typing import Optional

from loguru import logger

from tasks.common.base_vision_model_handler import VisionModelHandler
from tasks.common.llm_vision_openAI_handler import VisionOpenAIHandler


class VisionModelHandlerFactory:
    @staticmethod
    def create_handler(
        model_name: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ) -> VisionModelHandler:
        """
        Factory method to create appropriate model handler based on model name.
        """
        openai_models = [
            "gpt-4o-mini",
            "gpt-4o",
        ]
        llama_models = []

        if model_name in openai_models:
            return VisionOpenAIHandler(
                model_name=model_name,
                system_prompt=system_prompt,
                max_retries=max_retries,
                initial_retry_delay=initial_retry_delay,
            )
        elif model_name in llama_models:
            raise ValueError(f"Unsupported model: {model_name}")
        else:
            raise ValueError(f"Unsupported model: {model_name}")


def main():
    # Example usage
    try:
        # Create handler for OpenAI model
        vision_handler = VisionModelHandlerFactory.create_handler(
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

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
