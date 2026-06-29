# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from domain.errors.auth_errors import UnauthorizedError, ForbiddenError


def _unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc) or "No autorizado"})


def _forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc) or "Permiso denegado"})


def register_auth_errors(app: FastAPI):
    """Registra los handlers de errores de auth en FastAPI sin acoplar el server al dominio."""
    app.add_exception_handler(UnauthorizedError, _unauthorized_handler)
    app.add_exception_handler(ForbiddenError, _forbidden_handler)
