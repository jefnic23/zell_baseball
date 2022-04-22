from flask import render_template, redirect, url_for, flash
from flask_socketio import emit
from flask_login import login_user, current_user, logout_user
from engineio.payload import Payload
from app.forms import *
from app.models import *
from app.views import *
from app.email import *
from app import app, login, socketio, admin

Payload.max_decode_packets = 50
login.init_app(app)
admin.add_link(LogoutView(name='Logout', endpoint='logout'))
admin.add_view(DataView(Batters, db.session))
admin.add_view(DataView(Bets, db.session))
admin.add_view(DataView(Bullpens, db.session))
admin.add_view(DataView(Fielding, db.session))
admin.add_view(DataView(HEV, db.session))
admin.add_view(DataView(Matchups, db.session))
admin.add_view(DataView(Parks, db.session))
admin.add_view(DataView(Pitchers, db.session))
admin.add_view(DataView(Umps, db.session))

import pandas as pd
umps = pd.read_sql_table("umps", app.config['SQLALCHEMY_DATABASE_URI'], index_col='id')
parks = pd.read_sql_table("parks", app.config['SQLALCHEMY_DATABASE_URI'], index_col='park')
bets = pd.read_sql_table("bets", app.config['SQLALCHEMY_DATABASE_URI'], index_col='total')
fielding = pd.read_sql_table("fielding", app.config['SQLALCHEMY_DATABASE_URI'], index_col="id")
bullpens = pd.read_sql_table("bullpens", app.config['SQLALCHEMY_DATABASE_URI'], index_col='id')
pitchers = pd.read_sql_table("pitchers", app.config['SQLALCHEMY_DATABASE_URI'], index_col='id')
batters = pd.read_sql_table('batters', app.config['SQLALCHEMY_DATABASE_URI'], index_col='id')
matchups = pd.read_sql_table('matchups', app.config['SQLALCHEMY_DATABASE_URI'], index_col='matchup')
hev = pd.read_sql_table('hev', app.config['SQLALCHEMY_DATABASE_URI'], index_col='id')

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
        for i in range(0, speed - 10 + 1):
            wind -= 0.15
    if game['venue'] == "Chicago Cubs" and speed >= 10 and direction == "Out":
        for i in range(0, speed - 10 + 1):
            wind += 0.15
    return round(wind * (innings/9), 2)

def getUmp(ump, innings):
    try:
        runs = umps.loc[ump]['runs']
    except:
        runs = 0
    return round(runs * (innings/9), 2)

