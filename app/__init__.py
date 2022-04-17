from ensurepip import bootstrap
from flask import Flask
from config import Config
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object(Config)
Talisman(app, content_security_policy=None)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
socketio = SocketIO(app)
mail = Mail(app)
login = LoginManager(app)
admin = Admin(app, name="ZellBaseball", template_mode="bootstrap4")

from app import routes, models, views
