from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(settings.DATABASE_URL_asyncpg)

Async_Session = async_sessionmaker(bind=async_engine, autoflush=False, autocommit=False)


def get_db():
    db = Async_Session()
    try:
        yield db
    finally:
        db.close()
