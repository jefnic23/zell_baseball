from datetime import datetime

from backend.models.betting_data import BettingData
from backend.services.http_client import post_async


async def get_betting_data(date: datetime) -> BettingData:
    """Gets the odds from bettingdata.com."""

    url = "https://bettingdata.com/MLB_Odds/Odds_Read"
    filters = {
        "scope": 3, 
        "subscope": 1, 
        "season": date.year, 
        "date": date.strftime("%m-%d-%Y"), 
        "show_no_odds": False, 
        "client": 1, 
        "state": "WORLD", 
        "league": "mlb", 
        "widget_scope": 1
    }
    req = await post_async(url, payload={'filters': filters})
    if req:
        return BettingData(**req).Scores
    else:
        print("Error getting betting data")
        return None
