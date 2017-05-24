import logging
import os
import unittest
from app import app as sviewer
import app as ourapp
from config import basedir
from testcontent.factories.match import MatchFactory

dbpath = os.path.join(basedir, 'testcontent', 'db', 'test.db')  # pragma: no cover
if not os.path.exists(os.path.dirname(dbpath)):  # pragma: no cover
    os.makedirs(os.path.dirname(dbpath))  # pragma: no cover
sviewer.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(dbpath)  # pragma: no cover

# Todo: separate into own file, make it test for HTML elements instead of specific strings
class ViewsTestCase(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        sviewer.logger.setLevel(logging.ERROR)
        sviewer.config['TESTING'] = True
        self.app = sviewer.test_client()
        with sviewer.app_context():
            ourapp.db.create_all()

    def tearDown(self):
        with sviewer.app_context():
            ourapp.db.drop_all()

    def test_global_stats(self):
        with sviewer.app_context():
            MatchFactory()
            rv = self.app.get('/globalstats')
            assert b'matchChart' in rv.data

    def test_matchlist(self):
        with sviewer.app_context():
            testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
            rv = self.app.get('/matchlist')
            assert b'match-title' in rv.data

    def test_matchpage(self):
        with sviewer.app_context():
            testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
            rv = self.app.get('/match/1')
            assert b'Deaths' in rv.data

    def test_popcount_matchpage(self):
        with sviewer.app_context():
            testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2017.18.02.100019.txt')
            rv = self.app.get('/match/1')
            assert b'timeline' in rv.data


class GamemodeTemplatesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = sviewer.test_client()
        sviewer.config['TESTING'] = True
        with sviewer.app_context():
            ourapp.db.create_all()

    def tearDown(self):
        with sviewer.app_context():
            ourapp.db.drop_all()

    def test_malfview(self):
        with sviewer.app_context():
            match = MatchFactory(modes_string='ai malfunction')
            ourapp.db.session.commit()
            rv = self.app.get('/match/{}'.format(match.id))
            assert b'Malf win:' in rv.data

    def test_cultview(self):
        with sviewer.app_context():
            match = MatchFactory(modes_string='cult')
            ourapp.db.session.commit()
            rv = self.app.get('/match/{}'.format(match.id))
            assert b'Corpses fed to Nar\'sie:' in rv.data
