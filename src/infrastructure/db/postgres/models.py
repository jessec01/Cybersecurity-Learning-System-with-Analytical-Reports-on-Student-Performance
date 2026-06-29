# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean, Text, Date, DateTime, ForeignKey, Enum
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from infrastructure.db.postgres.connection import Base


class UserModel(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(200), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_token_verified = Column(Boolean, default=False, nullable=False)
    is_token_reset = Column(Boolean, default=False, nullable=False)
    is_token_expired = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    person = relationship("PersonModel", back_populates="user", uselist=False)


class PersonModel(Base):
    __tablename__ = "persons"

    id_person = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(200), nullable=False, index=True, unique=True)
    last_name = Column(String(200), nullable=False, index=True)
    mail = Column(String(500), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    id_users = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    user = relationship("UserModel", back_populates="person")
    rol_persons = relationship("RolPersonModel", back_populates="person")


class RoleModel(Base):
    __tablename__ = "roles"

    id_roles = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), unique=True, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    rol_persons = relationship("RolPersonModel", back_populates="role")
    rol_permissions = relationship("RolPermissionModel", back_populates="role")


class RolPersonModel(Base):
    __tablename__ = "rol_persons"

    id_person = Column(Integer, ForeignKey("persons.id_person", ondelete="CASCADE"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("roles.id_roles", ondelete="CASCADE"), primary_key=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    person = relationship("PersonModel", back_populates="rol_persons")
    role = relationship("RoleModel", back_populates="rol_persons")


class PermissionModel(Base):
    __tablename__ = "permissions"

    id_permission = Column(Integer, primary_key=True, autoincrement=True)
    codename = Column(String(100), unique=True, nullable=False)
    resource = Column(String(70), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    rol_permissions = relationship("RolPermissionModel", back_populates="permission")


class RolPermissionModel(Base):
    __tablename__ = "rol_permissions"

    id_rol = Column(Integer, ForeignKey("roles.id_roles", ondelete="CASCADE"), primary_key=True)
    id_permission = Column(Integer, ForeignKey("permissions.id_permission", ondelete="CASCADE"), primary_key=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    role = relationship("RoleModel", back_populates="rol_permissions")
    permission = relationship("PermissionModel", back_populates="rol_permissions")


class SuperAdminModel(Base):
    __tablename__ = "super_admins"

    id_super_admin = Column(Integer, primary_key=True, autoincrement=True)
    secret_key = Column(String(500), unique=True, nullable=False)
    id_person = Column(Integer, ForeignKey("persons.id_person", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
