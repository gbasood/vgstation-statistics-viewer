from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config, os

app = Flask(__name__)
app.config.from_object('config')
app.debug = config.debug
db = SQLAlchemy(app)

if not os.path.exists(config.STATS_DIR):
    os.makedirs(config.STATS_DIR)
if not os.path.exists(config.PROCESSED_DIR):
    os.makedirs(config.PROCESSED_DIR)
if not os.path.exists(config.UNPARSABLE_DIR):
    os.makedirs(config.UNPARSABLE_DIR)

from app import views, models

from app import helpers, filters
