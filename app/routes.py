from flask import render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor
from statistics import mean
import json, pickle

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
batters = pd.read_csv('app/data/batters.csv', index_col='batter')
matchups = pd.read_csv('app/data/matchups.csv', index_col='matchup')
hev = pd.read_csv('app/data/hev.csv', index_col='hev')

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
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "In":
        for i in range(0, speed - 10 + 1):
            wind -= 0.20
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "Out":
        for i in range(0, speed - 10 + 1):
            wind += 0.20
    return round(wind * (innings/9), 2)

def getUmp(ump, innings):
    runs = 0
    try:
        runs += umps.loc[ump]['runs']
    except: 
        runs += 0
    return round(runs * (innings/9), 2)

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
    h = (hitter/100) / (1 - (hitter/100))
    p = (pitcher/100) / (1 - (pitcher/100))
    l = matchups.loc[matchup]['odds']
    odds = h * p / l
    rate = round(odds / (odds + 1), 3)
    if 0.657 <= rate <= 0.824:
        return round(hev.loc[rate]['runs'], 2)
    else:
        if rate < 0.657:
            return -0.15
        if rate > 0.824:
            return 0.15

def getInnings(pitcher, pvb, bullpen, scheduled): 
    p_id = pitcher['id']
    try:
        innings = pitchers.loc[p_id]['ip'] / scheduled
        return round((pvb * innings) + (bullpen * (1 - innings)), 2)
    except:
        innings = pitchers['ip'].median() / scheduled
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
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['hev_L']
                b_runs = batters[batters['stand'] == "L"].loc[b_id]['hev_R']
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "S" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['hev_R']
                b_runs = batters[batters['stand'] == "R"].loc[b_id]['hev_L']
                runs += oddsRatio(b_runs, p_runs, 'LR')
            if b_hand == "L" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['hev_L']
                b_runs = batters[batters['stand'] == "L"].loc[b_id]['hev_L']
                runs += oddsRatio(b_runs, p_runs, 'LL')
            if b_hand == "L" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['hev_L']
                b_runs = batters[batters['stand'] == "L"].loc[b_id]['hev_R']
                runs += oddsRatio(b_runs, p_runs, 'RL')
            if b_hand == "R" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['hev_R']
                b_runs = batters[batters['stand'] == "R"].loc[b_id]['hev_R']
                runs += oddsRatio(b_runs, p_runs, 'RR')
            if b_hand == "R" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['hev_R']
                b_runs = batters[batters['stand'] == "R"].loc[b_id]['hev_L']
                runs += oddsRatio(b_runs, p_runs, 'LR')
        except:
            runs += 0
    return round(runs, 2)

def getHandicap(away_team, home_team, innings):
    handicap = parks.loc[home_team]['handicap'] - parks.loc[away_team]['handicap']
    return round(handicap * (innings/9), 2)

def getValue(total, over_threshold, under_threshold):
    bet = 'No Value'
    if total < 0 and abs(total) - under_threshold >= 0.01:
        value = round(abs(total) - under_threshold, 2)
        bet = int(bets.loc[value]['bet'])
    if total > 0 and total - over_threshold >= 0.01:
        value = round(abs(total) - over_threshold, 2)
        bet = int(bets.loc[value]['bet'])
    return bet

'''
model predictions
'''

defense = pd.read_csv('app/data/outs_above_average.csv', index_col='player_id')

reg_under_thresholds = pd.read_csv('app/data/reg_under_thresholds.csv', index_col='park')
reg_over_thresholds = pd.read_csv('app/data/reg_over_thresholds.csv', index_col='park')
reg_model = XGBRegressor()
reg_model.load_model('app/data/reg_model.txt')

wind_map = {' None': 0,
            ' R To L': 1,
            ' Varies': 2,
            ' Out To RF': 3,
            ' Out To CF': 4,
            ' L To R': 5,
            ' In From RF': 6,
            ' In From CF': 7,
            ' Out To LF': 8,
            ' In From LF': 9,
            ' Calm': 10
            }

condition_map = {'Dome': 0,
                 'Partly Cloudy': 1,
                 'Sunny': 2,
                 'Roof Closed': 3,
                 'Overcast': 4,
                 'Cloudy': 5,
                 'Clear': 6,
                 'Snow': 7,
                 'Drizzle': 8,
                 'Rain': 9
                 }

def pitcherHEV(pitcher):
    try:
        return pitchers.loc[pitcher]['wHEV']
    except:
        return pitchers['wHEV'].quantile(0.33)

def starterInnings(pitcher):
    innings = 5.1
    try:
        innings = pitchers.loc[pitcher]['ip']
        return round(innings,1)
    except:
        return innings

def batterHEV(lineup):
    hev = []
    osw = []
    for batter in lineup:
        try:
            b = batters.loc[batter]
            hev.append(b['wHEV'])
            osw.append(b['oswing'])
        except:
            hev.append(batters['wHEV'].quantile(0.33))
            osw.append(batters['oswing'].quantile(0.33))
    return round(mean(hev), 2), round(mean(osw), 2)

