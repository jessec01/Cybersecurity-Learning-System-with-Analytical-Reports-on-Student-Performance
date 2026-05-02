from fastapi import FastAPI
from infrastructure.server.setting import settings_server

def create_application()->FastAPI:
    """
    Función que crea e inicializa la aplicación FastAPI.
    Incluye routers, middlewares y configuraciones necesarias antes de arrancar.
    """
    apps:FastAPI = settings_server()
    return apps