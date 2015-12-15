#!flask/bin/python
from app import app
import os, config

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
cls()

app.debug = config.cfg["debug"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.cfg["track_mod"]

app.run(host='0.0.0.0',debug=config.cfg["debug"])
