from flask import render_template
from flask_socketio import SocketIO, emit
import pandas as pd
from app import app

umps = pd.read_csv("app/data/umps.csv")
parks = pd.read_csv("app/data/parks.csv")

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
        prediction = parks[parks['park'] == venue]['runs'].values[0] + umps[umps['name'] == ump]['runs'].values[0]
        emit('predictionData', {'gamePk': gamePk, 'prediction': prediction})
    except:
        emit('predictionData', {'gamePk': gamePk, 'prediction': "TBD"})

if __name__ == '__main__':
    socketio.run(app)