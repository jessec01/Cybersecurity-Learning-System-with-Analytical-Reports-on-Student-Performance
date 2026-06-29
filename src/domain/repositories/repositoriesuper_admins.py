# pyrefly: ignore [missing-import]
from abc import ABC, abstractmethod
# pyrefly: ignore [missing-import]
from typing import List
# pyrefly: ignore [missing-import]
from domain.entities.super_admins import SuperAdmins

class RepositorieSuperAdmin(ABC):
    @abstractmethod
    def save(self, super_admin: SuperAdmins) -> None:
        pass
    @abstractmethod
    def update(self, super_admin: SuperAdmins) -> None:
        pass
    @abstractmethod
    def delete(self, super_admin: SuperAdmins) -> None:
        pass
    @abstractmethod
    def get_by_id(self, super_admin: SuperAdmins) -> SuperAdmins:
        pass
    @abstractmethod
    def get_all(self) -> List[SuperAdmins]:
        pass