from typing import Optional

from pydantic import BaseModel


class ProbablePitcher(BaseModel):
    fullName: str
    id: int


class ProbablePitchers(BaseModel):
    away: ProbablePitcher
    home: ProbablePitcher


class Team(BaseModel):
    abbreviation: str
    name: str


class Teams(BaseModel):
    away: Team
    home: Team


class Weather(BaseModel):
    condition: Optional[str]
    temp: Optional[str]
    wind: Optional[str]

    
class GameData(BaseModel):
    teams: Teams
    probablePitchers: ProbablePitchers
    weather: Weather
