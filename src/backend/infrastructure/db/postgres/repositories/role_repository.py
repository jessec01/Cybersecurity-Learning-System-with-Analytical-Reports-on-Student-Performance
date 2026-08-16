# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from backend.infrastructure.db.postgres.models import RoleModel, RolPersonModel, PermissionModel, RolPermissionModel


class RoleRepository:

    def __init__(self, db: Session):
        self._db = db

    def get_roles_for_person(self, person_id: int) -> list[str]:
        rows = (
            self._db.query(RoleModel.name)
            .join(RolPersonModel, RoleModel.id_roles == RolPersonModel.id_rol)
            .filter(RolPersonModel.id_person == person_id, RolPersonModel.is_active.is_(True))
            .all()
        )
        return [row.name for row in rows]

    def get_permissions_for_person(self, person_id: int) -> list[str]:
        rows = (
            self._db.query(PermissionModel.codename)
            .join(RolPermissionModel, PermissionModel.id_permission == RolPermissionModel.id_permission)
            .join(RolPersonModel, RolPermissionModel.id_rol == RolPersonModel.id_rol)
            .filter(
                RolPersonModel.id_person == person_id,
                RolPersonModel.is_active.is_(True),
                RolPermissionModel.is_active.is_(True),
                PermissionModel.is_active.is_(True),
            )
            .all()
        )
        return [row.codename for row in rows]

    def get_permissions_for_role(self, role_id: int) -> list[str]:
        rows = (
            self._db.query(PermissionModel.codename)
            .join(RolPermissionModel, PermissionModel.id_permission == RolPermissionModel.id_permission)
            .filter(
                RolPermissionModel.id_rol == role_id,
                RolPermissionModel.is_active.is_(True),
                PermissionModel.is_active.is_(True),
            )
            .all()
        )
        return [row.codename for row in rows]
