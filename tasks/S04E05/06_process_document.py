import json
import os

from src.common_aidevs.files_read_write_download import read_file

# Create handler for Llama model
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)


question_system_prompt = """ 
                        You are specialized assistant in searching information in text and acting as detective assistant.
                        Your owner will ask question and your task is to answer it shortly.
                        Include all facts given in the text, in particular references to events.
                        Try to think about abstract information the document contain and connect the dots.  
                        Make sure you are using information also from images since this is a notepad it might be clue what author was thinking about. 
                         
                        Known facts: 
                        - Rafał przeniósł się do roku w którym wydany został GPT-2.
                        - Podana bezpośrednio konkretna data nie musi być tą o którą chodzi. Zwróć uwagę na określenia typu 'jutro' - należy wtedy wyznaczyć datę na podstawie podanej bezpośrednio daty.
                        - Na jednym z obrazów była jaskinia
                        
                        Think step by step about question, user is not hearing you so do it out load embed that info int <thinking></thinking> tags                
                        
                        <forbidden responses>
                        Rafał przeniósł się do 2024 roku
                        Rafał przeniósł się do nieokreślonego roku
                        Rafał znalazł schronienie w miejscu blisko miasta, w którym spędził ostatnie lata, ale nie podał jego nazwy
                        </forbidden responses>
                        
                        Response pattern:
                        {
                        "question-id": "response"
                        }
                        
                        Expected result:
                        {
                        "01": "krótka odpowiedź w 1 zdaniu",
                        "02": "krótka odpowiedź w 1 zdaniu",
                        "03": "krótka odpowiedź w 1 zdaniu",
                        "NN": "krótka odpowiedź w 1 zdaniu"
                        }
                        
                        """


def process_single_question(question_number, question_text, context, llm_handler):
    prompt = f"""Based on context: {context}
    Please answer this specific question: {question_text}"""

    llm_response = llm_handler.ask(prompt)
    json_response = extract_json_from_wrapped_response(llm_response)
    return {question_number: json_response.get(question_number, "")}


def main():
    base_path = os.getcwd()
    final_md_path = os.path.join(base_path, "output", "fixed_output.md")
    questions_file = os.path.join(base_path, "notes.json")

    # Read files
    questions_txt = read_file(questions_file)
    questions_json = json.loads(questions_txt)
    context = read_file(final_md_path)

    # Create LLM handler once
    llm_handler = ModelHandlerFactory.create_handler(
        # model_name=LlamaModels.GEMMA2_9B_INSTRUCT.value,
        # model_name=OpenAIModels.GPT_35_TURBO.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        # model_name=OpenAIModels.GPT_4o_MINI.value,
        model_name=OpenAIModels.GPT_4o.value,
        system_prompt=question_system_prompt,
    )

    # Process questions and collect responses
    all_responses = {}
    for question_number, question_text in questions_json.items():
        response = process_single_question(
            question_number, question_text, context, llm_handler
        )
        all_responses.update(response)
        print(
            f"Processed question {question_number} question_text: {question_text} response: {response} "
        )

    # Save final response
    response_file = "response_json.json"
    with open(response_file, "w", encoding="utf-8") as f:
        json.dump(all_responses, f, ensure_ascii=False, indent=4)

    # Verify saved response
    with open(response_file, "r", encoding="utf-8") as f:
        loaded_responses = json.load(f)
        print(f"\nFinal responses: {loaded_responses}")


if __name__ == "__main__":
    main()
