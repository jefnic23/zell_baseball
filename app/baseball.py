import requests
from datetime import datetime
from app.models import Batters, Fielding, Matchups, Parks, Pitchers, Umps, Woba


def getTemp(temp, innings):
    '''Get run value based on game time temperature.'''
    if temp <= 46:
        return round(-0.225 * (innings/9), 2)
    elif 47 <= temp <= 53:
        return round(-0.15 * (innings/9), 2)
    elif 54 <= temp <= 62:
        return round(-0.075 * (innings/9), 2)
    elif 63 <= temp <= 71:
        return 0.0
    elif 72 <= temp <= 79:
        return round(0.1 * (innings/9), 2)
    elif 80 <= temp <= 87:
        return round(0.2 * (innings/9), 2)
    else:
        return round(0.3 * (innings/9), 2)

def getWind(venue, wind_data, innings):
    '''
    Get run value based on game time wind speed and direction.
    Only applies to Wrigley Field.
    '''
    speed = int(wind_data[0])
    direction = wind_data[1]
    wind = 0
    if venue == "Chicago Cubs" and speed >= 10 and direction == "In":
        for _ in range(0, speed - 10 + 1):
            wind -= 0.15
    if venue == "Chicago Cubs" and speed >= 10 and direction == "Out":
        for _ in range(0, speed - 10 + 1):
            wind += 0.15
    return round(wind * (innings/9), 2)

def getUmp(ump, innings):
    '''Query Ump table by ump id and return run value.'''
    try:
        runs = Umps.query.filter_by(id=ump).first().runs
    except:
        runs = 0
    return round(runs * (innings/9), 2)

def getFielding(lineup, innings):
    '''Query Fielding table by player id and return team defense run value.'''
    runs = 0
    fielders = Fielding.query.filter(Fielding.id.in_([id for id in lineup])).all()
    for player in fielders:
        try:
            runs += player.runs
        except:
            runs += 0
    return round(runs * (innings/9), 2)

def getBullpen(bullpen, lineup):
    '''Query Bullpen table by player id and return team bullpen run value.'''
    bullpen_woba = [player.woba for player in bullpen]
    offense_woba = [player.woba for player in lineup]
    return oddsRatio((sum(offense_woba) / len(offense_woba)), (sum(bullpen_woba) / len(bullpen_woba)), 'league')

def oddsRatio(hitter, pitcher, matchup):
    '''
    Calculate odds ratio of a batter/pitcher matchup.
    Query Matchups table by odds ratio and return run value.
    '''
    league = Matchups.query.get(matchup).odds
    odds = round(hitter * pitcher / league, 3)
    if 0.269 <= odds <= 0.399:
        return Woba.query.get(odds).runs
    elif odds < 0.269:
        return -0.1
    else:
        return 0.1

def getInnings(pitcher, pvb, bullpen, scheduled, pvb_modifier): 
    '''
    Query Pitchers table by starting pitcher id and 
    return average innings pitched per start. On error
    a default value is returned.
    '''
    try:
        innings = pitcher.ip / scheduled
        return round(((pvb * innings) + (bullpen * (1 - innings))) * pvb_modifier, 2)
    except:
        # ip/gs
        innings = 4.8 / scheduled
        return round(((pvb * innings) + (bullpen * (1 - innings))) * pvb_modifier, 2)

def PvB(pitcher, lineup):
    '''Queries Pitchers and Batters tables by player id and returns run value.'''
    runs = 0
    for hitter in lineup:
        try:
            if hitter.stand == "S" or hitter.stand == "L" and pitcher.p_throws == "R":
                runs += oddsRatio(hitter.woba_r, pitcher.woba_l, 'RL')
            if hitter.stand == "S" or hitter.stand == "R" and pitcher.p_throws == "L":
                runs += oddsRatio(hitter.woba_l, pitcher.woba_r, 'LR')
            if hitter.stand == "L" and pitcher.p_throws == "L":
                runs += oddsRatio(hitter.woba_l, pitcher.woba_l, 'LL')
            if hitter.stand == "R" and pitcher.p_throws == "R":
                runs += oddsRatio(hitter.woba_r, pitcher.woba_r, 'RR')
        except:
            runs += 0
    return round(runs, 2)

def getHandicap(home_team, away_team, innings):
    '''Returns difference between home and away team handicaps'''
    return round((home_team.handicap - away_team.handicap) * (innings/9), 2)

