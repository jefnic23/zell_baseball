import json
from datetime import datetime
from types import SimpleNamespace
from urllib.request import Request, urlopen


def betting_data(date: datetime) -> SimpleNamespace:
    """Gets the odds from bettingdata.com"""

    url = "https://bettingdata.com/MLB_Odds/Odds_Read"
    payload = json.dumps(
        {"filters": 
            {"scope": 3, 
             "subscope": 1, 
             "season": date.year, 
             "date": date.strftime("%m-%d-%Y"), 
             "show_no_odds": False, 
             "client": 1, 
             "state": "WORLD", 
             "league": "mlb", 
             "widget_scope": 1
            }
        }
    ).encode()
    req = Request(url, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header(
        'User-Agent', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    )
    res = urlopen(req, data=payload)
    if res.status not in [200, 201]:
        res.error()
    else:
        return json.loads(res.read(), object_hook=lambda d: SimpleNamespace(**d))
