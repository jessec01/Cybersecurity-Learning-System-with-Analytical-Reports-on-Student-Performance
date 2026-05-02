from fastapi import APIRouter
router = APIRouter()
# Creamos nuestra primera ruta (el endpoint de inicio)
@router.get("/")
def read_root():
    return {"mensaje": "¡Hola Mundo! El servidor de FastAPI está vivo y funcionando 🚀"}