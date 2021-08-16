from flask import render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
import pandas as pd
from app import app

Payload.max_decode_packets = 500
socketio = SocketIO(app)

umps = pd.read_csv("app/data/umps.csv", index_col='id')
parks = pd.read_csv("app/data/parks.csv", index_col='park')
bets = pd.read_csv("app/data/bets.csv", index_col='total')
lines_20 = pd.read_csv("app/data/lines_20.csv", index_col='line')
lines_22 = pd.read_csv("app/data/lines_22.csv", index_col='line')
fielding = pd.read_csv("app/data/fielding.csv", index_col="player")
bullpens = pd.read_csv("app/data/bullpens.csv", index_col='pitcher')
pitchers = pd.read_csv("app/data/pitchers.csv", index_col='pitcher')
hitters = pd.read_csv('app/data/hitters.csv', index_col='batter')
matchups = pd.read_csv('app/data/matchups.csv', index_col='matchup')
woba = pd.read_csv('app/data/woba.csv', index_col='woba')

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
        return round(0. * (innings/9), 2)
    if temp >= 88:
        return round(0.3 * (innings/9), 2)

def getWind(game, speed, direction, innings):
    wind = 0
    if game['venue'] == "Wrigley Field" and speed >= 10 and direction == "In":
        for i in range(0, speed - 10 + 1):
            wind -= 0.20
    if game['venue'] == "Wrigley Field" and speed >= 10 and direction == "Out":
        for i in range(0, speed - 10 + 1):
            wind += 0.20
    return round(wind * (innings/9), 2)

def getUmp(ump, innings):
    runs = 0
    try:
        runs += umps.loc[ump]['runs']
    except: 
        runs += 0
    return round(runs * 1.6 * (innings/9), 2)

def getFielding(lineup, innings):
    runs = 0
    players = [id["id"] for id in lineup]
    for player in players:
        try:
            runs += fielding.loc[player]['outs']
        except:
            runs += 0
    return round(runs * (innings/9), 2)

def getBullpen(bullpen):
    runs = 0
    players = [id['id'] for id in bullpen]
    for player in players:
        try:
            runs += bullpens.loc[player]['runs']
        except:
            runs += 0
    return round(runs, 2)

def oddsRatio(hitter, pitcher, matchup):
    h = hitter / (1 - hitter)
    p = pitcher / (1 - hitter)
    l = matchups.loc[matchup]['odds']
    odds = h * p / l
    rate = round(odds / (odds + 1), 3)
    if 0.290 <= rate <= 0.400:
        return round(woba.loc[rate]['runs'], 2)
    else:
        if rate < 0.290:
            return -0.15
        if rate > 0.400:
            return 0.1825

def getInnings(pitcher, pvb, bullpen, scheduled): 
    p_id = pitcher['id']
    try:
        innings = pitchers.loc[p_id]['innings'] / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)
    except:
        innings = pitchers['innings'].median() / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)

