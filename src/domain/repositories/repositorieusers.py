# pyrefly: ignore [missing-import]
from domain.entities.users import Users
from abc import ABC, abstractmethod
# pyrefly: ignore [missing-import]
from typing import List

class RepositeorieUser(ABC):
    @abstractmethod
    def save(self,user: Users) ->None:
        pass
    @abstractmethod
    def update(self,user: Users) ->None:
        pass
    @abstractmethod
    def delete(self,user: Users) ->None:
        pass
    @abstractmethod
    def get_by_id(self, user_id: int) -> Users:
        pass
    @abstractmethod
    def get_all(self) ->List[Users]:
        pass 
