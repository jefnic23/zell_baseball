from datetime import datetime

from fastapi import APIRouter

from backend.services.mlb import get_game_data, get_schedule


router = APIRouter()


@router.get('/api/games')
async def get_games(date: str):
    """Gets the games for a given date."""

    date = datetime.strptime(date, "%m/%d/%Y")
    schedule = await get_schedule(date)
    return await get_game_data(schedule[0].link)