def PvB(pitcher, lineup):
    runs = 0
    p_id = pitcher['id']
    p_hand = pitcher['pitchHand']['code']
    for hitter in lineup:
        try:
            b_id = hitter['id']
            b_hand = hitter['batSide']['code']
            if b_hand == "S" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['woba_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['woba_R']
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "S" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['woba_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['woba_L']
                runs += oddsRatio(b_runs, p_runs, 'LR')
            if b_hand == "L" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['woba_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['woba_L']
                runs += oddsRatio(b_runs, p_runs, 'LL')
            if b_hand == "L" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['woba_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['woba_R']
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "R" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['woba_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['woba_R']
                runs += oddsRatio(b_runs, p_runs, 'RR')
            if b_hand == "R" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['woba_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['woba_L']
                runs += oddsRatio(b_runs, p_runs, 'LR')
        except:
            runs += 0
    return round(runs, 2)

def getHandicap(away_team, home_team):
    handicap = parks.loc[away_team]['handicap'] - parks.loc[away_team]['handicap']
    return round(handicap, 2)

def getValue(total, over_threshold, under_threshold):
    bet = 'No Value'
    if total < 0 and abs(total) - under_threshold >= 0.01:
        value = round(abs(total) - under_threshold, 2)
        bet = int(bets.loc[value]['bet'])
    if total > 0 and total - over_threshold >= 0.01:
        value = round(abs(total) - over_threshold, 2)
        bet = int(bets.loc[value]['bet'])
    return bet

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('game')
def send_data(data):
    game = data['game']
    gamePk = game['gamePk']
    game_time = game['game_time']
    over_under = game['over_under']
    over_line = game['over_line']
    under_line = game['under_line']
    if game['away_lineup'] and game['home_lineup'] and game['away_pitcher'] and game['home_pitcher']:
        innings = game['innings']
        wind_data = game['weather']['wind'].split()
        speed = int(wind_data[0])
        direction = wind_data[2]
        wind = getWind(game, speed, direction, innings)
        line = abs(over_line) + abs(under_line)
        venue = round(parks.loc[game['venue']]['runs'] * (innings/9), 2)
        handicap = getHandicap(game['away_team_full'], game['home_team_full'])
        over_threshold = round(parks.loc[game['venue']]['over_threshold'] * (innings/9), 2)
        under_threshold = round(parks.loc[game['venue']]['under_threshold'] * (innings/9), 2)
        ump = getUmp(game['ump']['official']['id'], innings)
        weather = getTemp(int(game['weather']['temp']), innings)
        away_fielding = getFielding(game['away_lineup'], innings)
        home_fielding = getFielding(game['home_lineup'], innings)
        away_bullpen = getBullpen(game['away_bullpen'])
        home_bullpen = getBullpen(game['home_bullpen'])
        away_pvb = PvB(game['away_pitcher'], game['home_lineup'])
        home_pvb = PvB(game['home_pitcher'], game['away_lineup'])
        away_matchups = getInnings(game['away_pitcher'], away_pvb, away_bullpen, innings)
        home_matchups = getInnings(game['home_pitcher'], home_pvb, home_bullpen, innings) 
        prediction = (venue + handicap + ump + away_fielding + home_fielding + weather + away_matchups + home_matchups + wind) * 1.077
        pred_data = [venue, handicap, weather, wind, ump, away_fielding, home_fielding, away_matchups, home_matchups]

        if line == 220:
            adj_line = round(over_under + lines_20.loc[over_line]['mod'], 2)
        else:
            adj_line = round(over_under + lines_22.loc[over_line]['mod'], 2)
        
        total = round(prediction - over_under, 2)
        adj_total = round(prediction - adj_line, 2)
        bet = getValue(total, over_threshold, under_threshold)

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': pred_data, 'wind_speed': speed, 'wind_direction': direction, 'wind': wind, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'prediction': round(prediction, 2), 'total': total, 'adj_line': adj_line, 'bet': bet})
    else:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': None, 'wind_speed': None, 'wind_direction': None, 'wind': None, 'over_threshold': None, 'under_threshold': None, 'prediction': "TBD", 'total': "TBD", 'adj_line': 'TBD', 'bet': "TBD"})

@socketio.on('changeLine')
def change_line(data):
    ids = data['ids']
    prediction = data['prediction']
    over_threshold = data['over_threshold']
    under_threshold = data['under_threshold']
    over_under = data['over_under']
    over = data['over']
    under = data['under']
    try:
        line = abs(over) + abs(under)
        if line == 220:
            adj_line = round(over_under + lines_20.loc[over]['mod'], 2)
        else: 
            adj_line = round(over_under + lines_22.loc[over]['mod'], 2)

        total = round(prediction - over_under, 2)
        adj_total = round(prediction - adj_line, 2)
        bet = getValue(total, over_threshold, under_threshold)

        emit('lineChange', {'over_under': over_under, 'adj_line': adj_line, 'new_total': total, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'bet': bet, "ids": ids})
    except:
        emit('lineChange', {'over_under': over_under, 'adj_line': 'TBD', 'new_total': 'TBD', 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'bet': 'TBD', "ids": ids})

if __name__ == '__main__':
    socketio.run(app)