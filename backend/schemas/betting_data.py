from typing import List, Optional

from pydantic import BaseModel


class TeamDetails(BaseModel):
    FullName: str


class Odds(BaseModel):
    SportsBookName: Optional[str]
    GameOddId: Optional[int]
    OverUnder: Optional[float]
    OverPayout: Optional[int]
    UnderPayout: Optional[int]


class Scores(BaseModel):
    GameID: int
    AwayTeamDetails: TeamDetails
    HomeTeamDetails: TeamDetails
    Consensus: Odds
    GameOddWebs: List[Odds]


class BettingData(BaseModel):
    Scores: List[Scores]
