from icecream import ic

from src.common_llm.llm_llama_handler import LlamaHandler


class Censorship:
    def __init__(self, model_name: str = "llama3.1", system_prompt: str = ""):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.llm = LlamaHandler(self.model_name, self.system_prompt)

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
        self.llm.set_system_prompt(self.system_prompt)

    def censor(self, text_to_censor):
        response = self.llm.ask(text_to_censor)
        ic(response)


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
    
    """
    censor = Censorship(system_prompt=system_prompt)
    result = censor.llm.ask(
        "Tożsamość osoby podejrzanej: Piotr Lewandowski. Zamieszkały w Łodzi przy ul. Wspólnej 22. Ma 34 lata."
    )
    ic(result)
    assert (
        result
        == "Tożsamość osoby podejrzanej: CENZURA. Zamieszkały w CENZURA przy ul. CENZURA. Ma CENZURA lata."
    )


if __name__ == "__main__":
    main()
