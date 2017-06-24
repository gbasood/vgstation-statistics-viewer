"""App entry point."""
import config
import os
import logging
from app import views, models, helpers, filters  # noqa: F401
from app.models import db
from logging.handlers import RotatingFileHandler
from flask import Flask


def create_app():
    global db
    app = Flask(__name__)
    app.config.from_object('config')
    app.debug = config.debug

    if not os.path.exists(config.STATS_DIR):
        os.makedirs(config.STATS_DIR)
    if not os.path.exists(config.PROCESSED_DIR):
        os.makedirs(config.PROCESSED_DIR)
    if not os.path.exists(config.UNPARSABLE_DIR):
        os.makedirs(config.UNPARSABLE_DIR)

    db = db.init_app(app)
    return app


logging.basicConfig(format="%(asctime)s %(msg)s", filename="statsserv_log.txt")

errorHandler = RotatingFileHandler('statsserv_error.txt', maxBytes=100000, backupCount=1)
errorHandler.setLevel(logging.WARNING)
app.logger.addHandler(errorHandler)


logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n'
                              '[in %(pathname)s:%(lineno)d]')
errorHandler.setFormatter(logFormat)
app.logger.handlers[0].setFormatter(logFormat)
