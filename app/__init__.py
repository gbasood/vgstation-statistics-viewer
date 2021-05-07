import logging
import os
import threading

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_compress import Compress


from config import config as Config
from flask_caching import Cache

db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()


def create_app(config):
    app = Flask(__name__)
    config_name = config

    if not isinstance(config, str):
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(Config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

    # This is how we load the different configs we have for different environments:
    # dev/testing/prod
    Config[config_name].init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    cache.init_app(app)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    register_blueprints(app)
    register_errorhandlers(app)

    app.db = db
    app.parse_lock = threading.Lock()

    return app


def register_blueprints(app):
    from app import api, public, main

    app.register_blueprint(main.blueprint)
    app.register_blueprint(api.views.blueprint)
    return None


def register_errorhandlers(app):
    """register error handlers"""
    def render_error(error):
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None
