from app.app import create_app
import app as ourapp
import logging
import os
import unittest
from app import models
from app.models import db
from config import basedir
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
    def test_empty_db(self):
        with self.sviewer.app_context():
            rv = self.app.get('/')
            assert b'Last match:' in rv.data
            a = models.Match.query.first()
            assert a is None

    def test_parse_valid_match(self):
        with self.sviewer.app_context():
            testresult = ourapp.parse.parse_file('tests/valid/statistics_2015.14.12.testfile.txt')
            # assert testresult
            match1 = models.Match.query.first()
            assert testresult and match1 and match1.mapname and match1.crewscore

    def test_parse_invalid_match(self):
        with self.sviewer.app_context():
            try:
                ourapp.parse.parse_file('tests/invalid/statistics_2015.14.testfile.txt')
                assert models.Match.query.first() is None
                assert len(models.Match.query.all()) is None
                self.fail("Test did not fail as expected")
                return False
            except:
                return True

    def test_parse_weird_match(self):
        with self.sviewer.app_context():
            testresult = ourapp.parse.parse_file('tests/valid/statistics_2016.05.10.HH10SS.txt')
            match1 = models.Match.query.first()

            assert testresult and match1 and match1.mapname and match1.crewscore and "HH10SS" in match1.parsed_file

    def test_parse_sqlinjection_test(self):
        with self.sviewer.app_context():
            ourapp.parse.parse_file('tests/invalid/statistics_2015.14.12.sqlinjectiontestfile.txt')
            match1 = models.Match.query.first()

            assert match1 is not None

    def test_parse_popcount_match(self):
        with self.sviewer.app_context():
            ourapp.parse.parse_file('tests/valid/statistics_2017.18.02.100019.txt')
            match1 = models.Match.query.first()

            assert match1 is not None
