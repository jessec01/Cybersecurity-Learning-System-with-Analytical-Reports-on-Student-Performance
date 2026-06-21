from pydantic import BaseModel
from abc import ABC, abstractmethod
class Users(BaseModel):
    username:str
    password:str
    is_email_verified:bool
    is_token_verified:bool
    is_token_reset:bool
    is_token_expired:bool
    is_active:bool   

    def is_user_email_verified(self)->bool:
        """valida si el usuario esta verificado por correo"""
        return self.is_email_verified 
    def is_user_token_verified(self)->bool:
        """valida si el usuario esta verificado por token"""
        return self.is_token_verified
    def is_user_token_reset(self)->bool:
        """valida si el usuario tiene un token de reseteo"""
        return self.is_token_reset
    def is_user_token_expired(self)->bool:
        """valida si el token del usuario ha expirado"""
        return self.is_token_expired
    def is_user_verified(self)->bool:
        """llama los otro metodos que definire para validar si el usuario esta validado""" 
        if self.is_email_verified and self.is_token_verified:
            self.is_active=True
        else:
            self.is_active=False    
    @property
    def is_user_active(self)->bool:
        """valida si el usuario esta activo"""
        return self.is_active
    @property
    def username(self)->str:
        """retorna el nombre de usuario"""
        return self.username
    