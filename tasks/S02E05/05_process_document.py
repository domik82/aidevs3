import json
import os

# Create handler for Llama model
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)

questions = """
01=jakiego owocu użyto podczas pierwszej próby transmisji materii w czasie?
02=Na rynku którego miasta wykonano testową fotografię użytą podczas testu przesyłania multimediów?
03=Co Bomba chciał znaleźć w Grudziądzu?
04=Resztki jakiego dania zostały pozostawione przez Rafała?
05=Od czego pochodzą litery BNW w nazwie nowego modelu językowego?
"""

question_system_prompt = """ 
                        You are specialized assistant in searching information in text.
                        User will ask question and your task is to answer it shortly.
                        
                        Pattern:
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


def convert_questions_to_json(text_content):
    # Initialize an empty list to hold the questions
    questions = []

    # Process the provided text content
    for line in text_content.splitlines():
        # Skip empty lines
        if line.strip():
            # Split the line into question number and question text
            question_number, question_text = line.strip().split("=", 1)
            # Append each question as a dictionary to the list
            questions.append({"number": question_number, "text": question_text})

    # Convert the list of questions to JSON format
    questions_json = json.dumps(questions)

    return questions_json


# Reading the file
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Get paths
base_path = os.getcwd()
# Example usage

file_name = "arxiv.txt"
file_path = os.path.join(base_path, file_name)
text_content = read_file(file_path)
questions_json = json.loads(convert_questions_to_json(text_content))

question_list = ""
for question in questions_json:
    question_list = (
        question_list + f'Question {question["number"]}: {question["text"]}\n'
    )

# print(question_list)

context_file_path = os.path.join(
    base_path, "output", "documents", "centrala_ag3nts_dane_arxiv-draft", "final.md"
)
context = read_file(context_file_path)

llm_handler = ModelHandlerFactory.create_handler(
    # model_name="gpt-3.5-turbo",
    # model_name="llama3.1",
    # model_name="gpt-4o-mini",
    model_name="gpt-4o",
    system_prompt=question_system_prompt,
)

llm_response = llm_handler.ask(
    f"Based on context:{context} Answer questions: \n {questions} "
)
print(llm_response)

response_json = extract_json_from_wrapped_response(llm_response)


with open("response_json", "w", encoding="utf-8") as f:
    json.dump(response_json, f)


llm_response_file = os.path.join(base_path, "response_json")
with open(llm_response_file, "r", encoding="utf-8") as data_file:
    content = data_file.read()
    load_json = json.loads(content)
print(f"\n\nload_json : {load_json}")
