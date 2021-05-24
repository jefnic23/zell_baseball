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

def getTemp(temp):
    if temp <= 46:
        return -0.225
    if 47 <= temp <= 53:
        return -0.15
    if 54 <= temp <= 62:
        return -0.075
    if 63 <= temp <= 71:
        return 0.0
    if 72 <= temp <= 79:
        return 0.1
    if 80 <= temp <= 87:
        return 0.2
    if temp >= 88:
        return 0.3

def getUmp(ump):
    runs = 0
    try:
        runs += umps.loc[ump]['runs']
    except: 
        runs += 0
    return runs

def getFielding(lineup):
    runs = 0
    players = [id["id"] for id in lineup]
    for player in players:
        try:
            runs += fielding.loc[player]['outs']
        except:
            runs += 0
    return runs

def getBullpen(bullpen):
    runs = 0
    players = [id['id'] for id in bullpen]
    for player in players:
        try:
            runs += bullpens.loc[player]['runs']
        except:
            runs += 0
    return runs

def PvB(pitcher, lineup):
    runs = 0
    p_id = pitcher['id']
    p_hand = pitcher['pitchHand']['code']
    for hitter in lineup:
        try:
            b_id = hitter['id']
            b_hand = hitter['batSide']['code']
            if b_hand == "S" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['runs_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['runs_R']
                runs += p_runs + b_runs
            if b_hand == "S" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['runs_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['runs_L']
                runs += p_runs + b_runs
            if b_hand == "L" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['runs_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['runs_L']
                runs += p_runs + b_runs
            if b_hand == "L" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['runs_L']
                b_runs = hitters[hitters['stand'] == "L"].loc[b_id]['runs_R']
                runs += p_runs + b_runs
            if b_hand == "R" and p_hand == "R":
                p_runs = pitchers[pitchers['p_throws'] == "R"].loc[p_id]['runs_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['runs_R']
                runs += p_runs + b_runs
            if b_hand == "R" and p_hand == "L":
                p_runs = pitchers[pitchers['p_throws'] == "L"].loc[p_id]['runs_R']
                b_runs = hitters[hitters['stand'] == "R"].loc[b_id]['runs_L']
                runs += p_runs + b_runs
        except:
            runs += 0
    return runs

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
    if game['away_lineup'] and game['home_lineup']:
        line = abs(over_line) + abs(under_line)
        venue = parks.loc[game['venue']]['runs']
        ump = getUmp(game['ump']['official']['id'])
        weather = getTemp(int(game['weather']['temp']))
        away_fielding = getFielding(game['away_lineup'])
        home_fielding = getFielding(game['home_lineup'])
        away_bullpen = getBullpen(game['away_bullpen'])
        home_bullpen = getBullpen(game['home_bullpen'])

        # PvB testing
        away_pvb = PvB(game['away_pitcher'], game['home_lineup'])
        home_pvb = PvB(game['home_pitcher'], game['away_lineup'])
        pvb = away_pvb + home_pvb + 0.17913259581679686
        print(f"\n{game['away_team_short']}: {pvb}\n")

        prediction = round(venue + ump + away_fielding + home_fielding + weather + away_bullpen + home_bullpen + pvb, 2)
        if game['innings'] == 7:
            prediction = round(prediction * (7/9), 2)

        if line == 220:
            adj_line = round(over_under + lines_20.loc[over_line]['mod'], 2)
        else:
            adj_line = round(over_under + lines_22.loc[over_line]['mod'], 2)
        
        total = round(prediction - adj_line - 0.3, 2)
        if total >= .5 or total <= -.5:
            bet = bets.loc[abs(total)]['bet']
        else:
            bet = "No Value"

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': prediction, 'total': total, 'adj_line': adj_line, 'bet': bet})
    else:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': "TBD", 'total': "TBD", 'adj_line': 'TBD', 'bet': "TBD"})

@socketio.on('changeLine')
def change_line(data):
    ids = data['ids']
    prediction = data['prediction']
    over_under = data['over_under']
    over = data['over']
    under = data['under']
    try:
        line = abs(over) + abs(under)
        if line == 220:
            adj_line = round(over_under + lines_20.loc[over]['mod'], 2)
        else: 
            adj_line = round(over_under + lines_22.loc[over]['mod'], 2)

        new_total = round(prediction - adj_line - 0.3, 2)
        if new_total >= .5 or new_total <= -.5:
            bet = bets.loc[abs(new_total)]['bet']
        else:
            bet = "No Value"

        emit('lineChange', {'over_under': over_under, 'adj_line': adj_line, 'new_total': new_total, 'bet': bet, "ids": ids})
    except:
        emit('lineChange', {'over_under': over_under, 'adj_line': 'TBD', 'new_total': 'TBD', 'bet': 'TBD', "ids": ids})

if __name__ == '__main__':
    socketio.run(app)