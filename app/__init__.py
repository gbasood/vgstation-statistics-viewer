"""App entry point."""
import config
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

app = None


def create_app(config_path):
    global app
    app = Flask(__name__)
    app.config.from_pyfile(config_path)

    if not os.path.exists(config.STATS_DIR):
        os.makedirs(config.STATS_DIR)
    if not os.path.exists(config.PROCESSED_DIR):
        os.makedirs(config.PROCESSED_DIR)
    if not os.path.exists(config.UNPARSABLE_DIR):
        os.makedirs(config.UNPARSABLE_DIR)

    from app import views, helpers, filters  # noqa: F401
    from app.models import db
    db = db.init_app(app)

    logging.basicConfig(format="%(asctime)s %(msg)s", filename="statsserv_log.txt")

    errorHandler = RotatingFileHandler('statsserv_error.txt', maxBytes=100000, backupCount=1)
    errorHandler.setLevel(logging.WARNING)
    app.logger.addHandler(errorHandler)

    logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n'
                                  '[in %(pathname)s:%(lineno)d]')
    errorHandler.setFormatter(logFormat)
    app.logger.handlers[0].setFormatter(logFormat)

    return app
