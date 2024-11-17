from abc import ABC, abstractmethod


class BaseModelHandler(ABC):
    @abstractmethod
    def ask(self, question: str, clear_history: bool = False) -> str:
        pass

    @abstractmethod
    def clear_conversation(self) -> None:
        pass

    @abstractmethod
    def set_system_prompt(self, system_prompt: str) -> None:
        pass
