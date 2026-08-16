import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.infrastructure.db.postgres.connection import Base
from backend.infrastructure.server.server import create_application


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)





@pytest.fixture
def sample_user_dict():
    return {
        "username": "testuser",
        "password": "plain123",
        "first_name": "Test",
        "last_name": "User",
        "mail": "test@example.com",
        "phone": "+51999888777",
    }
