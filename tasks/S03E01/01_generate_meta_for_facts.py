import os

from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels


def combine_files_in_folder(folder_path: str, output_file: str) -> None:
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")

    # Dictionary to store folder contents
    # folder_contents: Dict[str, List[tuple[str, str]]] = {}

    # Read all files and organize by folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read()
                if "entry deleted" in content:
                    continue

    # Write organized content to output file
    # with open(output_file, 'w', encoding="utf-8" ) as outfile:
    # save_file(final_result, final_result_file)


def ask_question(text: str = "", filename: str = "", data_context: str = ""):
    print(f"Question about the text file: {filename}")
    filename = os.path.basename(filename)
    try:
        print(f"\n\n-------------\nAnalysing text:\n\n {text}")

        metadata_system_prompt = """
        1. Your task is to prepare metadata (tags) for provided data in json format. The **context* is enclosed in `<context></context>` tags. 
        2. Think step-by-step about the content to make sure you have all the information.
        3. If the context mentions about technology or programming, include it as a keyword (e.g., "JavaScript", "Python")
        4. If the input mentions about animals, include it as a keyword. (e.g., "zwierzę", "zwierzyna leśna").
        5. Generate keywords in the **Polish language**, ensuring they are in the **nominative case** 
        (e.g., "sportowiec", not "sportowcem" or "sportowców"). 
        6. If the context mentions a profession or job title (even if is retired), include it as a keyword (e.g., "nauczyciel", "inżynier").
        7. The **user input**, will have <document_name></document_name> and <document_content></document_content> tags.
        8. Metadata should facilitate the headquarters in searching for these reports using their own technologies.
        9. Focus on the given report and generate a response by providing 15 keywords, separated by commas.

        Make good use of the context to create highly precise keywords. 
        For example, if a person mentioned in the facts is discussed, use the information from the facts to create accurate keywords. 
        When proper names or surnames appear, key information about these people or things (found in the facts) should be included in the keywords.

        Return JSON data ONLY!

        """
        print(f"\n{metadata_system_prompt}\n\n")
        # Create handler for Llama model
        llm_handler = ModelHandlerFactory.create_handler(
            # model_name=LlamaModels.GEMMA2_27B_INSTRUCT_Q4.value,
            model_name=OpenAIModels.GPT_4o_MINI.value,
            # model_name=OpenAIModels.GPT_4o.value,
            system_prompt=metadata_system_prompt,
        )

        question = (
            f"What should be document tags?, document: "
            f"<document_name>{filename}</document_name> "
            f"<document_content>{text}</document_content>"
        )

        print(f"\n\nquestion: \n {question}")

        llm_response = llm_handler.ask(question)
        print(f"\n\nResponse for file {filename}: {llm_response}")
        return llm_response

    except Exception as e:
        print(f"Error: {str(e)}")


def main() -> None:
    try:
        base_path = os.getcwd()
        print(base_path)
        facts_path = os.path.join(base_path, "pliki_z_fabryki/facts")
        output_file = os.path.join(base_path, "combined_facts.txt")

        combine_files_in_folder(facts_path, output_file)
        print("Files have been combined successfully.")
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
