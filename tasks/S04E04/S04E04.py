import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")
AI_DEVS_AZYL_ADDRESS = os.getenv("AI_DEVS_AZYL_ADDRESS")


def main():
    try:
        task_name = "webhook"

        result = f"https://{AI_DEVS_AZYL_ADDRESS}/drone_location"

        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, result)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()

# Jeśli masz aktywne konto na Azylu,
# możesz też użyć SSH do przekierowania swojego lokalnego portu (na przykładzie = 3000)
# na swój port na Azylu (na przykladzie = 50005).
# Robi się to komendą wydaną na lokalnym komputerze w ten sposób:
# ssh -R 50005:localhost:3000 agent10005@azyl.ag3nts.org -p 5022

# or use putty plink
# plink -ssh -R 50005:localhost:3000 -P 5022 -l agent10005 -pw passs azyl......org
