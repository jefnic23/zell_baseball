from typing import List

from marshmallow import EXCLUDE, Schema
from marshmallow_dataclass import dataclass


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


@dataclass(base_schema=BaseSchema)
class TeamDetails:
    FullName: str


@dataclass(base_schema=BaseSchema)
class Consensus:
    GameId: int
    GameOddId: int
    OverUnder: float
    OverPayout: int
    UnderPayout: int


@dataclass(base_schema=BaseSchema)
class Scores:
    AwayTeamDetails: TeamDetails
    HomeTeamDetails: TeamDetails
    Consensus: Consensus


@dataclass(base_schema=BaseSchema)
class BettingData:
    Scores: List[Scores]


betting_data_schema = BettingData.Schema()
