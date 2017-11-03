import logging
import os
from logging.handlers import RotatingFileHandler
from os import path

from flask import Flask

import config
from app import api, commands, public
from app.extensions import db, migrate


def create_app(config_path):
    app = Flask(__name__.split('.')[0])
    app.config.from_pyfile(config_path)

    if not os.path.exists(config.STATS_DIR):
        os.makedirs(config.STATS_DIR)
    if not os.path.exists(config.PROCESSED_DIR):
        os.makedirs(config.PROCESSED_DIR)
    if not os.path.exists(config.UNPARSABLE_DIR):
        os.makedirs(config.UNPARSABLE_DIR)

    # from app.models import db

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    create_db_if_necessary(app, db)

    logging.basicConfig(format="%(asctime)s %(msg)s", filename="statsserv_log.txt")

    errorHandler = RotatingFileHandler('statsserv_error.txt', maxBytes=100000, backupCount=1)
    errorHandler.setLevel(logging.WARNING)
    app.logger.addHandler(errorHandler)

    logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n'
                                  '[in %(pathname)s:%(lineno)d]')
    errorHandler.setFormatter(logFormat)
    app.logger.handlers[0].setFormatter(logFormat)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    return None


def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)


def create_db_if_necessary(app, db):
    if not path.exists(path.join(config.SQLALCHEMY_DATABASE_URI, "app.db")):
        db.create_all(app=app)
