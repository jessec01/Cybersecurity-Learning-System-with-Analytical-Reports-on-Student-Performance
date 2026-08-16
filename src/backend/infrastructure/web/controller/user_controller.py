from backend.application.dto.register_admin_input import RegisterAdminDTOInput
from backend.application.use_case.register_admin import RegisterAdminUseCase

class UserController:
   def __init__(self):
      pass 
   
   def register_admin(self,data:dict):
      #sacar la informacion del dict
      dto_input=RegisterAdminDTOInput(
         username=data.get("username"),
         password=data.get("password"),
         first_name=data.get("first_name"),
         last_name=data.get("last_name"),
         mail=data.get("mail"),
         phone=data.get("phone")
      )
      #crea el caso de uso
      dto_output=RegisterAdminUseCase().execute(dto_input)
      return dto_output
      