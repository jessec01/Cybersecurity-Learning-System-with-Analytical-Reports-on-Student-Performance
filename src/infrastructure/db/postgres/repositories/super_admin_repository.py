from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from domain.entities.super_admins import SuperAdmins
from domain.repositories.repositoriesuper_admins import RepositorieSuperAdmin
from infrastructure.db.postgres.models import SuperAdminModel


class SuperAdminRepository(RepositorieSuperAdmin):

    def __init__(self, db: Session):
        self._db = db

    def save(self, super_admin: SuperAdmins) -> None:
        model = SuperAdminModel(
            secret_key=super_admin.secret_key,
            id_person=super_admin.id_person,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()

    def update(self, super_admin: SuperAdmins) -> None:
        model = self._db.query(SuperAdminModel).filter(SuperAdminModel.id_super_admin == super_admin.id_super_admin).first()
        if model:
            model.secret_key = super_admin.secret_key
            model.is_active = super_admin.is_active
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()

    def delete(self, super_admin: SuperAdmins) -> None:
        model = self._db.query(SuperAdminModel).filter(SuperAdminModel.id_super_admin == super_admin.id_super_admin).first()
        if model:
            self._db.delete(model)
            self._db.commit()

    def get_by_id(self, super_admin_id: int) -> SuperAdmins | None:
        model = self._db.query(SuperAdminModel).filter(SuperAdminModel.id_super_admin == super_admin_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_by_secret_key(self, secret_key: str) -> SuperAdmins | None:
        model = self._db.query(SuperAdminModel).filter(SuperAdminModel.secret_key == secret_key).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_all(self) -> list[SuperAdmins]:
        models = self._db.query(SuperAdminModel).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: SuperAdminModel) -> SuperAdmins:
        return SuperAdmins(
            id_super_admin=model.id_super_admin,
            id_person=model.id_person,
            is_active=True,
            secret_key=model.secret_key,
        )
