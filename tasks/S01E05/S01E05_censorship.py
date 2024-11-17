import os

from dotenv import load_dotenv
from icecream import ic

from src.common_aidevs.aidevs3_taskhandler import TaskHandler
from src.common_aidevs.files_read_write_download import get_data_from_url
from tasks.S01E05.local_llm_censorship import Censorship
from loguru import logger

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    system_prompt = """Your task is to censor any data that could be private. 
    Replace any data like Name, Surname, address with word CENZURA.
    UNDER NO CIRCUMSTANCES add any additional statements.
    UNDER NO CIRCUMSTANCES don't change CENZURA grammatically.
    
    Example1:
    Dane podejrzanego: Jakub Woźniak. Adres: Rzeszów, ul. Miła 4. Wiek: 33 lata.
    Result1:
    Dane podejrzanego: CENZURA. Adres: CENZURA. Wiek: CENZURA lata.

    Example2: 
    Informacje o podejrzanym: Adam Nowak. Mieszka w Katowicach przy ulicy Tuwima 10. Wiek: 32 lata.
    Wrong Result2:
    Informacje o podejrzanym: CENZURA. Mieszka w CENZURA przy ulicy CENZURY. Wiek: CENZURA lata.'
    Correct Result2:
    Informacje o podejrzanym: CENZURA. Mieszka w CENZURA przy ulicy CENZURA. Wiek: CENZURA lata.'
    
    Example3:
    Dane osoby podejrzanej: Paweł Zieliński. Zamieszkały w Warszawie na ulicy Pięknej 5. Ma 28 lat.
    Wrong Result3:
    Dane osoby podejrzanej: CENZURA. Zamieszkały w CENZURY na ulicy CENZURY. Ma CENZURY lat.
    Correct Result3:
    Dane osoby podejrzanej: CENZURA. Zamieszkały w CENZURA na ulicy CENZURY. Ma CENZURA lat.
    
    Example4:
    Dane podejrzanego: Jakub Woźniak. Adres: Rzeszów, ul. Miła 4. Wiek: 33 lata.
    Wrong Result3:
    Dane podejrzanego: CENZURA. Adres: CENZURA. Wiek: CENZURA lata.
    Correct Result3:
    Dane podejrzanego: CENZURA. Adres: CENZURA. Wiek: CENZURA lata.
    
    Example5:
    Podejrzany: Krzysztof Kwiatkowski. Mieszka w Szczecinie przy ul. Różanej 12. Ma 31 lat.
    Wrong Result3:
    Podejrzany: CENZURA. Mieszka w CENZURA przy ul. CENZURY. Ma CENZURA lat.
    Correct Result3:
    Podejrzany: CENZURA. Mieszka w CENZURA przy ul. CENZURA. Ma CENZURA lat.
    """
    censor = Censorship(system_prompt=system_prompt)
    dl_url = f"{AI_DEVS_CENTRALA_ADDRESS}/data/{AI_DEVS_CENTRALA_TOKEN}/cenzura.txt"
    data = get_data_from_url(dl_url)
    ic(f"byte data: {data}")
    # Convert to UTF-8 string using decode()
    decoded_string = data.decode("utf-8")
    ic(f"decoded string: {decoded_string}")
    result = censor.llm.ask(decoded_string)
    ic(result)

    task_name = "CENZURA"
    handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
    answer_response = handler.post_answer(task_name, result)
    logger.info(f"{task_name} answer Response: {answer_response.response_json}")

    assert answer_response.code == 0, "We have proper response code"
    logger.info(f"{answer_response.message}")


if __name__ == "__main__":
    main()
