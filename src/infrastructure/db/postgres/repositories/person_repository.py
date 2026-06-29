from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from domain.entities.persons import Person
from domain.repositories.repositoriepersons import RepositoriePerson
from infrastructure.db.postgres.models import PersonModel


class PersonRepository(RepositoriePerson):

    def __init__(self, db: Session):
        self._db = db

    def save(self, person: Person) -> None:
        model = PersonModel(
            first_name=person.first_name,
            last_name=person.last_name,
            mail=person.mail,
            phone=person.phone,
            date_of_birth=person.date_of_birth,
            id_users=person.id_users,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()

    def update(self, person: Person) -> None:
        model = self._db.query(PersonModel).filter(PersonModel.mail == person.mail).first()
        if model:
            model.first_name = person.first_name
            model.last_name = person.last_name
            model.phone = person.phone
            model.date_of_birth = person.date_of_birth
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()

    def delete(self, person: Person) -> None:
        model = self._db.query(PersonModel).filter(PersonModel.mail == person.mail).first()
        if model:
            self._db.delete(model)
            self._db.commit()

    def get_by_id(self, person_id: int) -> Person | None:
        model = self._db.query(PersonModel).filter(PersonModel.id_person == person_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_by_user_id(self, user_id: int) -> Person | None:
        model = self._db.query(PersonModel).filter(PersonModel.id_users == user_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_by_email(self, email: str) -> Person | None:
        model = self._db.query(PersonModel).filter(PersonModel.mail == email).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_all(self) -> list[Person]:
        models = self._db.query(PersonModel).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: PersonModel) -> Person:
        return Person(
            id_person=model.id_person,
            first_name=model.first_name,
            last_name=model.last_name,
            mail=model.mail,
            phone=model.phone,
            date_of_birth=model.date_of_birth,
            id_users=model.id_users,
        )
