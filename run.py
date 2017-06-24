#!flask/bin/python

from flask_script import Manager
from app import create_app

manager = Manager(create_app())

# def cls():
#     os.system('cls' if os.name=='nt' else 'clear')
# cls()

if __name__ == '__main__':
    manager.run()

# app.run(config.host, config.port)
