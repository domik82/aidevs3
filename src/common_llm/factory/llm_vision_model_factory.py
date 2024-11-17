import os
from typing import Optional

from loguru import logger

from src.common_llm.handlers.vision.base_vision_model_handler import VisionModelHandler
from src.common_llm.handlers.vision.llm_vision_ollama_handler import VisionOllamaHandler
from src.common_llm.handlers.vision.llm_vision_openAI_handler import VisionOpenAIHandler
from src.tools.find_project_root import find_project_root


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
        ollama_models = ["llava", "bakllava", "minicpm-v:8b-2.6-q5_K_M", "llava:13b"]

        if model_name in openai_models:
            return VisionOpenAIHandler(
                model_name=model_name,
                system_prompt=system_prompt,
                max_retries=max_retries,
                initial_retry_delay=initial_retry_delay,
            )
        elif model_name in ollama_models:
            return VisionOllamaHandler(
                model_name=model_name,
                system_prompt=system_prompt,
                max_retries=max_retries,
                initial_retry_delay=initial_retry_delay,
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")


def main():
    # Example usage
    try:
        # Create a simple test image
        from PIL import Image

        # Get paths
        resources_path = os.path.join(find_project_root(__file__), "resources")

        # Single image analysis
        # Create a test image with some basic shapes
        img = Image.new("RGB", (100, 100), color="white")
        test_image_path = "test_image.png"
        sample_path = os.path.join(resources_path, test_image_path)
        img.save(sample_path)

        # Create handler for OpenAI model
        vision_handler = VisionModelHandlerFactory.create_handler(
            model_name="gpt-4o-mini",
            system_prompt="You are an expert in image analysis.",
        )
        logger.info(f"Analyzing image: {sample_path}")

        result = vision_handler.ask(
            question="What objects can you see in this image? Please describe in detail.",
            images=[sample_path],
        )
        print("\nImage Analysis Results:")
        print(f"{result}")

        # Clean up
        os.remove(sample_path)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()