from abc import ABC, abstractmethod
from typing import Optional, List


class VisionModelHandler(ABC):
    @abstractmethod
    def ask(
        self,
        question: str,
        clear_history: bool = False,
        images: Optional[List[str]] = None,
        max_response_tokens: Optional[int] = None,
    ) -> str:
        pass

    @abstractmethod
    def clear_conversation(self) -> None:
        pass

    @abstractmethod
    def set_system_prompt(self, system_prompt: str) -> None:
        pass
