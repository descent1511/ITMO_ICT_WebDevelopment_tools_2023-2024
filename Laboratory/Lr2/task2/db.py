from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

engine = create_engine(DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    session = Session(engine)
    return session


class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field()


def add_page(page: Page) -> Page:
    session = get_session()
    try:
        session.add(page)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    init_db()  
