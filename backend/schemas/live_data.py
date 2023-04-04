from pydantic import BaseModel


class Official(BaseModel):
    fullName: str
    id: int    


class Officials(BaseModel):
    official: Official
    officialType: str
    

class Team(BaseModel):
    battingOrder: list[int]
    bullpen: list[int]


class Teams(BaseModel):
    away: Team
    home: Team


class Boxscore(BaseModel):
    teams: Teams
    officials: list[Officials]


class LiveData(BaseModel):
    boxscore: Boxscore
