from enum import Enum


class OpenAIModels(Enum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4o_MINI = "gpt-4o-mini"
    GPT_4o = "gpt-4o"
    GPT_4o_MINI_FT_s04e02 = "ft:gpt-4o-mini-2024-07-18:personal:s04e02:Abx1M8QC"


class LlamaModels(Enum):
    LLAMA2 = "llama2"
    LLAMA3_1 = "llama3.1"
    LLAMA3_2_1b = "llama3.2:1b"
    LLAMA3_2_3b = "llama3.2:3b"
    CODELLAMA = "codellama"
    DEEPSEEK_CODER_V2 = "deepseek-coder-v2:16b"
    STARCODER2_7B = "starcoder2:7b"
    QWEN2_5_14B = "qwen2.5:14b"
    GEMMA2_9B_INSTRUCT = "gemma2:9b-instruct-q5_K_M"
    BIELIK_11B = "hf.co/speakleash/Bielik-11B-v2.2-Instruct-GGUF-IQ-Imatrix:Q5_K_M"
    CODESTRAL_22B = "codestral:22b-v0.1-q4_K_M"
    MISTRAL_7B_INSTRUCT = "mistral:7b-instruct-q5_K_M"
    GEMMA2_27B = "gemma2:27b"
    GEMMA2_27B_INSTRUCT_Q4 = "gemma2:27b-instruct-q4_K_M"


class LlamaVisionModels(Enum):
    LLAVA = "llava"
    BAKLLAVA = "bakllava"
    MINICPM = "minicpm-v:8b-2.6-q5_K_M"
    LLAVA_13B = "llava:13b"
    LLAVA_34B = "llava:34b"
    LLAMA3_2_VISION_11B = "llama3.2-vision:11b"
    LLAMA3_2_VISION_11B_INSTRUCT_Q8_0 = "llama3.2-vision:11b-instruct-q8_0"


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
