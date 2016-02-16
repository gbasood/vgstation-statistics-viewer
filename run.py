#!flask/bin/python
from app import app
import os, config

# def cls():
#     os.system('cls' if os.name=='nt' else 'clear')
# cls()

app.run(config.host, config.port)
