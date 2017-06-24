import logging
import os
import unittest
from app import app
from app import create_app
from app import parse
from app.models import db
from testcontent.factories.match import MatchFactory


# Todo: separate into own file, make it test for HTML elements instead of specific strings
class ViewsTestCase(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.sviewer = create_app(os.path.join('..', 'config_unittest.py'))
        self.sviewer.logger.setLevel(logging.ERROR)
        self.sviewer.config['TESTING'] = True
        self.app = self.sviewer.test_client()
        with self.sviewer.app_context():
            db.create_all()

    def tearDown(self):
        with self.sviewer.app_context():
            db.drop_all()

    def test_global_stats(self):
        with self.sviewer.app_context():
            MatchFactory()
            rv = self.app.get('/globalstats')
            assert b'matchChart' in rv.data

    def test_matchlist(self):
        with self.sviewer.app_context():
            parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
            rv = self.app.get('/matchlist')
            assert b'match-title' in rv.data

    def test_matchpage(self):
        with self.sviewer.app_context():
            parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
            rv = self.app.get('/match/1')
            assert b'Deaths' in rv.data

    def test_popcount_matchpage(self):
        with self.sviewer.app_context():
            parse.parse_file('testcontent/valid/statistics_2017.18.02.100019.txt')
            rv = self.app.get('/match/1')
            assert b'timeline' in rv.data


class GamemodeTemplatesTestCase(unittest.TestCase):

    def setUp(self):
        self.sviewer = create_app(os.path.join('..', 'config_unittest.py'))
        self.sviewer.logger.setLevel(logging.ERROR)
        self.sviewer.config['TESTING'] = True
        self.app = self.sviewer.test_client()
        with self.sviewer.app_context():
            db.create_all()

    def tearDown(self):
        with self.sviewer.app_context():
            db.drop_all()

    def test_malfview(self):
        with self.sviewer.app_context():
            match = MatchFactory(modes_string='ai malfunction')
            db.session.commit()
            rv = self.app.get('/match/{}'.format(match.id))
            assert b'Malf win:' in rv.data

    def test_cultview(self):
        with self.sviewer.app_context():
            match = MatchFactory(modes_string='cult')
            db.session.commit()
            rv = self.app.get('/match/{}'.format(match.id))
            assert b'Corpses fed to Nar\'sie:' in rv.data
