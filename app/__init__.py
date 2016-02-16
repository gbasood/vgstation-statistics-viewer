from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config.from_object('config')
app.debug = config.debug
db = SQLAlchemy(app)

from app import views, models
