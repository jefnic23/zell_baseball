from typing import List

from pydantic import BaseModel


class Official(BaseModel):
    fullName: str
    id: int    


class Officials(BaseModel):
    official: Official
    officialType: str
    

class Team(BaseModel):
    battingOrder: List[int]
    bullpen: List[int]


class Teams(BaseModel):
    away: Team
    home: Team


class Boxscore(BaseModel):
    teams: Teams
    officials: List[Officials]


class LiveData(BaseModel):
    boxscore: Boxscore
