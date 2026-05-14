from fastapi import FastAPI
from presentation.urls import router as urls
from infrastructure.server.lifespan import lifespan


def settings_server() -> FastAPI:
    app = FastAPI(
        title="Cybersecurity Learning System with Analytical Reports on Student Performance",
        description="Sistema de aprendizaje de ciberseguridad con informes analíticos sobre el rendimiento de los estudiantes",
        version="1.0.0",
        lifespan=lifespan
    )
    app.include_router(urls)
    return app

