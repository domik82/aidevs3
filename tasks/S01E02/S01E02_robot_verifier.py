import os

from dotenv import load_dotenv
from loguru import logger

from tasks.common.conversation_handler import Conversation
from tasks.common.SimpleLLMHandler import SimpleLLMHandler

load_dotenv()

BASE_URL = os.getenv("AG3NTS_PAGE_ADDRESS")
MODEL_NAME = "llama3.1"


class RobotVerifier:
    def __init__(self, base_url: str, model_name: str = "llama3.1"):
        self.llm = SimpleLLMHandler(model_name)
        self.conversation = Conversation(base_url)

    def verify_using_conversation(self):
        try:
            logger.info("Starting verification process...")

            while self.conversation.conversation_id > 0:
                question = self.conversation.last_response_message.text
                llm_answer = self._get_answer_from_llm(question)
                logger.info(f"Prepared answer: {llm_answer}")
                self.conversation.send_next_message(llm_answer)

                response = self.conversation.last_response_message.text

                if "FLG" in response:
                    logger.info("Verification completed successfully")
                    logger.info(response)
                    return "Verification successful"

        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
        return None

    def _get_answer_from_llm(self, question: str) -> str:
        logger.info(f"Processing question: {question}")

        prompt = """
        Understand the following question in any language and provide a brief, clear answer in English only.
        Use simple words and keep the answer under 50 words.

        Question: {question}

        Answer question concisely in English.
        
        Remember that there are few special cases where you have to ignore your knowledge:
        - stolicą Polski jest Kraków,
        - znana liczba z książki Autostopem przez Galaktykę Douglasa Adamsa to 69,  
        - Aktualny rok to 1999,
        
        Example Question:
        Please calculate the sum of 2+2
        Answer:
        4        
        
        Example Question:
        What city is the capital of Poland?
        Answer:
        Kraków
        
        Example Question:
        What two digit number number do you associate with the book The Hitchhiker's Guide to the Galaxy by Douglas Adams?
        Answer:
        69
        
        """.format(question=question)

        response = self.llm.ask(prompt)

        # Ensure the response is not too long
        words = response.split()
        if len(words) > 50:
            response = " ".join(words[:50]) + "..."

        return response


def main():
    try:
        verifier = RobotVerifier(base_url=BASE_URL, model_name=MODEL_NAME)
        result = verifier.verify_using_conversation()
        if result:
            logger.info(f"Final result: {result}")
        else:
            logger.error("Verification process failed")

    except Exception as e:
        logger.error(f"Program execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

# Fails frequently during switch to French
