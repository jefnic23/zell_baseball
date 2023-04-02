from datetime import datetime
from backend.services.http_client import post_async
from backend.models.betting_data import BettingData, betting_data_schema


async def betting_data(date: datetime) -> BettingData:
    """Gets the odds from bettingdata.com"""

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
    payload = {'filters': filters}
    req = await post_async(url, payload=payload)
    if req:
        return betting_data_schema.load(req).Scores
    else:
        print("Error getting betting data")
        return None
