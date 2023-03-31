import json
from datetime import datetime
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from fake_useragent import UserAgent


MLB_BASE_URL = "https://statsapi.mlb.com"


def make_request(
        url: str, 
        method: str = 'GET', 
        payload: dict = None
    ) -> SimpleNamespace:
    '''Makes an HTTP request to the given URL.'''

    req = Request(url, method=method)
    req.add_header('User-Agent', UserAgent().random)
    if payload:
        req.add_header('Content-Type', 'application/json')
        payload = json.dumps(payload).encode()
    res = urlopen(req, data=payload)
    try:
        return json.loads(res.read(), object_hook=lambda d: SimpleNamespace(**d))
    except HTTPError as e:
        print(e) # TODO: Log this error
        return None


def betting_data(date: datetime) -> SimpleNamespace:
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
    req = make_request(url, method='POST', payload=payload)
    if req:
        return req.Scores
    else:
        print("Error getting betting data")
        return None
    

def schedule(date: datetime) -> list:
    url = f"{MLB_BASE_URL}/api/v1/schedule/games/?sportId=1&date={date.strftime('%m/%d/%Y')}"
    req = make_request(url)
    if req:
        filtered = filter(
            lambda game: game.status.codedGameState in ["P", "S"], 
            req.dates[0].games
        )
        return sorted(list(filtered), key=lambda game: game.gameDate)
    else:
        print("Error getting schedule")
        return None
