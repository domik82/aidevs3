from typing import Optional

from src.common_llm.handlers.base_model_handler import BaseModelHandler
from src.common_llm.handlers.llm_llama_handler import LlamaHandler
from src.common_llm.handlers.llm_openAI_handler import OpenAIHandler


class ModelHandlerFactory:
    @staticmethod
    def create_handler(
        model_name: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ) -> BaseModelHandler:
        """
        Factory method to create appropriate model handler based on model name.
        """
        openai_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o-mini",
            "gpt-4o",
        ]
        llama_models = [
            "llama2",
            "llama3.1",
            "codellama",
            "deepseek-coder-v2:16b",
            "starcoder2:7b",
            "llama3.2",
            "qwen2.5:14b",
            "gemma2:9b-instruct-q5_K_M",
            "hf.co/speakleash/Bielik-11B-v2.2-Instruct-GGUF-IQ-Imatrix:Q5_K_M",
            "codestral:22b-v0.1-q4_K_M",
        ]

        if model_name in openai_models:
            return OpenAIHandler(
                model_name=model_name,
                system_prompt=system_prompt,
                max_retries=max_retries,
                initial_retry_delay=initial_retry_delay,
            )
        elif model_name in llama_models:
            return LlamaHandler(
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
        # Create handler for OpenAI model
        openai_handler = ModelHandlerFactory.create_handler(
            model_name="gpt-3.5-turbo", system_prompt="You are a helpful AI assistant."
        )

        # Create handler for Llama model
        llama_handler = ModelHandlerFactory.create_handler(
            model_name="llama3.1", system_prompt="You are a helpful AI assistant."
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
