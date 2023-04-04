from datetime import time

import jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column

from backend.config import settings
from backend.database import Base, db


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password)

    def set_password(self, password: str) -> None:
        self.password = password

    def get_reset_password_token(self, expires_in: int = 600) -> str:
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in}, 
            settings.SECRET_KEY, 
            algorithm='HS256'
        )

    @staticmethod
    async def verify_reset_password_token(token: str) -> 'User' | None:
        try:
            id = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )['reset_password']
        except:  # noqa: E722
            return None
        async with db.session() as session:
            query = await session.execute(select(User).where(User.id == id))
            return query.scalars().first()


class Batter(Base):
    __tablename__ = "batters"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str] = mapped_column(nullable=False)
    stand = Mapped[str] = mapped_column(nullable=False)
    woba_r = Mapped[float] = mapped_column(nullable=False)
    woba_l = Mapped[float] = mapped_column(nullable=False)
    woba = Mapped[float] = mapped_column(nullable=False)


class Fielding(Base):
    __tablename__ = "fielding"

    id = Mapped[int] = mapped_column(ForeignKey('batters.id'), primary_key=True)
    name = Mapped[str] = mapped_column(ForeignKey('batters.name'), nullable=False)
    runs = Mapped[float] = mapped_column(nullable=False)


class Woba(Base):
    __tablename__ = "woba"

    woba = Mapped[float] = mapped_column(primary_key=True)
    runs = Mapped[float] = mapped_column(nullable=False)


class Matchup(Base):
    __tablename__ = "matchups"

    matchup = Mapped[str] = mapped_column(primary_key=True)
    odds = Mapped[float] = mapped_column(nullable=False)


class Misc(Base):
    __tablename__ = "misc"

    name = Mapped[str] = mapped_column(primary_key=True)
    value = Mapped[float] = mapped_column(nullable=False)


class Park(Base):
    __tablename__ = "parks"

    park = Mapped[str] = mapped_column(primary_key=True)
    runs = Mapped[float] = mapped_column(nullable=False)
    over_threshold = Mapped[float] = mapped_column(nullable=False)
    under_threshold = Mapped[float] = mapped_column(nullable=False)
    handicap = Mapped[float] = mapped_column(nullable=False)


class Pitcher(Base):
    __tablename__ = "pitchers"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str] = mapped_column(nullable=False)
    p_throws = Mapped[str] = mapped_column(nullable=False)
    woba_r = Mapped[float] = mapped_column(nullable=False)
    woba_l = Mapped[float] = mapped_column(nullable=False)
    woba = Mapped[float] = mapped_column(nullable=False)
    ips = Mapped[float] = mapped_column(nullable=False)


class Ump(Base):
    __tablename__ = "umps"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str] = mapped_column(unique=True, nullable=False)
    runs = Mapped[float] = mapped_column(nullable=False)
