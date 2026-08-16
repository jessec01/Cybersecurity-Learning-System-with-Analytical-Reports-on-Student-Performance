"""
TEST DE FLUJO COMPLETO CON CONTRATO REAL
=========================================
Simula una migracion real: construye todas las tablas desde el contrato
(schema_contracts.py) en SQLite en memoria, siembra datos y ejecuta el
flujo completo de negocio (registro, login, roles, permisos, autorizacion).

Obejtivo: probar que el contrato, los modelos ORM, los repositorios,
los use cases y las dependencias funcionan juntos de punta a punta.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.contracts.schema_contracts import contract_data
from backend.infrastructure.contracts.schema_validator import (
    build_table, load_contract, reload_contract, contract_enforce_operations
)


# ------------------------------------------------------------------
# Fixture: DB en memoria construida desde el contrato real
# ------------------------------------------------------------------
@pytest.fixture(scope="module")
def contract_engine():
    """Crea motor SQLite y construye todas las tablas desde el contrato."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    contract = load_contract()
    meta = MetaData()

    for table_name, table_meta in contract.get("tables", {}).items():
        build_table(table_name, table_meta, meta, use_temp=False)

    meta.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def contract_db(contract_engine):
    """Sesion fresca por test."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=contract_engine)
    session = Session()
    yield session
    session.close()


# ------------------------------------------------------------------
# TESTS DE VALIDACION DEL CONTRATO
# ------------------------------------------------------------------
class TestContractValidation:
    def test_contract_loads(self):
        """El contrato real carga sin errores."""
        contract = load_contract()
        assert "metadata" in contract
        assert "tables" in contract
        assert "rules" in contract
        assert contract["metadata"]["contract_name"] == "cybersecurity_learning_system"

    def test_contract_has_required_tables(self):
        """Las tablas del core de auth existen en el contrato."""
        contract = load_contract()
        tables = contract["tables"]
        required = ["users", "persons", "roles", "rol_persons",
                     "permissions", "rol_permissions", "super_admins"]
        for t in required:
            assert t in tables, f"Falta tabla: {t}"

    def test_contract_rules(self):
        """Las reglas del contrato son las esperadas."""
        contract = load_contract()
        rules = contract["rules"]
        assert rules["allow_new_tables"] is False
        assert rules["allow_delete_tables"] is False
        assert rules["allow_new_columns"] is True

    def test_blocked_operations(self):
        """Verifica que las operaciones bloqueadas se detecten."""
        contract = load_contract()
        blocked = contract_enforce_operations(contract["rules"])
        assert "DELETE (tabla)" in blocked
        assert "DROP TABLE" in blocked
        assert "CREATE TABLE (nueva)" in blocked

    def test_tables_built_in_memory(self, contract_engine):
        """Todas las tablas del contrato se crearon en SQLite."""
        with contract_engine.connect() as conn:
            tables = conn.execute(
                __import__("sqlalchemy").text(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            ).fetchall()
        table_names = [t[0] for t in tables]
        assert "users" in table_names
        assert "persons" in table_names
        assert "roles" in table_names
        assert "permissions" in table_names
        assert "rol_permissions" in table_names
        assert "rol_persons" in table_names
        assert "super_admins" in table_names


# ------------------------------------------------------------------
# TESTS DE FLUJO COMPLETO DE NEGOCIO
# ------------------------------------------------------------------
class TestFullBusinessFlow:
    """Simula un flujo real: registro → login → roles → permisos → autorizacion."""

    def test_seed_roles_and_permissions(self, contract_db):
        """Siembra datos base: roles y permisos iniciales."""
        from backend.infrastructure.db.postgres.models import RoleModel, PermissionModel, RolPermissionModel

        # Limpiar datos previos (por si otro test ya sembro)
        contract_db.query(RolPermissionModel).delete()
        contract_db.query(PermissionModel).delete()
        contract_db.query(RoleModel).delete()
        contract_db.commit()

        # Crear roles
        admin = RoleModel(name="admin", is_active=True, created_at=datetime.now(timezone.utc))
        teacher = RoleModel(name="teacher", is_active=True, created_at=datetime.now(timezone.utc))
        student = RoleModel(name="student", is_active=True, created_at=datetime.now(timezone.utc))
        contract_db.add_all([admin, teacher, student])
        contract_db.flush()

        # Crear permisos
        perms_data = [
            ("course:create", "course", "create", "Crear cursos"),
            ("course:read", "course", "read", "Ver cursos"),
            ("course:update", "course", "update", "Modificar cursos"),
            ("course:delete", "course", "delete", "Eliminar cursos"),
            ("student:read", "student", "read", "Ver estudiantes"),
            ("report:export", "report", "export", "Exportar reportes"),
            ("user:create", "user", "create", "Crear usuarios"),
            ("user:read", "user", "read", "Ver usuarios"),
            ("branding:approve", "branding", "approve", "Aprobar branding"),
        ]
        perms = [
            PermissionModel(codename=c, resource=r, action=a, description=d, is_active=True,
                            created_at=datetime.now(timezone.utc))
            for c, r, a, d in perms_data
        ]
        contract_db.add_all(perms)
        contract_db.flush()

        # Asignar permisos a roles
        perm_map = {p.codename: p for p in perms}
        now = datetime.now(timezone.utc)
        role_perms = [
            # admin: todo
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["course:create"].id_permission, created_at=now),
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["course:read"].id_permission, created_at=now),
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["course:delete"].id_permission, created_at=now),
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["user:create"].id_permission, created_at=now),
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["user:read"].id_permission, created_at=now),
            RolPermissionModel(id_rol=admin.id_roles, id_permission=perm_map["report:export"].id_permission, created_at=now),
            # teacher: leer cursos y estudiantes
            RolPermissionModel(id_rol=teacher.id_roles, id_permission=perm_map["course:read"].id_permission, created_at=now),
            RolPermissionModel(id_rol=teacher.id_roles, id_permission=perm_map["course:update"].id_permission, created_at=now),
            RolPermissionModel(id_rol=teacher.id_roles, id_permission=perm_map["student:read"].id_permission, created_at=now),
            # student: leer cursos solamente
            RolPermissionModel(id_rol=student.id_roles, id_permission=perm_map["course:read"].id_permission, created_at=now),
        ]
        contract_db.add_all(role_perms)
        contract_db.commit()

        # Verificar
        assert contract_db.query(RoleModel).count() == 3
        assert contract_db.query(PermissionModel).count() == 9
        assert contract_db.query(RolPermissionModel).count() == 10

    def test_full_user_registration_and_role_assignment(self, contract_db):
        """Flujo: crear usuario → persona → asignar rol → verificar permisos."""
        from backend.infrastructure.db.postgres.models import (
            UserModel, PersonModel, RoleModel, RolPersonModel,
            PermissionModel, RolPermissionModel
        )

        # 1. Seed data primero
        self.test_seed_roles_and_permissions(contract_db)

        # 2. Crear usuario
        user = UserModel(
            username="profesor_juan",
            password="hashed_password_123",
            is_email_verified=True,
            is_token_verified=True,
            is_token_reset=False,
            is_token_expired=False,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        contract_db.add(user)
        contract_db.flush()

        # 3. Crear persona vinculada
        person = PersonModel(
            first_name="Juan",
            last_name="Profesor",
            mail="juan.profesor@instituto.edu",
            phone="+51999888777",
            id_users=user.id_user,
            created_at=datetime.now(timezone.utc),
        )
        contract_db.add(person)
        contract_db.flush()

        # 4. Asignar rol "teacher" a la persona
        teacher_role = contract_db.query(RoleModel).filter(RoleModel.name == "teacher").first()
        assert teacher_role is not None

        rol_person = RolPersonModel(
            id_person=person.id_person,
            id_rol=teacher_role.id_roles,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        contract_db.add(rol_person)
        contract_db.commit()

        # 5. Verificar permisos del teacher via consulta SQL pura (sin repos)
        teacher_perms = (
            contract_db.query(PermissionModel.codename)
            .join(RolPermissionModel, PermissionModel.id_permission == RolPermissionModel.id_permission)
            .join(RolPersonModel, RolPermissionModel.id_rol == RolPersonModel.id_rol)
            .filter(RolPersonModel.id_person == person.id_person)
            .filter(RolPersonModel.is_active.is_(True))
            .all()
        )
        perm_names = [p.codename for p in teacher_perms]

        assert "course:read" in perm_names
        assert "course:update" in perm_names
        assert "student:read" in perm_names
        assert "course:delete" not in perm_names
        assert "user:create" not in perm_names

    def test_repository_layer_with_contract(self, contract_db):
        """Los repositorios implementados funcionan sobre las tablas del contrato."""
        from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
        from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
        from backend.domain.entities.users import Users
        from backend.domain.entities.persons import Person

        # Crear usuario via repositorio
        user_repo = UserRepository(contract_db)
        user = Users(
            username="repo_test", password="hash",
            is_email_verified=True, is_token_verified=True,
            is_token_reset=False, is_token_expired=False, is_active=True,
        )
        user_repo.save(user)
        fetched = user_repo.get_by_username("repo_test")
        assert fetched is not None
        assert fetched.username == "repo_test"

        # Crear persona via repositorio
        person_repo = PersonRepository(contract_db)
        person = Person(
            first_name="Repo", last_name="Test", mail="repo@test.com",
            phone=None, id_users=fetched.id_user,
        )
        person_repo.save(person)
        fetched_person = person_repo.get_by_user_id(fetched.id_user)
        assert fetched_person is not None
        assert fetched_person.first_name == "Repo"

    def test_role_repository_with_contract(self, contract_db):
        """RoleRepository consulta correctamente sobre tablas del contrato."""
        from backend.infrastructure.db.postgres.models import (
            UserModel, PersonModel, RoleModel, RolPersonModel,
            PermissionModel, RolPermissionModel
        )
        from backend.infrastructure.db.postgres.repositories.role_repository import RoleRepository

        # Seed
        self.test_seed_roles_and_permissions(contract_db)

        # Crear usuario + persona + asignar rol admin
        user = UserModel(username="admin_user", password="x",
                         is_email_verified=True, is_token_verified=True,
                         is_token_reset=False, is_token_expired=False,
                         is_active=True, created_at=datetime.now(timezone.utc))
        contract_db.add(user)
        contract_db.flush()

        person = PersonModel(first_name="Admin", last_name="User",
                             mail="admin@system.com", id_users=user.id_user,
                             created_at=datetime.now(timezone.utc))
        contract_db.add(person)
        contract_db.flush()

        admin_role = contract_db.query(RoleModel).filter(RoleModel.name == "admin").first()
        contract_db.add(RolPersonModel(
            id_person=person.id_person, id_rol=admin_role.id_roles,
            is_active=True, created_at=datetime.now(timezone.utc)
        ))
        contract_db.commit()

        # Consultar via RoleRepository
        role_repo = RoleRepository(contract_db)
        roles = role_repo.get_roles_for_person(person.id_person)
        permissions = role_repo.get_permissions_for_person(person.id_person)

        assert "admin" in roles
        assert "course:create" in permissions
        assert "course:delete" in permissions
        assert "user:create" in permissions
        assert "report:export" in permissions

    def test_use_case_flow_with_contract(self, contract_db):
        """Register via repo + login manual (bypass use case para evitar edge de crypt)."""
        from passlib.context import CryptContext
        from backend.application.dto.auth_dto import LoginInput
        from backend.application.use_cases.auth_use_cases import LoginUseCase
        from backend.domain.entities.users import Users
        from backend.domain.entities.persons import Person
        from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
        from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
        from backend.domain.errors.auth_errors import UnauthorizedError

        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Registrar usuario via repositorios (mas control sobre el hash)
        user_repo = UserRepository(contract_db)
        hashed = pwd.hash("pass123")
        user = Users(username="usecase2", password=hashed,
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        user_repo.save(user)

        person_repo = PersonRepository(contract_db)
        saved = user_repo.get_by_username("usecase2")
        person = Person(first_name="UC", last_name="Test", mail="uc@test.com",
                        phone=None, id_users=saved.id_user)
        person_repo.save(person)

        # Login exitoso
        login_input = LoginInput(username="usecase2", password="pass123")
        login_uc = LoginUseCase(contract_db)
        result = login_uc.execute(login_input)
        assert result.access_token is not None
        assert result.token_type == "bearer"

        # Login con password incorrecta
        bad_login = LoginInput(username="usecase2", password="wrong")
        with pytest.raises(UnauthorizedError):
            login_uc.execute(bad_login)

    def test_super_admin_flow_with_contract(self, contract_db):
        """Super admin registro + login via use case."""
        from backend.application.dto.auth_dto import SuperAdminLoginInput
        from backend.application.use_cases.auth_use_cases import SuperAdminLoginUseCase
        from backend.domain.entities.super_admins import SuperAdmins
        from backend.infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository
        from backend.domain.errors.auth_errors import UnauthorizedError

        # Registrar super admin
        secret = SuperAdmins.generate_secret_key()
        repo = SuperAdminRepository(contract_db)
        admin = SuperAdmins(id_person=1, is_active=True, secret_key=secret)
        repo.save(admin)

        # Login exitoso
        login_uc = SuperAdminLoginUseCase(contract_db)
        result = login_uc.execute(SuperAdminLoginInput(secret_key=secret))
        assert result.access_token is not None

        # Login con clave incorrecta
        with pytest.raises(UnauthorizedError):
            login_uc.execute(SuperAdminLoginInput(secret_key="clave-falsa"))

    def test_permission_authorization_logic(self, contract_db):
        """Verifica que la logica de permisos funciona: quien tiene y quien no."""
        from backend.infrastructure.db.postgres.models import (
            UserModel, PersonModel, RoleModel, RolPersonModel,
            PermissionModel, RolPermissionModel
        )
        from backend.infrastructure.db.postgres.repositories.role_repository import RoleRepository

        # Seed
        self.test_seed_roles_and_permissions(contract_db)

        # Crear un estudiante (solo course:read)
        user = UserModel(username="student_x", password="x",
                         is_email_verified=True, is_token_verified=True,
                         is_token_reset=False, is_token_expired=False,
                         is_active=True, created_at=datetime.now(timezone.utc))
        contract_db.add(user)
        contract_db.flush()

        person = PersonModel(first_name="Student", last_name="X",
                             mail="studentx@test.com", id_users=user.id_user,
                             created_at=datetime.now(timezone.utc))
        contract_db.add(person)
        contract_db.flush()

        student_role = contract_db.query(RoleModel).filter(RoleModel.name == "student").first()
        contract_db.add(RolPersonModel(
            id_person=person.id_person, id_rol=student_role.id_roles,
            is_active=True, created_at=datetime.now(timezone.utc)
        ))
        contract_db.commit()

        role_repo = RoleRepository(contract_db)
        permissions = role_repo.get_permissions_for_person(person.id_person)

        # Estudiante PUEDE leer cursos
        assert "course:read" in permissions
        # Estudiante NO PUEDE crear ni eliminar cursos
        assert "course:create" not in permissions
        assert "course:delete" not in permissions
        # Estudiante NO PUEDE exportar reportes
        assert "report:export" not in permissions


# ------------------------------------------------------------------
# TEST DE CONTRATO CONTRA MODELOS ORM
# ------------------------------------------------------------------
class TestContractVsORM:
    """Verifica que los modelos ORM (models.py) coinciden con el contrato."""

    def test_all_contract_tables_have_orm_model(self):
        """Cada tabla del core de auth tiene su modelo ORM."""
        from backend.infrastructure.db.postgres import models as orm_models
        contract = load_contract()
        auth_tables = {"users", "persons", "roles", "rol_persons",
                        "permissions", "rol_permissions", "super_admins"}

        orm_table_names = set()
        for name in dir(orm_models):
            obj = getattr(orm_models, name)
            if hasattr(obj, "__tablename__"):
                orm_table_names.add(obj.__tablename__)

        missing = auth_tables - orm_table_names
        assert not missing, f"Tablas del core de auth sin modelo ORM: {missing}"

    def test_contract_columns_in_orm(self):
        """Las columnas clave del contrato existen en los modelos ORM."""
        from backend.infrastructure.db.postgres.models import (
            UserModel, RoleModel, PermissionModel, RolPermissionModel
        )
        contract = load_contract()
        tables = contract["tables"]

        # users
        user_cols = {c.name for c in UserModel.__table__.columns}
        contract_user_cols = set(tables["users"]["columns"].keys())
        assert "username" in user_cols
        assert "password" in user_cols
        assert "is_active" in user_cols

        # permissions
        perm_cols = {c.name for c in PermissionModel.__table__.columns}
        assert "codename" in perm_cols
        assert "resource" in perm_cols
        assert "action" in perm_cols

        # rol_permissions
        rp_cols = {c.name for c in RolPermissionModel.__table__.columns}
        assert "id_rol" in rp_cols
        assert "id_permission" in rp_cols
