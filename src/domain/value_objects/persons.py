import re
import phonenumbers


class PersonsValidate:
    def __init__(self, first_name: str, last_name: str, phone: str, email: str):
        self.first_name = self._check_first_name(first_name)
        self.last_name = self._check_last_name(last_name)
        self.phone = self._check_phone(phone) if phone else None
        self.email = self._check_email(email)

    @staticmethod
    def _check_first_name(first_name: str) -> str:
        if not re.match(r"^[a-zA-Z]{2,50}$", first_name):
            raise ValueError("Nombre invalido")
        return first_name

    @staticmethod
    def _check_last_name(last_name: str) -> str:
        if not re.match(r"^[a-zA-Z]{2,50}$", last_name):
            raise ValueError("Apellido invalido")
        return last_name

    @staticmethod
    def _check_phone(phone: str) -> str:
        try:
            parsed = phonenumbers.parse(phone, None)
        except phonenumbers.NumberParseException:
            raise ValueError(f"Telefono invalido: '{phone}'. Use formato internacional (+51999888777)")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"Numero de telefono no valido: '{phone}'")
        return phone

    @staticmethod
    def _check_email(email: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Email invalido")
        return email
