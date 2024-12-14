import asyncio
import json
import os

from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)
from tasks.S04E03.b_mardown_crawlee_simplified import SpecializedWebCrawler


def response_to_question(current_link, context, question, visited_links):
    question_system_prompt = """ 
        Your task is to search the provided document and answer question that user asked.
        If you can't answer based on provided context then suggest next link in document where the answer might be.
        
        User will provide you:
        CURRENT LINK: currently visited link 
        CONTENT: Content of the current HTML site converted to Markdown format
        QUESTION: <|question|>  
        VISITED LINKS: A list of links that were checked already.
        
        Respond in json format
        {
        "action": "answer" | "search" | "none"
        "answer": "Answer to question" | "next search link" | "none"
        }
        
        """
    llm_handler = ModelHandlerFactory.create_handler(
        # model_name=OpenAIModels.GPT_35_TURBO.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        # model_name=LlamaModels.GEMMA2_9B_INSTRUCT.value,
        model_name=OpenAIModels.GPT_4o_MINI.value,
        # model_name=OpenAIModels.GPT_4o.value,
        system_prompt=question_system_prompt,
    )
    llm_response = llm_handler.ask(
        f"CURRENT LINK: {current_link}, CONTENT:{context}, QUESTION: {question}, VISITED LINKS: {visited_links}"
    )
    return llm_response


def handle_llm_response(answer_json, url, available_links, visited_links):
    """Handle the JSON response from LLM"""
    if not answer_json or "action" not in answer_json:
        return None, url, visited_links

    action = answer_json.get("action")
    answer = answer_json.get("answer", "")

    if action == "answer":
        return answer, url, visited_links
    elif action == "search":
        # If LLM suggests searching a new link
        new_url = answer
        if answer.startswith("/"):
            # Handle relative URLs by finding matching link in available_links
            matching_link = next(
                (link for link in available_links if link.endswith(answer)), None
            )
            new_url = matching_link if matching_link else url + answer.lstrip("/")

        if new_url not in visited_links:
            return "", new_url, visited_links

    return None, url, visited_links


async def main():
    base_path = os.getcwd()
    questions_file = os.path.join(base_path, "softo.json")

    with open(questions_file, "r", encoding="utf-8") as data_file:
        content = data_file.read()
        questions = json.loads(content)

    answers = {}
    for key, question in questions.items():
        base_url = "https://softo.ag3nts.org"
        final_answer = ""
        visited_links = set()

        while not final_answer and len(visited_links) < 10:
            visited_links.add(base_url)

            try:
                crawler = SpecializedWebCrawler(max_depth=0, save_to_disk=False)
                results = await crawler.run(base_url, extract_content=True)

                if not results:
                    break

                content = results[0].content
                current_link = results[0].url
                available_links = results[0].links

                llm_response = response_to_question(
                    current_link, content, question, list(visited_links)
                )
                answer_json = extract_json_from_wrapped_response(llm_response)

                final_answer, new_url, visited_links = handle_llm_response(
                    answer_json, base_url, available_links, visited_links
                )

                base_url = new_url  # Update URL for next iteration if needed

            except Exception as e:
                print(f"Error processing question {key}: {str(e)}")
                break

        answers[key] = final_answer or "Could not find an answer"

    return answers


if __name__ == "__main__":
    answers = asyncio.run(main())
    print(json.dumps(answers, indent=2))