def getBet(bankroll, bet_pct):
    '''Queries Bets table by value and returns bet amount.'''
    return round(bankroll * bet_pct)

def getValue(total, over_threshold, under_threshold, bankroll, bet_pct):
    '''
    Calculates amount of bet value by subtracting over and 
    under thresholds from total (prediction - money line). 
    '''
    if (total < 0 and abs(total) - under_threshold >= 0.01) or (total > 0 and total - over_threshold >= 0.01):
        return getBet(bankroll, bet_pct)
    else:
        return 'No Value'

def getMoneyLine(data):
    '''Calculates over/under lines.'''
    e = 1 + data['currentpriceup'] / data['currentpricedown']
    return round(100 * (e - 1) if e >=2 else -100 / (e - 1))

def filterPitcher(pid, r):
    '''Filters MLB Stats API for in-depth pitcher info.'''
    return r['gameData']['players'][f'ID{pid}']

# Requests data
BASE_URL = "https://statsapi.mlb.com"

def Game(g, fd, modifier, bankroll, bet_pct, pvb_modifier):
    '''
    First, get game data from MLB Stats API and bet data from FanDuel.
    Then, calculate prediction factors. Returns game object.
    '''
    game = {
        "gameData": {
            "gamePk": g.gamePk,
            "game_time": datetime.strptime(g.gameDate, "%Y-%m-%dT%H:%M:%SZ"),
            "link": g.link,
            "double_header": g.doubleHeader,
            "game_number": g.gameNumber,
            "innings": g.scheduledInnings,
            "home_team_full": g.teams.home.team.name,
            "home_team_short": "",
            "home_pitcher": "",
            "home_lineup": [],
            "home_bullpen": [],
            "away_team_full": g.teams.away.team.name,
            "away_team_short": "",
            "away_pitcher": "",
            "away_lineup": [],
            "away_bullpen": [],
            "weather": "",
            "ump": "",
            "hydrate": False
        },
        "betData": {
            'idfoevent': '',
            'idfoselection': '',
            'over_under': "",
            'over_line': "",
            'under_line': "",
            "live_bet": False
        },
        "predData": {
            "park_factor": "",
            "wind_factor": "",
            "temp_factor": "",
            "ump_factor": "",
            "home_fielding": "",
            "home_bullpen": "",
            "home_pvb": "",
            "home_matchups": "",
            "away_fielding": "",
            "away_bullpen": "",
            "away_pvb": "",
            "away_matchups": "",
            "handicap": ""
        },
        "valueData": {
            "prediction": "TBD",
            "total": "TBD",
            "over_120": "",
            "under_120": "",
            "over_100": "",
            "under_100": "",
            "value_120": "TBD",
            "value_100": "TBD" 
        }  
    }

    url = BASE_URL + game["gameData"]['link']
    r = requests.get(url)
    if r.status_code not in [200, 201]:
        r.raise_for_status()

    r = r.json()
    try:
        game["gameData"]['home_team_short'] = r['gameData']['teams']['home']['teamName']
        game["gameData"]['away_team_short'] = r['gameData']['teams']['away']['teamName']
        game["gameData"]['home_pitcher'] = filterPitcher(r['gameData']['probablePitchers']['home']['id'], r)
        game["gameData"]['home_lineup'] = r['liveData']['boxscore']['teams']['home']['battingOrder']
        game["gameData"]['home_bullpen'] = r['liveData']['boxscore']['teams']['home']['bullpen']
        game["gameData"]['away_pitcher'] = filterPitcher(r['gameData']['probablePitchers']['away']['id'], r)
        game["gameData"]['away_lineup'] = r['liveData']['boxscore']['teams']['away']['battingOrder']
        game["gameData"]['away_bullpen'] = r['liveData']['boxscore']['teams']['away']['bullpen']
        game["gameData"]['weather'] = r['gameData']['weather']
        game["gameData"]['ump'] = next(filter(lambda x: x['officialType'] == "Home Plate", r['liveData']['boxscore']['officials']), None)
        game["gameData"]['hydrate'] = True
    except:
        pass

    odds = list(filter(lambda x: x.HomeTeamDetails.FullName == game["gameData"]['home_team_full'] or x.AwayTeamDetails.FullName == game["gameData"]['away_team_full'], fd))

    try:
        game["betData"]['idfoevent'] = odds[0].Consensus.GameId
        game["betData"]['idfoselection'] = odds[0].Consensus.GameOddId
        game["betData"]['over_under'] = odds[0].Consensus.OverUnder
        game["betData"]['over_line'] = odds[0].Consensus.OverPayout
        game["betData"]['under_line'] = odds[0].Consensus.UnderPayout
        game["betData"]['live_bet'] = True
    except:
        pass


    if game["gameData"]['hydrate'] and game["betData"]['live_bet']:
        try:
            home_team = Parks.query.filter_by(park=game["gameData"]['home_team_full']).first()
            home_pitcher = Pitchers.query.filter_by(id=game["gameData"]['home_pitcher']['id']).first()
            home_bullpen = Pitchers.query.filter(Pitchers.id.in_([id for id in game["gameData"]['home_bullpen']])).all()
            home_offense = Batters.query.filter(Batters.id.in_([id for id in game["gameData"]['home_lineup']])).all()
            away_team = Parks.query.filter_by(park=game["gameData"]['away_team_full']).first()
            away_pitcher = Pitchers.query.filter_by(id=game["gameData"]['away_pitcher']['id']).first()
            away_bullpen = Pitchers.query.filter(Pitchers.id.in_([id for id in game["gameData"]['away_bullpen']])).all()
            away_offense = Batters.query.filter(Batters.id.in_([id for id in game["gameData"]['away_lineup']])).all()
            game["predData"]["park_factor"] = round(home_team.runs * modifier, 2)
            game["predData"]['wind_factor'] = getWind(game["gameData"]['home_team_full'], game["gameData"]['weather']['wind'].split(), game["gameData"]['innings'])
            game["predData"]['temp_factor'] = getTemp(int(game["gameData"]['weather']['temp']), game["gameData"]['innings'])
            game["predData"]["ump_factor"] = getUmp(game["gameData"]['ump']['official']['id'], game["gameData"]['innings'])
            game["predData"]['home_fielding'] = getFielding(game["gameData"]['home_lineup'], game["gameData"]['innings'])
            game["predData"]['home_bullpen'] = getBullpen(home_bullpen, away_offense)
            game["predData"]['home_pvb'] = PvB(home_pitcher, away_offense)
            game["predData"]['away_fielding'] = getFielding(game["gameData"]['away_lineup'], game["gameData"]['innings'])
            game["predData"]['away_bullpen'] = getBullpen(away_bullpen, home_offense)
            game["predData"]['away_pvb'] = PvB(away_pitcher, home_offense)
            game["predData"]['home_matchups'] = getInnings(
                home_pitcher, 
                game["predData"]['home_pvb'], 
                game["predData"]['home_bullpen'], 
                game["gameData"]['innings'],
                pvb_modifier
            )
            game["predData"]['away_matchups'] = getInnings(
                away_pitcher, 
                game["predData"]['away_pvb'], 
                game["predData"]['away_bullpen'], 
                game["gameData"]['innings'],
                pvb_modifier
            )
            game["predData"]["handicap"] = getHandicap(home_team, away_team, game["gameData"]['innings'])
            game["valueData"]["prediction"] = round(sum([
                game["predData"]["park_factor"], 
                game["predData"]['wind_factor'], 
                # game["predData"]['temp_factor'], add back in later?
                game["predData"]["ump_factor"], 
                game["predData"]['home_fielding'], 
                game["predData"]['away_fielding'], 
                game["predData"]['home_matchups'], 
                game["predData"]['away_matchups'], 
                game["predData"]["handicap"]
            ]), 2)
            game["valueData"]["total"] = round(game["valueData"]['prediction'] - game["betData"]['over_under'], 2)
            game["valueData"]["over_100"] = round(home_team.over_threshold * (game["gameData"]['innings']/9), 2)
            game["valueData"]["under_100"] = round(home_team.under_threshold * (game["gameData"]['innings']/9), 2)
            game["valueData"]["over_120"] = round(game["valueData"]['over_100'] * 1.2, 2)
            game["valueData"]["under_120"] = round(game["valueData"]['under_100'] * 1.2, 2)
            game["valueData"]["value_120"] = getValue(game["valueData"]['total'], game["valueData"]['over_120'], game["valueData"]['under_120'], bankroll, bet_pct)
            game["valueData"]["value_100"] = getValue(game["valueData"]['total'], game["valueData"]['over_100'], game["valueData"]['under_100'], bankroll, bet_pct)
        except:
            pass
        
    return game
