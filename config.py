import sys, os

# Non-Flask, SQLAlchemy, lib stuff, just for our use!
basedir = os.path.abspath(os.path.dirname(__file__))

# General settings
debug = False
host = '0.0.0.0'
port = 5000

# Database
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db/db_repository')



# Load from arguments
if len(sys.argv) > 1:
    if sys.argv[1] == 'debug':
        debug = True
        SQLALCHEMY_TRACK_MODIFICATIONS = True
