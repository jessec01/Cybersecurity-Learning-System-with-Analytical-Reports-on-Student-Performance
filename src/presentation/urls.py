from fastapi import APIRouter
from presentation.endpoints.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)


@router.get("/")
def read_root():
    return {"mensaje": "Hola Mundo! El servidor de FastAPI esta vivo y funcionando"}