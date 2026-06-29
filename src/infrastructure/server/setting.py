from fastapi import FastAPI
from presentation.urls import router as urls
from infrastructure.server.lifespan import lifespan
from infrastructure.errors.auth import register_auth_errors


def settings_server() -> FastAPI:
    app = FastAPI(
        title="Cybersecurity Learning System with Analytical Reports on Student Performance",
        description="Sistema de aprendizaje de ciberseguridad con informes analiticos sobre el rendimiento de los estudiantes",
        version="1.0.0",
        lifespan=lifespan
    )
    app.include_router(urls)
    register_auth_errors(app)
    return app

