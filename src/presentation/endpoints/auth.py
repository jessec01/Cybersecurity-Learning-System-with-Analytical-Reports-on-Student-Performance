# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]    
from sqlalchemy.orm import Session

from application.dto.auth_dto import LoginInput, RegisterInput, SuperAdminLoginInput, SuperAdminRegisterInput, TokenOutput
from application.use_cases.auth_use_cases import LoginUseCase, RegisterUseCase, SuperAdminLoginUseCase
from domain.entities.super_admins import SuperAdmins
from domain.errors.auth_errors import UnauthorizedError
from infrastructure.db.postgres.connection import get_db
from infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOutput)
def login(body: LoginInput, db: Session = Depends(get_db)):
    try:
        return LoginUseCase(db).execute(body)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterInput, db: Session = Depends(get_db)):
    try:
        RegisterUseCase(db).execute(body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return {"message": "Usuario registrado exitosamente"}


@router.post("/logout")
def logout():
    return {"message": "Sesion cerrada"}


@router.post("/super-admin/login", response_model=TokenOutput)
def super_admin_login(body: SuperAdminLoginInput, db: Session = Depends(get_db)):
    try:
        return SuperAdminLoginUseCase(db).execute(body)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/super-admin/register", status_code=status.HTTP_201_CREATED)
def super_admin_register(body: SuperAdminRegisterInput, db: Session = Depends(get_db)):
    repo = SuperAdminRepository(db)
    admin = SuperAdmins(id_person=body.id_person, is_active=True, secret_key=body.secret_key)
    repo.save(admin)
    return {"message": "Super admin registrado exitosamente"}