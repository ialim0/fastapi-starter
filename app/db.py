from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from databases import Database
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""
    pass

database = Database(DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import user 
    Base.metadata.create_all(bind=engine)