def getFielding(lineup, innings):
    runs = 0
    players = [id["id"] for id in lineup]
    for player in players:
        try:
            runs += fielding.loc[player]['runs']
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
routes
'''

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(email=login_form.email.data).first()
        if not user_object or not user_object.check_password(login_form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user_object, remember=login_form.remember_me.data)
        flash('Login successful', 'success')
        return redirect(url_for('admin.index'))
    return render_template("login.html", form=login_form)

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    logout_user()
    flash("You have logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for instructions on how to reset your password", 'info')
        return redirect(url_for('login'))
    return render_template("reset_password_request.html", form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        user.set_password(hashed_pswd)
        db.session.commit()
        flash('Your password has been reset', "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

'''
sockets
'''

@socketio.on('game')
def send_data(data):
    game = data['game']
    gamePk = game['gamePk']
    game_time = game['game_time']
    over_under = game['over_under']
    # over_line = game['over_line']
    # under_line = game['under_line']
    starters = {'away': "TBA", 'home': "TBA"}
    if game['away_lineup'] and game['home_lineup'] and game['away_pitcher'] and game['home_pitcher']:
        starters['away'] = game['away_pitcher']['boxscoreName']
        starters['home'] = game['home_pitcher']['boxscoreName']
        innings = game['innings']
        wind_data = game['weather']['wind'].split()
        speed = int(wind_data[0])
        direction = wind_data[2]
        wind = getWind(game, speed, direction, innings)
        venue = round(parks.loc[game['venue']]['runs'] * (innings/9), 2)
        handicap = getHandicap(game['away_team_full'], game['home_team_full'], innings)
        over_threshold = round(parks.loc[game['venue']]['over_threshold'] * (innings/9), 2)
        under_threshold = round(parks.loc[game['venue']]['under_threshold'] * (innings/9), 2)
        over_80 = round(over_threshold * 0.8, 2)
        under_80 = round(under_threshold * 0.8, 2)
        over_60 = round(over_threshold * 0.6, 2)
        under_60 = round(under_threshold * 0.6, 2)
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
        prediction = venue + handicap + ump + away_fielding + home_fielding + weather + away_matchups + home_matchups + wind
        pred_data = [venue, handicap, weather, wind, ump, home_fielding, away_fielding, away_matchups, home_matchups]

        # line = abs(over_line) + abs(under_line)
        # if line == 220:
        #     adj_line = round(over_under + lines_20.loc[over_line]['mod'], 2)
        # else:
        #     try:
        #         adj_line = round(over_under + lines_22.loc[over_line]['mod'], 2)
        #     except:
        #         adj_line = -0.25
        # adj_total = round(prediction - adj_line, 2)

        total = round(prediction - over_under, 2)
        bet_100 = getValue(total, over_threshold, under_threshold)
        bet_80 = getValue(total, over_80, under_80)
        bet_60 = getValue(total, over_60, under_60)

        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': pred_data, 'pitchers': starters, 'wind_speed': speed, 'wind_direction': direction, 'wind': wind, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_80': over_80, 'under_80': under_80, 'over_60': over_60, 'under_60': under_60, 'prediction': round(prediction, 2), 'total': total, 'bet_100': bet_100, 'bet_80': bet_80, 'bet_60': bet_60})
    else:
        emit('predictionData', {'game': game, 'gamePk': gamePk, 'game_time': game_time, 'pred_data': None, 'pitchers': starters, 'wind_speed': None, 'wind_direction': None, 'wind': None, 'over_threshold': None, 'under_threshold': None, 'over_80': None, 'under_80': None, 'over_60': None, 'under_60': None,  'prediction': "TBD", 'total': "TBD", 'bet_100': "TBD", 'bet_80': "TBD", 'bet_60': "TBD"})

@socketio.on('changeLine')
def change_line(data):
    ids = data['ids']
    prediction = data['prediction']
    over_threshold = data['over_threshold']
    under_threshold = data['under_threshold']
    over_80 = data['over_80']
    under_80 = data['under_80']
    over_60 = data['over_60']
    under_60 = data['under_60']
    over_under = data['over_under']
    over = data['over']
    under = data['under']
    game = data['game']
    game['over_under'] = over_under
    try:
        # line = abs(over) + abs(under)
        # if line == 220:
        #     adj_line = round(over_under + lines_20.loc[over]['mod'], 2)
        # else: 
        #     try:
        #         adj_line = round(over_under + lines_22.loc[over]['mod'], 2)
        #     except:
        #         adj_line = -0.25
        # adj_total = round(prediction - adj_line, 2)

        total = round(prediction - over_under, 2)
        bet_100 = getValue(total, over_threshold, under_threshold)
        bet_80 = getValue(total, over_80, under_80)
        bet_60 = getValue(total, over_60, under_60)

        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'new_total': total, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_80': over_80, 'under_80': under_80, 'over_60': over_60, 'under_60': under_60, 'bet_100': bet_100, 'bet_80': bet_80, 'bet_60': bet_60, "ids": ids})
    except:
        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'new_total': 'TBD', 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_80': over_80, 'under_80': under_80, 'over_60': over_60, 'under_60': under_60, 'bet_100': "TBD", 'bet_80': "TBD", 'bet_60': "TBD", "ids": ids})

if __name__ == '__main__':
    socketio.run(app)