def getRelievers(bullpen):
    runs = []
    for player in bullpen:
        try:
            runs.append(pitchers.loc[player['id']]['wHEV'])
        except:
            runs.append(pitchers['wHEV'].quantile(0.33))
    return round(sum(runs)/len(runs), 2)

def getDefense(lineup):
    runs = 0
    for player in lineup:
        try:
            runs += defense.loc[player['id']]['outs_above_average']
        except:
            runs += 0
    return runs

def modelPred(game):
    d = {'innings': game['innings'],
         'park': game['park'],
         'ump': umps.loc[game['ump']['official']['id']]['ratio'].round(2),
         'sp_hev': pitcherHEV(game['away_pitcher']['id']) + pitcherHEV(game['home_pitcher']['id']),
         'sp_innings': starterInnings(game['away_pitcher']['id']) + starterInnings(game['home_pitcher']['id']),
         'offense_hev': batterHEV(game['away_lineup'])[0] + batterHEV(game['home_lineup'])[0],
         'offense_osw': batterHEV(game['away_lineup'])[1] + batterHEV(game['home_lineup'])[1],
         'defense': getDefense(game['away_lineup']) + getDefense(game['home_lineup']),
         'bullpens': getRelievers(game['away_bullpen']) + getRelievers(game['home_bullpen']),
         'CloseOU': game['over_under'] 
         }
    df = pd.DataFrame(d, columns=d.keys(), index=[0])
    X = df.loc[:,'park':'CloseOU']
    pred = reg_model.predict(X)
    if game['innings'] == 7:
        return float(pred * (7/9))
    else:
        return float(pred)

def modelData(park, pred, line):
    try:
        o = reg_over_thresholds.loc[park]['threshold']
        o_pct = reg_over_thresholds.loc[park]['pct']
        u = reg_under_thresholds.loc[park]['threshold']
        u_pct = reg_under_thresholds.loc[park]['pct']
        total = round(pred - line, 2)
        larry = [o, u, o_pct, u_pct, total]
    except:
        larry = None

    return larry

'''
sockets
'''

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
    starters = {'away': "TBA", 'home': "TBA"}
    if game['away_lineup'] and game['home_lineup'] and game['away_pitcher'] and game['home_pitcher']:
        starters['away'] = game['away_pitcher']['boxscoreName']
        starters['home'] = game['home_pitcher']['boxscoreName']
        innings = game['innings']
        wind_data = game['weather']['wind'].split()
        speed = int(wind_data[0])
        direction = wind_data[2]
        wind = getWind(game, speed, direction, innings)
        line = abs(over_line) + abs(under_line)
        venue = round(parks.loc[game['venue']]['runs'] * (innings/9), 2)
        handicap = getHandicap(game['away_team_full'], game['home_team_full'], innings)
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
        prediction = (1.03 * venue) + (0.25 * (over_under - venue)) + handicap + ump + away_fielding + home_fielding + weather + away_matchups + home_matchups + wind
        pred_data = [venue, handicap, weather, wind, ump, home_fielding, away_fielding, away_matchups, home_matchups]
        model_pred = modelPred(game)
        model_data = modelData(game['park'], model_pred, over_under)

        if line == 220:
            adj_line = round(over_under + lines_20.loc[over_line]['mod'], 2)
        else:
            try:
                adj_line = round(over_under + lines_22.loc[over_line]['mod'], 2)
            except:
                adj_line = -0.25

        total = round(prediction - over_under, 2)
        adj_total = round(prediction - adj_line, 2)
        bet = getValue(total, over_threshold, under_threshold)

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': pred_data, 'pitchers': starters, 'wind_speed': speed, 'wind_direction': direction, 'wind': wind, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'prediction': round(prediction, 2), 'total': total, 'adj_line': adj_line, 'bet': bet, 'larry_pred': round(model_pred, 2), 'larry_data': model_data})
    else:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': None, 'pitchers': starters, 'wind_speed': None, 'wind_direction': None, 'wind': None, 'over_threshold': None, 'under_threshold': None, 'prediction': "TBD", 'total': "TBD", 'adj_line': 'TBD', 'bet': "TBD", 'larry_pred': "TBD", 'larry_data': None})

@socketio.on('changeLine')
def change_line(data):
    ids = data['ids']
    larry = data['larry']
    prediction = data['prediction']
    over_threshold = data['over_threshold']
    under_threshold = data['under_threshold']
    over_under = data['over_under']
    over = data['over']
    under = data['under']
    game = data['game']
    game['over_under'] = over_under
    try:
        model_pred = modelPred(game)
        model_data = modelData(game['park'], model_pred, over_under)

        line = abs(over) + abs(under)
        if line == 220:
            adj_line = round(over_under + lines_20.loc[over]['mod'], 2)
        else: 
            try:
                adj_line = round(over_under + lines_22.loc[over]['mod'], 2)
            except:
                adj_line = -0.25

        total = round(prediction - over_under, 2)
        adj_total = round(prediction - adj_line, 2)
        bet = getValue(total, over_threshold, under_threshold)

        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'adj_line': adj_line, 'new_total': total, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'bet': bet, "ids": ids})
    except:
        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'adj_line': 'TBD', 'new_total': 'TBD', 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'bet': 'TBD', "ids": ids})

if __name__ == '__main__':
    socketio.run(app)