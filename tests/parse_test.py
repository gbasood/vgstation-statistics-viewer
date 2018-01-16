import logging
import os
import unittest

import app as ourapp
from app import models
from app.app import create_app
from app.extensions import db
from config import basedir  # dumb but oh well

# from tests import factories


class ParseToDBTestCase(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.sviewer = create_app(os.path.join(basedir, 'config_unittest.py'))
        self.sviewer.logger.setLevel(logging.ERROR)
        self.sviewer.testing = True
        self.app = self.sviewer.test_client()
        with self.sviewer.app_context():
            db.create_all()

    def tearDown(self):
        with self.sviewer.app_context():
            db.drop_all()

    # Let's make sure our DB is clean before we continue.
    # This test exists mostly to show faults in the testing setup.
    def test_empty_db(self):
        with self.sviewer.app_context():
            # rv = self.app.get('/')
            # assert b'Last match:' in rv.data
            a = models.Match.query.first()
            assert a is None

    def test_parse_valid_match(self):
        with self.sviewer.app_context():
            testresult = ourapp.parse.parse_file('tests/valid/statistics-2018-01-15.113254.json')
            match1 = models.Match.query.first()

            assert testresult is not None
            assert match1 is not None
            # assert match1.station_name is not None
            assert len(match1.survivors.all()) is not 0
            print(match1.populationstats.all())
            assert len(match1.populationstats.all()) is not 0
