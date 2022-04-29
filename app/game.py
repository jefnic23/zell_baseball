import requests
from app.models import *


def getTemp(temp, innings):
    '''Get run value based on game time temperature.'''
    if temp <= 46:
        return round(-0.225 * (innings/9), 2)
    if 47 <= temp <= 53:
        return round(-0.15 * (innings/9), 2)
    if 54 <= temp <= 62:
        return round(-0.075 * (innings/9), 2)
    if 63 <= temp <= 71:
        return 0.0
    if 72 <= temp <= 79:
        return round(0.1 * (innings/9), 2)
    if 80 <= temp <= 87:
        return round(0.2 * (innings/9), 2)
    if temp >= 88:
        return round(0.3 * (innings/9), 2)

def getWind(game, speed, direction, innings):
    '''
    Get run value based on game time wind speed and direction.
    Only applies to Wrigley Field.
    '''
    wind = 0
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "In":
        for _ in range(0, speed - 10 + 1):
            wind -= 0.15
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "Out":
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
    players = Fielding.query.filter(Fielding.id.in_([id["id"] for id in lineup])).all()
    for player in players:
        try:
            runs += player.runs
        except:
            runs += 0
    return round(runs * (innings/9), 2)

def getBullpen(bullpen):
    '''Query Bullpen table by player id and return team bullpen run value.'''
    runs = 0
    players = Bullpens.query.filter(Bullpens.id.in_([id["id"] for id in bullpen])).all()
    for player in players:
        try:
            runs += player.runs
        except:
            runs += 0
    return round(runs, 2)

def oddsRatio(hitter, pitcher, matchup):
    '''
    Calculate odds ratio of a batter/pitcher matchup.
    Query Matchups table by odds ratio and return run value.
    '''
    h = (hitter/100) / (1 - (hitter/100))
    p = (pitcher/100) / (1 - (pitcher/100))
    l = Matchups.query.get(matchup).odds
    odds = h * p / l
    rate = round(odds / (odds + 1), 3)
    if 0.657 <= rate <= 0.824:
        return Hev.query.get(rate).runs
    else:
        if rate < 0.657:
            return -0.15
        if rate > 0.824:
            return 0.15

def getInnings(pitcher, pvb, bullpen, scheduled): 
    '''
    Query Pitchers table by starting pitcher id and 
    return average innings pitched per start. On error
    a default value is returned.
    '''
    p_id = pitcher['id']
    try:
        innings = Pitchers.query.filter_by(id=p_id).first().ip / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)
    except:
        # ip/gs
        innings = 4.8 / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)

def PvB(pitcher, lineup):
    '''Queries Pitchers and Batters tables by player id and returns run value.'''
    runs = 0
    p_id = pitcher['id']
    p_hand = pitcher['pitchHand']['code']
    p = Pitchers.query.filter_by(id=p_id).first()
    hitters = Batters.query.filter(Batters.id.in_([id["id"] for id in lineup])).all()
    for hitter in hitters:
        try:
            if hitter.stand == "S" and p_hand == "R":
                p_runs = p.hev_l
                b_runs = hitter.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if hitter.stand == "S" and p_hand == "L":
                p_runs = p.hev_r
                b_runs = hitter.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LR')
            if hitter.stand == "L" and p_hand == "L":
                p_runs = p.hev_l
                b_runs = hitter.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LL')
            if hitter.stand == "L" and p_hand == "R":
                p_runs = p.hev_l
                b_runs = hitter.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if hitter.stand == "R" and p_hand == "R":
                p_runs = p.hev_r
                b_runs = hitter.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RR')
            if hitter.stand == "R" and p_hand == "L":
                p_runs = p.hev_r
                b_runs = hitter.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LR')
        except:
            runs += 0
    return round(runs, 2)

def getHandicap(away_team, home_team, innings):
    '''Returns difference between home and away team handicaps'''
    handicap = home_team.handicap - away_team.handicap
    return round(handicap * (innings/9), 2)

def getValue(total, over_threshold, under_threshold):
    '''
    Queries Bets table by the difference of predicted score and
    betting threshold and returns the amount to bet.
    '''
    bet = 'No Value'
    if total < 0 and abs(total) - under_threshold >= 0.01:
        value = round(abs(total) - under_threshold, 2)
        try:
            bet = int(Bets.query.get(value).bet)
        except:
            bet = 1230
    if total > 0 and total - over_threshold >= 0.01:
        value = round(abs(total) - over_threshold, 2)
        try:
            bet = int(Bets.query.get(value).bet)
        except:
            bet = 1230
    return bet

def schedule(date):
    '''Returns scheduled games'''
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=${date}&hydrate=lineups"
    r = requests.get(url)
    if r.status_code not in [200, 201]:
        r.raise_for_status()
    else:
        return r.json()

# def games(schedule):
#     g = []
#     for game in schedule['dates'][0]['games']:
#         if game['status']['abstractGameCode'] == "P":
