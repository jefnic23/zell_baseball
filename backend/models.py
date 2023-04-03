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
    async def verify_reset_password_token(token: str) -> 'User':
        try:
            id = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )['reset_password']
        except:  # noqa: E722
            return
        async with db.session() as session:
            query = await session.execute(select(User).where(User.id == id))
            return query.scalars().first()


class Batter(Base):
    __tablename__ = "batters"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = db.Column(db.String(), nullable=False)
    stand = db.Column(db.String(), nullable=False)
    woba_r = db.Column(db.Float, nullable=False)
    woba_l = db.Column(db.Float, nullable=False)
    woba = db.Column(db.Float, nullable=False)


class Fielding(Base):
    __tablename__ = "fielding"

    id = Mapped[int] = mapped_column(ForeignKey('batters.id'), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    runs = db.Column(db.Float, nullable=False)


class Woba(Base):
    __tablename__ = "woba"

    woba = db.Column(db.Float, primary_key=True)
    runs = db.Column(db.Float, nullable=False)


class Matchup(Base):
    __tablename__ = "matchups"

    matchup = db.Column(db.String(), primary_key=True)
    odds = db.Column(db.Float, nullable=False)


class Misc(Base):
    __tablename__ = "misc"

    name = db.Column(db.String(), primary_key=True)
    value = db.Column(db.Float, nullable=False)


class Park(Base):
    __tablename__ = "parks"

    park = db.Column(db.String(), primary_key=True)
    runs = db.Column(db.Float, nullable=False)
    over_threshold = db.Column(db.Float, nullable=False)
    under_threshold = db.Column(db.Float, nullable=False)
    handicap = db.Column(db.Float, nullable=False)


class Pitcher(Base):
    __tablename__ = "pitchers"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = db.Column(db.String(), nullable=False)
    p_throws = db.Column(db.String(), nullable=False)
    woba_r = db.Column(db.Float, nullable=False)
    woba_l = db.Column(db.Float, nullable=False)
    woba = db.Column(db.Float, nullable=False)
    ips = db.Column(db.Float, nullable=False)


class Ump(Base):
    __tablename__ = "umps"

    id = Mapped[int] = mapped_column(primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    runs = db.Column(db.Float, nullable=False)
