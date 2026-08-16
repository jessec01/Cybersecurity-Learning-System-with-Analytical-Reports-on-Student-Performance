class RegisterAdminDTOInput:
    def __init__(self, username:str,password:str,first_name:str,
                 last_name:str,mail:str,phone:str):
      self.username=username
      self.password=password
      self.first_name=first_name
      self.last_name=last_name
      self.mail=mail
      self.phone=phone
      