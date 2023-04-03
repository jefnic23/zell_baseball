from asyncio import gather
from datetime import datetime

from backend.services.betting_data import get_betting_data
from backend.services.mlb import get_game_data, get_schedule


class ZellBall:
    def __init__(self, date: datetime):
        self.date = date


    async def get_games(self):
        '''Gets the games for a given date.'''

        betting_data = await get_betting_data(self.date)
        schedule = await get_schedule(self.date)