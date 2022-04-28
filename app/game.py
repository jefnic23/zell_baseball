from app.models import *

def getTemp(temp, innings):
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
    wind = 0
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "In":
        for _ in range(0, speed - 10 + 1):
            wind -= 0.15
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "Out":
        for _ in range(0, speed - 10 + 1):
            wind += 0.15
    return round(wind * (innings/9), 2)

def getUmp(ump, innings):
    try:
        runs = Umps.query.filter_by(id=ump).first().runs
        # runs = umps.loc[ump]['runs']
    except:
        runs = 0
    return round(runs * (innings/9), 2)

def getFielding(lineup, innings):
    runs = 0
    players = [id["id"] for id in lineup]
    for player in players:
        try:
            runs += Fielding.query.filter_by(id=player).first().runs
            # runs += fielding.loc[player]['runs']
        except:
            runs += 0
    return round(runs * (innings/9), 2)

def getBullpen(bullpen):
    runs = 0
    players = [id['id'] for id in bullpen]
    for player in players:
        try:
            runs += Bullpens.query.filter_by(id=player).first().runs
            # runs += bullpens.loc[player]['runs']
        except:
            runs += 0
    return round(runs, 2)

def oddsRatio(hitter, pitcher, matchup):
    h = (hitter/100) / (1 - (hitter/100))
    p = (pitcher/100) / (1 - (pitcher/100))
    l = Matchups.query.get(matchup).odds
    # l = matchups.loc[matchup]['odds']
    odds = h * p / l
    rate = round(odds / (odds + 1), 3)
    if 0.657 <= rate <= 0.824:
        return Hev.query.get(rate).runs
        # return round(hev.loc[rate]['runs'], 2)
    else:
        if rate < 0.657:
            return -0.15
        if rate > 0.824:
            return 0.15

def getInnings(pitcher, pvb, bullpen, scheduled): 
    p_id = pitcher['id']
    try:
        innings = Pitchers.query.filter_by(id=p_id).first().ip / scheduled
        # innings = pitchers.loc[p_id]['ip'] / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)
    except:
        # ip/gs
        innings = 4.8 / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)

def PvB(pitcher, lineup):
    runs = 0
    p_id = pitcher['id']
    p_hand = pitcher['pitchHand']['code']
    p = Pitchers.query.filter_by(id=p_id).first()
    for hitter in lineup:
        try:
            b_id = hitter['id']
            b_hand = hitter['batSide']['code']
            b = Batters.query.filter_by(id=b_id).first()
            if b_hand == "S" and p_hand == "R":
                p_runs = p.hev_l
                b_runs = b.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "S" and p_hand == "L":
                p_runs = p.hev_r
                b_runs = b.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LR')
            if b_hand == "L" and p_hand == "L":
                p_runs = p.hev_l
                b_runs = b.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LL')
            if b_hand == "L" and p_hand == "R":
                p_runs = p.hev_l
                b_runs = b.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "R" and p_hand == "R":
                p_runs = p.hev_r
                b_runs = b.hev_r
                runs += oddsRatio(b_runs, p_runs, 'RR')
            if b_hand == "R" and p_hand == "L":
                p_runs = p.hev_r
                b_runs = b.hev_l
                runs += oddsRatio(b_runs, p_runs, 'LR')
        except:
            runs += 0
    return round(runs, 2)

def getHandicap(away_team, home_team, innings):
    handicap = home_team.handicap - away_team.handicap
    # handicap = parks.loc[home_team]['handicap'] - parks.loc[away_team]['handicap']
    return round(handicap * (innings/9), 2)

def getValue(total, over_threshold, under_threshold):
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
