from flask import render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from app import app

socketio = SocketIO(app)

umps = pd.read_csv("app/data/umps.csv", index_col='name')
parks = pd.read_csv("app/data/parks.csv", index_col='park')
bets = pd.read_csv("app/data/bets.csv", index_col='total')
fielding = pd.read_csv("app/data/fielding.csv", index_col="player")
bullpens = pd.read_csv("app/data/bullpens.csv", index_col='pitcher')

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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('game')
def send_data(data):
    game = data['game']
    gamePk = game['gamePk']
    game_time = game['game_time']
    away_lineup = game['away_lineup']
    home_lineup = game['home_lineup']
    try:
        venue = game['venue']
        ump = game['ump']['official']['fullName']
        temp = int(game['weather']['temp'])
        weather = getTemp(temp)
        away_fielding = getFielding(away_lineup)
        home_fielding = getFielding(home_lineup)
        away_bullpen = getBullpen(game['away_bullpen'])
        home_bullpen = getBullpen(game['home_bullpen'])
        # change below to fielding to check totals, should be between -0.2 & 0.2
        print(f"\n\n{game['home_team_short']} fielding total: {away_bullpen + home_bullpen}\n\n")
        prediction = round(parks.loc[venue]['runs'] + umps.loc[ump]['runs'] + away_fielding + home_fielding + weather + away_bullpen + home_bullpen, 2)

        if game['innings'] == 7:
            prediction = round(prediction * (7/9), 2)
        
        total = round(prediction - game['over_under'] - 0.25, 2)
        if total >= 0.75 or total <= -0.75:
            bet = bets.loc[abs(total)]['bet']
        else:
            bet = "No bet"

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': prediction, 'total': total, 'bet': bet})
    except:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': "TBD", 'total': "TBD", 'bet': "TBD"})

if __name__ == '__main__':
    socketio.run(app)