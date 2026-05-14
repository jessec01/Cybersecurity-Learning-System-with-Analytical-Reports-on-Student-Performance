from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from infrastructure.db.postgres.setting import settings

engine = create_engine(settings.get_postgres_url)
session_local=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()


#inyectar_dependecias
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()