import json
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from loguru import logger
from sympy import sympify
from sympy.core.sympify import SympifyError

from tasks.common.llm_handler import LLMHandler

load_dotenv()
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def validate_and_update_data(
    data: Dict[str, Any], llm_handler: LLMHandler
) -> Dict[str, Any]:
    """
    Validates and updates test data according to specified rules:
    - Ensures 'answer' fields are integers
    - Validates arithmetic operations in questions
    - Updates test questions using LLM
    """
    for item in data["test-data"]:
        # Validate arithmetic questions
        if "answer" in item:
            try:
                # Convert answer to integer if needed
                if not isinstance(item["answer"], int):
                    item["answer"] = int(item["answer"])

                # Validate arithmetic operation
                question = item["question"]
                expected_answer = int(solve_math_operation(question))

                if item["answer"] != expected_answer:
                    logger.warning(
                        f"Correcting answer for {question} from {item['answer']} to {expected_answer}"
                    )
                    item["answer"] = expected_answer

            except (ValueError, TypeError) as e:
                logger.error(
                    f"Error processing answer for question '{item['question']}': {e}"
                )

        # Handle test questions using LLM
        if "test" in item:
            try:
                question = item["test"]["q"]
                logger.info(f"Processing test question: {question}")
                llm_answer = llm_handler.execute_question(question)
                item["test"]["a"] = llm_answer
            except Exception as e:
                logger.error(f"Error processing LLM question: {e}")
                item["test"]["a"] = "Error: Could not process question"

    return data


def update_api_key(json_data: dict, new_api_key: str) -> dict:
    """Updates the API key in the JSON data."""
    json_data["apikey"] = new_api_key
    return json_data


def solve_math_operation(question: str) -> Optional[int]:
    try:
        expression = sympify(question)
        result = expression.evalf()
        return result
    except SympifyError:
        return None


def main():
    # Initialize LLM handler
    llm = LLMHandler()

    # Read JSON data
    with open("sample.json", "r") as f:
        data = json.load(f)

    # Update API key
    updated_data = update_api_key(data, AI_DEVS_CENTRALA_TOKEN)

    # Validate and update data
    validated_data = validate_and_update_data(updated_data, llm)

    # Save updated data
    with open("validated_sample.json", "w") as f:
        json.dump(validated_data, f, indent=2)


if __name__ == "__main__":
    main()


# grabbed idea from https://github.com/Janoz94/AI_Devs3/blob/main/task_s1e3.py to use sympy
