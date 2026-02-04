from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

class Base(DeclarativeBase):
    pass

async_engine = create_async_engine(settings.DATABASE_URL_asyncpg)

AsyncSession = async_sessionmaker(bind=async_engine, autoflush=False, autocommit=False)

async def get_db():
    async with AsyncSession() as session:
        yield session