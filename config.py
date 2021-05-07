import os

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'Statistics-Viewer')
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        if not os.path.exists(app.config["STATS_BASE_DIR"]):
            os.makedirs(app.config["STATS_BASE_DIR"])
        if not os.path.exists(app.config["STATS_PROCESSED_DIR"]):
            os.makedirs(app.config["STATS_PROCESSED_DIR"])
        if not os.path.exists(app.config["STATS_UNPARSABLE_DIR"]):
            os.makedirs(app.config["STATS_UNPARSABLE_DIR"])
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL',
                                             'sqlite:///' + 'sqlite:///' + os.path.join(basedir, 'db', 'app.db'))
    STATS_BASE_DIR = os.path.join(basedir, 'test-statfiles')
    STATS_PROCESSED_DIR = os.path.join(STATS_BASE_DIR, 'processed')
    STATS_UNPARSABLE_DIR = os.path.join(STATS_BASE_DIR, 'unparsable')

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        print('THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
                                             'sqlite:///' + 'sqlite:///' + os.path.join(basedir, 'db', 'app.db'))
    WTF_CSRF_ENABLED = False
    STATS_BASE_DIR = os.path.join(basedir, 'test-statfiles')
    STATS_PROCESSED_DIR = os.path.join(STATS_BASE_DIR, 'processed')
    STATS_UNPARSABLE_DIR = os.path.join(STATS_BASE_DIR, 'unparsable')

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        print('THIS APP IS IN TESTING MODE.  \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class ProductionConfig(Config):
    DEBUG = False
    USE_RELOADER = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'sqlite:///' + os.path.join(basedir, 'db', 'app.db'))
    SSL_DISABLE = (os.environ.get('SSL_DISABLE', 'True') == 'True')
    STATS_BASE_DIR = os.path.join(basedir, 'test-statfiles')
    STATS_PROCESSED_DIR = os.path.join(STATS_BASE_DIR, 'processed')
    STATS_UNPARSABLE_DIR = os.path.join(STATS_BASE_DIR, 'unparsable')

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# General settings
host = '0.0.0.0'
port = 5000

# Database
# SQLALCHEMY_TRACK_MODIFICATIONS = False
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'app.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db', 'db_repository')

# No longer used due to Manager implementation
# Load from arguments
# if len(sys.argv) > 1:
#     if sys.argv[1] == 'debug':
#         debug = True
#         SQLALCHEMY_TRACK_MODIFICATIONS = True


# App settings
MATCHES_PER_PAGE = 24  # Works best as a multiple of 3
