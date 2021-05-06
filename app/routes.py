from flask import render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from app import app

umps = pd.read_csv("app/data/umps.csv", index_col="name")
parks = pd.read_csv("app/data/parks.csv", index_col="park")
bets = pd.read_csv("app/data/bets.csv", index_col='total')

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('game')
def send_data(data):
    gamePk = data['game']['gamePk']
    try:
        venue = data['game']['venue']
        ump = data['game']['ump']['official']['fullName']
        temp = data['game']['weather']['temp']
        if temp <= 46:
            weather = -0.225
        elif 47 <= temp <= 53:
            weather = -0.15
        elif 54 <= temp <= 62:
            weather = -0.075
        elif 63 <= temp <= 71:
            weather = 0.0
        elif 72 <= temp <= 79:
            weather = 0.1
        elif 80 <= temp <= 87:
            weather = 0.2
        elif temp >= 88:
            weather = 0.3
        
        prediction = round(parks.loc[venue]['runs'] + umps.loc[ump]['runs'] + weather, 2)
        if data['game']['innings'] == 9:
            total = round(prediction - data['game']['over_under'], 2)
        else:
            total = round((prediction - data['game']['over_under']) * (7/9), 2)

        if total >= 0.5 or total <= -0.5:
            bet = bets.loc[total]['bet']
        else:
            bet = "No bet"
        emit('predictionData', {'gamePk': gamePk, 'prediction': prediction, 'total': total, 'bet': bet})
    except:
        emit('predictionData', {'gamePk': gamePk, 'prediction': "TBD", 'total': "TBD", 'bet': "TBD"})

if __name__ == '__main__':
    socketio.run(app)