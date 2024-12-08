from typing import Optional

from src.common_llm.handlers.base_model_handler import BaseModelHandler
from src.common_llm.handlers.llm_llama_handler import LlamaHandler
from src.common_llm.handlers.llm_openAI_handler import OpenAIHandler
from src.common_llm.llm_enums import OpenAIModels, LlamaModels


class ModelHandlerFactory:
    @staticmethod
    def create_handler(
        model_name: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        temperature: float = 0.7,
    ) -> BaseModelHandler:
        """
        Factory method to create appropriate model handler based on model name.
        """

        try:
            if any(model_name == model.value for model in OpenAIModels):
                return OpenAIHandler(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    initial_retry_delay=initial_retry_delay,
                    temperature=temperature,
                )
            elif any(model_name == model.value for model in LlamaModels):
                return LlamaHandler(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    initial_retry_delay=initial_retry_delay,
                    temperature=temperature,
                )
            else:
                raise ValueError(f"Unsupported model: {model_name}")
        except ValueError as e:
            raise ValueError(f"Invalid model name: {str(e)}")


def main():
    # Example usage
    try:
        # Create handler for OpenAI model
        openai_handler = ModelHandlerFactory.create_handler(
            model_name=OpenAIModels.GPT_35_TURBO.value,
            system_prompt="You are a helpful AI assistant.",
        )

        # Create handler for Llama model
        llama_handler = ModelHandlerFactory.create_handler(
            model_name=LlamaModels.LLAMA3_1.value,
            system_prompt="You are a helpful AI assistant.",
        )

        # Use handlers
        openai_response = openai_handler.ask("What is Python? 3 sentences")
        print(f"OpenAI Response: {openai_response}")

        llama_response = llama_handler.ask("What is Java? 3 sentences")
        print(f"Llama Response: {llama_response}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
