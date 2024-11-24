import os
from typing import Optional

from loguru import logger

from src.common_llm.handlers.vision.base_vision_model_handler import VisionModelHandler
from src.common_llm.handlers.vision.llm_vision_ollama_handler import VisionOllamaHandler
from src.common_llm.handlers.vision.llm_vision_openAI_handler import VisionOpenAIHandler
from src.common_llm.llm_enums import LlamaVisionModels, OpenAIVisionModels
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
        try:
            if any(model_name == model.value for model in OpenAIVisionModels):
                return VisionOpenAIHandler(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    initial_retry_delay=initial_retry_delay,
                )
            elif any(model_name == model.value for model in LlamaVisionModels):
                return VisionOllamaHandler(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    initial_retry_delay=initial_retry_delay,
                )
            else:
                raise ValueError(f"Unsupported model: {model_name}")
        except ValueError as e:
            raise ValueError(f"Invalid model name: {str(e)}")


def simple_sample_openai():
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
            model_name=OpenAIVisionModels.GPT_4O_MINI.value,
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


def simple_sample_ollama():
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
            # model_name=LlamaVisionModels.LLAVA_13B.value,
            model_name=LlamaVisionModels.LLAVA_34B.value,
            # model_name=LlamaVisionModels.MINICPM.value,
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


def main():
    # simple_sample_openai()
    simple_sample_ollama()


if __name__ == "__main__":
    main()
