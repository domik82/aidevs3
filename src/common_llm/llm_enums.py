from enum import Enum


class OpenAIModels(Enum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4o_MINI = "gpt-4o-mini"
    GPT_4o = "gpt-4o"


class LlamaModels(Enum):
    LLAMA2 = "llama2"
    LLAMA3_1 = "llama3.1"
    CODELLAMA = "codellama"
    DEEPSEEK_CODER_V2 = "deepseek-coder-v2:16b"
    STARCODER2_7B = "starcoder2:7b"
    LLAMA3_2 = "llama3.2"
    QWEN2_5_14B = "qwen2.5:14b"
    GEMMA2_9B_INSTRUCT = "gemma2:9b-instruct-q5_K_M"
    BIELIK_11B = "hf.co/speakleash/Bielik-11B-v2.2-Instruct-GGUF-IQ-Imatrix:Q5_K_M"
    CODESTRAL_22B = "codestral:22b-v0.1-q4_K_M"


class LlamaVisionModels(Enum):
    LLAVA = "llava"
    BAKLLAVA = "bakllava"
    MINICPM = "minicpm-v:8b-2.6-q5_K_M"
    LLAVA_13B = "llava:13b"
    LLAVA_34B = "llava:34b"


class OpenAIVisionModels(Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


def main() -> None:
    # Example usage
    print(OpenAIModels.GPT_4.value)  # Prints: gpt-4
    print(LlamaModels.LLAMA2.value)  # Prints: llama2

    # List all models
    print(list(OpenAIModels))
    print(list(LlamaModels))
    print(list(LlamaVisionModels))


if __name__ == "__main__":
    main()
