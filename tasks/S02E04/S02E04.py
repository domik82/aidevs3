import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from common.aidevs3_taskhandler import TaskHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")

# {
#   "people": ["plik1.txt", "plik2.mp3", "plikN.png"],
#   "hardware": ["plik4.txt", "plik5.png", "plik6.mp3"],
# }

task = """Zadanie: Zdobyliśmy dostęp do danych z fabryki, którą nam wskazałeś. Są to raporty dzienne kilku działających tam oddziałów. Część z nich to zwykłe raporty techniczne, a część to raporty związane z bezpieczeństwem. Pozyskane dane są w różnych formatach i nie wszystkie zawierają użyteczne dane. Wydobądź dla nas proszę tylko notatki zawierające informacje o schwytanych ludziach lub o śladach ich obecności oraz o naprawionych usterkach hardwarowych (pomiń te związane z softem oraz pomiń katalog z faktami). Raport wyślij do zadania “kategorie” w formie jak poniżej. Pliki powinny być posortowane alfabetycznie."""


def main():
    try:
        task_name = "kategorie"
        result = {
            "people": ["plik1.txt", "plik2.mp3", "plikN.png"],
            "hardware": ["plik4.txt", "plik5.png", "plik6.mp3"],
        }

        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, result)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
