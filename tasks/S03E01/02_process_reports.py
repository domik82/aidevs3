import json
import os

from icecream import ic


from src.common_aidevs.files_read_write_download import (
    save_file,
    read_txt_file,
    build_filename,
)
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)


def process_files_in_folder(folder_path, context):
    # output_path = os.path.join(folder_path, "")
    # Initialize dictionary with empty lists for each category
    result_data = {}
    question_result = ""
    for filename in os.listdir(folder_path):
        # Skip files containing "transcribe" or "ocr"
        if "transcribe" in filename or "ocr" in filename or "facts" in filename:
            continue

        file_path = os.path.join(folder_path, filename)
        # Process file based on type and get classification
        if filename.endswith(".txt"):
            text = read_txt_file(file_path)
            question_result = ask_question(
                text=text, filename=file_path, data_context=context
            )

        # Extract classification results
        json_object = extract_json_from_wrapped_response(question_result)
        result_data.update(json_object)

    return json.dumps(result_data, indent=2)


def ask_question(text: str = "", filename: str = "", data_context: str = ""):
    print(f"Question about the text file: {filename}")
    filename = os.path.basename(filename)
    try:
        print(f"\n\n-------------\nAnalysing text:\n\n {text}")

        metadata_system_prompt = (
            f"""
        1. Your task is to prepare metadata (tags) for provided data in json format. The **context*  is enclosed in `<context></context>` tags. 
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
            "Expected output:\n"
            '{"filename processed" : "metadata sample one, metadata sample two, metadata sample three, ..."}\n'
            "Sample input:\n"
            "<document_name>grocery_list.txt</document_name>\n"
            "<document_content>On drive to home please buy eggs, apples, oranges. Remember about it.</document_content>\n"
            "Sample output:\n"
            '{"grocery_list.txt" : "grocery, list, eggs, apples, oranges, memory, drive, home"}\n'
            """\n### Example Input:
        <context>Jan Nowak pracował jako nauczyciel języka polskiego, przez wiele lat prowadząc zajęcia w Szkole Podstawowej nr 9 w Kielcach.
        Ma 50 lat.His hobby is Scala and JavaScript programming.</context>
        \n
        <document_name>report_01_09_2024_sector_D.txt</document_name>
        <document_content>Jan Nowak został zatrzymany przez policję.</document_content>\n
        
        \n### Example Output:
        {'report_01_09_2024.txt' : 'Jan Nowak, nauczyciel, Kielce, szkoła podstawowa, policja, zatrzymanie, Scala, JavaScript, sektor D'}
        """
            f"""<context>
        {data_context}
        </context>
        """
        )
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


def main():
    try:
        # Get paths
        base_path = os.getcwd()
        print(base_path)

        combined_facts_file = os.path.join(base_path, "combined_facts.txt")
        if os.path.isfile(combined_facts_file):
            with open(combined_facts_file, "r", encoding="utf-8") as infile:
                content = infile.read()

        reports_folder = os.path.join(base_path, "pliki_z_fabryki")
        final_result = process_files_in_folder(reports_folder, content)

        final_result_file = os.path.join(
            base_path, f"{build_filename('final_result_file', '', 'llm')}.json"
        )
        save_file(final_result, final_result_file)
        print("\n------------------------------------\nFinal result:\n", final_result)

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
