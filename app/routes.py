from flask import render_template, redirect, url_for, flash
from flask_socketio import emit
from flask_login import login_user, current_user, logout_user
from engineio.payload import Payload
from app.forms import *
from app.models import *
from app.views import *
from app.email import *
from app.baseball import *
from app import app, login, socketio, admin


Payload.max_decode_packets = 50
login.init_app(app)
admin.add_link(LogoutView(name='Logout', endpoint='logout'))
admin.add_view(DataView(Batters, db.session))
admin.add_view(DataView(Bullpens, db.session))
admin.add_view(DataView(Fielding, db.session))
admin.add_view(DataView(Hev, db.session))
admin.add_view(DataView(Matchups, db.session))
admin.add_view(DataView(Parks, db.session))
admin.add_view(DataView(Pitchers, db.session))
admin.add_view(DataView(Umps, db.session))
admin.add_view(DataView(Misc, db.session))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    MODIFIER = Misc.query.get('modifier').value
    BANKROLL = Misc.query.get('bankroll').value
    BET_PCT = Misc.query.get('bet_pct').value
    PVB_MODIFIER = Misc.query.get('pvb_modifier').value
    TODAY = datetime.now(pytz.timezone('America/New_York')).strftime("%m/%d/%Y")
    fd = fanduel()
    sched = schedule(TODAY)
    data = []
    for game in sched:
        data.append(Game(game, fd, MODIFIER, BANKROLL, BET_PCT, PVB_MODIFIER))
    return render_template('index.html', data=data, today=TODAY)

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

@socketio.on('changeLine')
def change_line(data):
    ids = data['ids']
    prediction = data['prediction']
    over_threshold = data['over_threshold']
    under_threshold = data['under_threshold']
    over_80 = data['over_80']
    under_80 = data['under_80']
    over_120 = data['over_120']
    under_120 = data['under_120']
    over_under = data['over_under']
    over = data['over']
    under = data['under']
    game = data['game']
    game['over_under'] = over_under
    try:
        total = round(prediction - over_under, 2)
        bet_120 = getValue(total, over_120, under_120)
        bet_100 = getValue(total, over_threshold, under_threshold)
        bet_80 = getValue(total, over_80, under_80)

        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'new_total': total, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_80': over_80, 'under_80': under_80, 'over_120': over_120, 'under_120': under_120, 'bet_100': bet_100, 'bet_80': bet_80, 'bet_120': bet_120, "ids": ids})
    except:
        emit('lineChange', {'over_under': over_under, 'over': over, 'under': under, 'new_total': 'TBD', 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_80': over_80, 'under_80': under_80, 'over_120': over_120, 'under_120': under_120, 'bet_100': "TBD", 'bet_80': "TBD", 'bet_120': "TBD", "ids": ids})

if __name__ == '__main__':
    socketio.run(app)
