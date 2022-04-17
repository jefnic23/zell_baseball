from flask import Flask
from config import Config
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
Talisman(app, content_security_policy=None)
db = SQLAlchemy(app)

from app import routes
