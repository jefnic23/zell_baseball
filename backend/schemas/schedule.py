from typing import List

from pydantic import BaseModel


class Status(BaseModel):
    codedGameState: str
    detailedState: str


class TeamName(BaseModel):
    name: str


class Team(BaseModel):
    team: TeamName


class Teams(BaseModel):
    away: Team
    home: Team


class Game(BaseModel):
    doubleHeader: str
    gameDate: str
    gameNumber: int
    gamePk: int
    link: str
    scheduledInnings: int
    status: Status
    teams: Teams


class Date(BaseModel):
    date: str
    games: List[Game]


class Schedule(BaseModel):
    dates: List[Date]
