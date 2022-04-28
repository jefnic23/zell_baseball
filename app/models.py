import jwt
from time import time
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
from app import app, db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def set_password(self, password):
        self.password = password

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Batters(db.Model):
    __tablename__ = "batters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    stand = db.Column(db.String(), nullable=False)
    hev_r = db.Column(db.Float, nullable=False)
    hev_l = db.Column(db.Float, nullable=False)

class Bets(db.Model):
    __tablename__ = "bets"
    total = db.Column(db.Float, primary_key=True)
    bet = db.Column(db.Integer, nullable=False)

class Bullpens(db.Model):
    __tablename__ = "bullpens"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    runs = db.Column(db.Float, nullable=False)

class Fielding(db.Model):
    __tablename__ = "fielding"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    runs = db.Column(db.Float, nullable=False)

class Hev(db.Model):
    __tablename__ = "hev"
    id = db.Column(db.Float, primary_key=True)
    runs = db.Column(db.Float, nullable=False)

class Matchups(db.Model):
    __tablename__ = "matchups"
    matchup = db.Column(db.String(), primary_key=True)
    odds = db.Column(db.Float, nullable=False)

class Misc(db.Model):
    __tablename__ = "misc"
    name = db.Column(db.String(), primary_key=True)
    value = db.Column(db.Float, nullable=False)

class Parks(db.Model):
    __tablename__ = "parks"
    park = db.Column(db.String(), primary_key=True)
    lg = db.Column(db.String(), nullable=False)
    runs = db.Column(db.Float, nullable=False)
    over_threshold = db.Column(db.Float, nullable=False)
    under_threshold = db.Column(db.Float, nullable=False)
    handicap = db.Column(db.Float, nullable=False)

class Pitchers(db.Model):
    __tablename__ = "pitchers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    p_throws = db.Column(db.String(), nullable=False)
    hev_r = db.Column(db.Float, nullable=False)
    hev_l = db.Column(db.Float, nullable=False)
    ip = db.Column(db.Float, nullable=False)

class Umps(db.Model):
    __tablename__ ="umps"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    runs = db.Column(db.Float, nullable=False)
