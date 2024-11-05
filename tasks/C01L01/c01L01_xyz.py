import asyncio
import re
import sys

import requests

from tasks.C01L01.crawlee_ag3nts_sample import return_extracted_data
from tasks.C01L01.local_llama_ask_question import execute_question


async def main():
    page_adress = "https://xyz.ag3nts.org/"
    question = await return_extracted_data(page_adress)

    model = "llama3.1"  # You can change this to the specific Llama model you have
    user_question = f"Answer shortly - {question}"
    response = execute_question(model, user_question)
    print(f"\nResponse: {response}")

    username = "tester"
    password = "574e112a"

    form_values = {"username": username, "password": password, "answer": response}
    try:
        result_raw = requests.post(page_adress, data=form_values)
    except Exception as error:
        print(f"Error sending the answer: {error}")
        sys.exit(1)
    result_text = result_raw.content.decode("utf8")
    print("\nThe result page is:\n")
    print(result_text)
    flag = re.findall("{{FLG:(.*?)}}", result_text)
    if flag:
        print(f"\n\nZnaleziono flagę: {flag[0]}")


if __name__ == "__main__":
    asyncio.run(main())
