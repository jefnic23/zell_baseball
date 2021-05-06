from flask import render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from app import app

umps = pd.read_csv("app/data/umps.csv")
parks = pd.read_csv("app/data/parks.csv")
bets = pd.read_csv("app/data/bets.csv", index_col='total')

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('game')
def send_data(data):
    gamePk = data['game']['gamePk']
    game_time = data['game']['game_time']
    try:
        venue = data['game']['venue']
        ump = data['game']['ump']['official']['fullName']

        prediction = round(parks[parks['park'] == venue]['runs'].values[0] + umps[umps['name'] == ump]['runs'].values[0], 2)

        if data['game']['innings'] == 9:
            total = round(prediction - data['game']['over_under'], 2)
        else:
            total = round((prediction - data['game']['over_under']) * (7/9), 2)

        if total >= 0.5 or total <= -0.5:
            bet = bets.loc[total]['bet']
        else:
            bet = "No bet"
        emit('predictionData', {'gamePk': gamePk, 'game_time': game_time, 'prediction': prediction, 'total': total, 'bet': bet})
    except:
        emit('predictionData', {'gamePk': gamePk, 'game_time': game_time, 'prediction': "TBD", 'total': "TBD", 'bet': "TBD"})

if __name__ == '__main__':
    socketio.run(app)