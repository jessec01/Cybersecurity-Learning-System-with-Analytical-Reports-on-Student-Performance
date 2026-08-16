# pyrefly: ignore [missing-import]
from backend.application.dto.register_admin_input import RegisterAdminDTOInput
from backend.domain.value_objects.users import UsersValidate
from backend.domain.value_objects.persons import PersonsValidate
class RegisterAdminUseCase:
    def __init__(self):
        pass 
    def execute(self,data:RegisterAdminDTOInput):
        try:
            user_validate=UsersValidate(
                username=data.username,
                password=data.password,
            )
            person_validate=PersonsValidate(
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone
                mail=data.mail,
                
            )
        except Exception as e:
            raise ValueError(f"Error al validar los datos: {str(e)}")
            


        
        