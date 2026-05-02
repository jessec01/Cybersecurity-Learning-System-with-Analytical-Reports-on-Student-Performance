from fastapi import FastAPI
from presentation.urls import router as urls
# Inicializamos la aplicación
# aqui se maneja la logica de arranque de la aplicacion
def settings_server()->FastAPI:
    #aqui se crea la instancia de FastAPI
    app = FastAPI(
        title="Cybersecurity Learning System with Analytical Reports on Student Performance",
        description="Sistema de aprendizaje de ciberseguridad con informes analíticos sobre el rendimiento de los estudiantes",
        version="1.0.0"
    )
    app.include_router(urls)
    return app

