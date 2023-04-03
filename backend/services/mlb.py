from datetime import datetime
from typing import List

from backend.schemas.game import Game
from backend.schemas.schedule import Game as ScheduledGame
from backend.schemas.schedule import Schedule
from backend.services.http_client import get_async

BASE_URL = "https://statsapi.mlb.com"


async def get_schedule(
    date: datetime, 
    base: str = BASE_URL
) -> List[ScheduledGame]:
    '''Gets the schedule for a given date.'''

    url = f"{base}/api/v1/schedule/games/?sportId=1&date={date.strftime('%m/%d/%Y')}"
    req = await get_async(url)
    if req:
        filtered = filter(
            lambda game: game.status.codedGameState in ["P", "S"], 
            Schedule(**req).dates[0].games
        )
        return sorted(list(filtered), key=lambda game: game.gameDate)
    else:
        print("Error getting schedule")
        return None
    

async def get_game_data(
    link: str, 
    base: str = BASE_URL
) -> Game:
    '''Gets the data for a given game.'''

    url = f"{base}{link}"
    req = await get_async(url)
    if req:
        return Game(**req)
    else:
        print("Error getting game data")
        return None
