import factory
import datetime
import pytz
from datetime import tzinfo
from app import models, db
from testcontent import factories as ourfactory
from factory.fuzzy import FuzzyInteger, FuzzyChoice, FuzzyDateTime


def filename():
    parsed_file_date = FuzzyDateTime(datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone('US/Eastern')))
    parsed_file = "statistics_{}".format(parsed_file_date.evaluate(2, None, False).strftime('%Y.%m.%d.%Y%m%d'))
    return parsed_file


class MatchFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Match
        sqlalchemy_session = db.session

    # modes_string = FuzzyChoice(['cult', 'revolution', 'vampire', 'autotraitor', 'nuclear emergency', 'blob', 'wizard', 'ragin\' mages', 'ai malfunction', 'revolutionary squad', 'changeling'])
    id = factory.Sequence(lambda n: n)
    modes_string = FuzzyChoice(['cult']).fuzz()
    parsed_file = filename()
    if modes_string == 'cult':
        cultstat = factory.SubFactory(ourfactory.cult.CultStatFactory)
    # to be continued as factories are added
