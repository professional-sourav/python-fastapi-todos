from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

SA_DB_URL = 'sqlite:///./todos.db'

engine = create_engine(
    SA_DB_URL,
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]