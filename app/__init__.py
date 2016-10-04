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

import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('statsserv_log.txt', maxBytes = 100000, backupCount = 1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

errorHandler = RotatingFileHandler('statsserv_error.txt', maxBytes = 100000, backupCount = 1)
errorHandler.setLevel(logging.WARNING)
app.logger.addHandler(errorHandler)

app.logger.info('Logging enabled.')

from app import views, models

from app import helpers, filters
