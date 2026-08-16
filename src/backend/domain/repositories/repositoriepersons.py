# pyrefly: ignore [missing-import]
from abc import ABC, abstractmethod
# pyrefly: ignore [missing-import]
from typing import List
# pyrefly: ignore [missing-import]
from backend.domain.entities.persons import Person

class RepositoriePerson(ABC):
    @abstractmethod
    def save(self, person: Person) -> None:
        pass
    @abstractmethod
    def update(self, person: Person) -> None:
        pass
    @abstractmethod
    def delete(self, person: Person) -> None:
        pass
    @abstractmethod
    def get_by_id(self, person_id: int) -> Person | None:
        pass
    @abstractmethod
    def get_all(self) -> List[Person]:
        pass
