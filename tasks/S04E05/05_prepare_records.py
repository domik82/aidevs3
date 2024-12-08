import json
import os

from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
from src.markdown_tools.split_markdown_by_paragraph import split_by_headers
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)


def fix_paragraphs(described):
    question_system_prompt = (
        "Your task is to review the provided text that was extracted from a corrupted document"
        "Based on context please fix the wording and formatting."
        "Please remove any random letter or words that doesn't improve content of the document"
        "Remove also any image descriptions that doesn't make document more meaningful"
        "If there are any indications of pages make sure you will leave that information"
        "The document was in markdown format. Make sure that fixed text follows same format"
        "Example text to remove: It's just the blank background ready for writing."
        "Second example of text removal: 'ple doj), emyzi'"
        "Think carefully while doing the document analysis. Store it in 'thinking' part "
        "The final answer should be json with below structure"
        "{"
        "   'thinking': 'document represents a description of an image of car, I can remove any random text or tags. "
        "I will leave name of paragraph. For some reason it seems that same image was described multiple times. "
        "I wil leave only one description that captures the essence of the document'"
        "   'answer': 'Paragraph1. The image represent a very popular Ford Fiesta car that was common in the 1980s.'"
        "}"
        "DON'T REMOVE ANY IMPORTANT DATA"
        "Don't add any content that wasn't present in the original document"
    )
    llm_handler = ModelHandlerFactory.create_handler(
        # model_name=OpenAIModels.GPT_35_TURBO.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        # model_name=LlamaModels.GEMMA2_9B_INSTRUCT.value,
        model_name=OpenAIModels.GPT_4o_MINI.value,
        # model_name=OpenAIModels.GPT_4o.value,
        system_prompt=question_system_prompt,
    )
    llm_response = llm_handler.ask(
        f"Based on context:{described} Please fix the document in best way possible."
    )
    return llm_response


def main():
    base_path = os.getcwd()
    output_folder = os.path.join(base_path, "output")
    output_path = os.path.join(output_folder)
    final_md_file_path = os.path.join(output_path, "final.md")

    # Read the original markdown file
    with open(final_md_file_path, "r", encoding="utf-8") as file:
        md_content = file.read()

    sections = split_by_headers(md_content)

    # Store both original responses and processed data
    fixed_sections = []
    original_responses = []

    for section in sections:
        print(section)
        llm_response = fix_paragraphs(section)
        print(f"llm_response: \n\n {llm_response}")

        # Store original LLM response
        original_responses.append(llm_response)

        # Extract JSON from response
        json_data = extract_json_from_wrapped_response(llm_response)
        fixed_sections.append(json_data)

    # Save original LLM responses
    with open("original_responses.txt", "w", encoding="utf-8") as file:
        for response in original_responses:
            file.write(f"{response}\n{'=' * 50}\n")

    # Save thinking/answer pairs
    with open("thinking_answer_pairs.json", "w", encoding="utf-8") as file:
        json.dump(fixed_sections, file, indent=4, ensure_ascii=False)

    # Create markdown file from answer sections
    with open("fixed_output.md", "w", encoding="utf-8") as file:
        for section in fixed_sections:
            if isinstance(section, dict) and "answer" in section:
                file.write(f"{section['answer']}\n\n")


if __name__ == "__main__":
    main()
