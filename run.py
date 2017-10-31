#!flask/bin/python

from flask import current_app
from app.app import create_app
import os

ourapp = create_app(os.path.realpath('config.py'))
with ourapp.app_context():
    print("Starting up " + current_app.name)
