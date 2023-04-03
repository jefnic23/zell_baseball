from backend.models.mlb.game_data import GameData
from backend.models.mlb.live_data import LiveData

from pydantic import BaseModel


class Game(BaseModel):
    gameData: GameData
    liveData: LiveData
