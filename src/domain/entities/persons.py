# pyrefly: ignore [missing-import]
from datetime import datetime
from datetime import date
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
# pyrefly: ignore [missing-import]
from pydantic_extra_types.phone_numbers import PhoneNumber

class Person(BaseModel):
    id_person: int | None = None
    first_name: str
    last_name: str
    mail: EmailStr
    phone: PhoneNumber | None = None
    date_of_birth: date | None = None
    id_users: int | None = None
    def extraction_full_name(self)->str:
        """retorna el nombre completo de la persona"""
        return f"{self.first_name} {self.last_name}"
    def see_full_information(self):
        print(f"Nombre completo: {self.first_name} {self.last_name}") 
        print(f"Correo electronico: {self.mail}") 
        print(f"Numero de telefono: {self.phone}") 
        print(f"Fecha de nacimiento: {self.date_of_birth}")
    def date_of_birth_valid(self)->bool:
        """valida si la fecha de nacimiento es valida"""
        if self.date_of_birth >= date.today():
            return False
        return True 