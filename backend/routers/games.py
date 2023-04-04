from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db
from backend.services.betting_data import get_betting_data
from backend.services.mlb import get_game_data, get_schedule
from backend.services.predictions import Predictions


router = APIRouter()


@router.get('/api/games')
async def get_games(date: str, db: AsyncSession = Depends(db.get_session)):
    """Gets the games for a given date."""

    date = datetime.strptime(date, "%m/%d/%Y")
    betting_data = await get_betting_data(date)
    schedule = await get_schedule(date)
    game = await get_game_data(schedule[0].link)
    predictions = Predictions(betting_data, game, db)
    return await predictions.get_prediction_data()
