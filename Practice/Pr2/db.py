from sqlmodel import SQLModel, Session, create_engine
import os
db_url = 'postgresql://postgres:15112002@localhost:5432/warriors_db'

engine = create_engine(db_url)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session