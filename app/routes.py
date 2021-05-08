from flask import render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from app import app

socketio = SocketIO(app)

umps = pd.read_csv("app/data/umps.csv", index_col='name')
parks = pd.read_csv("app/data/parks.csv", index_col='park')
bets = pd.read_csv("app/data/bets.csv", index_col='total')

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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('game')
def send_data(data):
    game = data['game']
    gamePk = game['gamePk']
    game_time = game['game_time']
    try:
        venue = game['venue']
        ump = game['ump']['official']['fullName']
        temp = int(game['weather']['temp'])
        weather = getTemp(temp)
        prediction = round(parks.loc[venue]['runs'] + umps.loc[ump]['runs'] + weather, 2)

        if game['innings'] == 9:
            total = round(prediction - game['over_under'] - 0.2, 2)
        else:
            total = round((prediction - game['over_under'] - 0.2) * (7/9), 2)

        if total >= 0.6 or total <= -0.6:
            bet = bets.loc[total]['bet']
        else:
            bet = "No bet"

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': prediction, 'total': total, 'bet': bet})
    except:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'prediction': "TBD", 'total': "TBD", 'bet': "TBD"})

if __name__ == '__main__':
    socketio.run(app)