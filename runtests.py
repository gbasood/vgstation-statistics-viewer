import os, unittest, tempfile
from app import app as sviewer
import app as ourapp
from config import basedir
from sqlalchemy import MetaData

dbpath = os.path.join(basedir, 'testcontent', 'db', 'test.db') #pragma: no cover
if not os.path.exists(os.path.dirname(dbpath)): # pragma: no cover
    os.makedirs(os.path.dirname(dbpath)) # pragma: no cover
sviewer.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(dbpath) # pragma: no cover


class ParseToDBTestCase(unittest.TestCase): # pragma: no cover

    def setUp(self):
        self.app = sviewer.test_client()
        sviewer.config['TESTING'] = True
        with sviewer.app_context():
            ourapp.db.create_all()
        # Import a file to work with.

    def tearDown(self):
        ourapp.db.drop_all()

    # Let's make sure our DB is clean before we continue.
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Last match:' in rv.data
        a = ourapp.models.Match.query.first()
        assert a == None

    def test_parse_valid_match(self):
        testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
        # assert testresult
        match1 = ourapp.models.Match.query.first()
        assert testresult and match1 and match1.mapname and match1.crewscore

    def test_parse_invalid_match(self):
        print('Next test should not pass!')
        try:
            testresult = ourapp.parse.parse_file('testcontent/invalid/statistics_2015.14.testfile.txt')
            assert ourapp.models.Match.query.first() is None
            assert len(ourapp.models.Match.query.all()) is None
            self.fail("Test did not fail as expected")
            return False
        except:
            return True

    def test_parse_weird_match(self):
        testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2016.05.10.HH10SS.txt')
        match1 = ourapp.models.Match.query.first()

        assert testresult and match1 and match1.mapname and match1.crewscore and "HH10SS" in match1.parsed_file

    def test_parse_sqlinjection_test(self):
        testresult = ourapp.parse.parse_file('testcontent/invalid/statistics_2015.14.12.sqlinjectiontestfile.txt')
        match1 = ourapp.models.Match.query.first()

        assert match1 is not None

class ViewsTestCase(unittest.TestCase): # pragma: no cover

    def setUp(self):
        self.app = sviewer.test_client()
        sviewer.config['TESTING'] = True
        with sviewer.app_context():
            ourapp.db.create_all()
        # Import a file to work with.

    def tearDown(self):
        ourapp.db.drop_all()

    def test_global_stats(self):
        rv = self.app.get('/globalstats')
        assert b'matchChart' in rv.data

    def test_matchlist(self):
        testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
        rv = self.app.get('/matchlist')
        assert b'match-title' in rv.data

    def test_matchpage(self):
        testresult = ourapp.parse.parse_file('testcontent/valid/statistics_2015.14.12.testfile.txt')
        rv = self.app.get('/match/1')
        assert b'Player deaths' in rv.data

if __name__ == '__main__': # pragma: no cover
    unittest.main()
