from fastapi import APIRouter
from backend.services.betting_data_service import betting_data
from datetime import datetime

router = APIRouter()


@router.get('/api/games')
async def get_games(date: str):
    return await betting_data(datetime.strptime(date, "%m-%d-%Y"))
