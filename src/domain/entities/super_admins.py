# pyrefly: ignore [missing-import]
from pydantic import BaseModel
import uuid


class SuperAdmins(BaseModel):
    id_super_admin: int | None = None
    id_person: int
    is_active: bool = True
    secret_key: str

    def verify_secret_key(self, secret_key: str) -> bool:
        return self.secret_key == secret_key

    @staticmethod
    def generate_secret_key() -> str:
        return str(uuid.uuid4())