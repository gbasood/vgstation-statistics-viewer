#!flask/bin/python

from flask_script import Manager
from flask import current_app
from app import create_app
import os

ourapp = create_app(os.path.realpath('config.py'))
with ourapp.app_context():
    print("Starting up " + current_app.name)

manager = Manager(ourapp)

# def cls():
#     os.system('cls' if os.name=='nt' else 'clear')
# cls()

if __name__ == '__main__':
    manager.run()

# app.run(config.host, config.port)
