#!flask/bin/python

from flask.ext.script import Manager, Command
from app import app
import os, config

manager = Manager(app)

# def cls():
#     os.system('cls' if os.name=='nt' else 'clear')
# cls()

if __name__ == '__main__':
    manager.run()

# app.run(config.host, config.port)
