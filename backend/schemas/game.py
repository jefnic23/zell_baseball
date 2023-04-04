from backend.schemas.game_data import GameData
from backend.schemas.live_data import LiveData

from pydantic import BaseModel


class Game(BaseModel):
    gameData: GameData
    liveData: LiveData
