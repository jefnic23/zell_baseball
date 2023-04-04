from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import settings


Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True
        )
        self.session = async_sessionmaker(
            self.engine, 
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        async with self.session() as session:
            async with session.begin():
                yield session


db = Database()
