from abc import ABC,abstractmethod
class RegisterAdminRepository(ABC):
    
    @abstractmethod
    def create_hash(self,password:str)->str:
        pass
    
    @abstractmethod
    def create_user(self,data:dict)->dict:
        pass
    
    @abstractmethod
    def create_person(self,data:dict)->dict:
        pass
    @abstractmethod
    def is_exists_admin(self,secret_key:str)->bool:
        pass
    @abstractmethod
    def is_exist_user(self,phone:str)->bool:
        pass
    @abstractmethod
    def is_exist_person(self,mail:str)->bool:
        pass
    @abstractmethod
    def is_exist_phone(self,phone:str)->bool:
        pass
