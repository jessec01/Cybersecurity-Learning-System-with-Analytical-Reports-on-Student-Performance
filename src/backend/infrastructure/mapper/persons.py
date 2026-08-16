from backend.domain.entities.persons import Person
from backend.infrastructure.db.postgres.models import PersonModel

class PersonsMapper:
    @staticmethod
    def to_entity(model: PersonModel) -> Person:
        return Person(
            id_person=model.id_person,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            mail=model.mail,
            id_user=model.id_user,
        )

    @staticmethod
    def to_model(person: Person) -> PersonModel:
        return PersonModel(
            id_person=person.id_person,
            first_name=person.first_name,
            last_name=person.last_name,
            phone=person.phone,
            mail=person.mail,
            id_user=person.id_user,
        )   