import re


class UsersValidate:
    def __init__(self, username: str, password: str):
        self.username = self._check_username(username)
        self.password = self._check_password(password)

    @staticmethod
    def _check_username(username: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]{3,16}$", username):
            raise ValueError("Username invalido")
        return username

    @staticmethod
    def _check_password(password: str) -> str:
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            raise ValueError("Password invalido")
        return password
    
    
    