#!/usr/bin/env python
import os
import subprocess

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, Server
from redis import Redis
from rq import Connection, Queue, Worker

from app import create_app, db
from config import Config

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def runserver(port='5000'):
    Server(host='0.0.0.0', port=port)
    print("bye")


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


# @manager.command
# def setup_dev():
#     """Runs the set-up needed for local development."""
#     setup_general()
#
#
# @manager.command
# def setup_prod():
#     """Runs the set-up needed for production."""
#     setup_general()


@manager.command
def format_code():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == '__main__':
    manager.run()
