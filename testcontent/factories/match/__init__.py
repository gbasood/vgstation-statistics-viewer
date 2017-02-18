import factory
import datetime
import pytz
from app import models, db
from testcontent.factories import cult, malf, popsnap
from factory.fuzzy import FuzzyInteger, FuzzyDateTime


def filename():
    parsed_file_date = FuzzyDateTime(datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone('US/Eastern')))
    parsed_file = "statistics_{}".format(parsed_file_date.evaluate(2, None, False).strftime('%Y.%m.%d.%Y%m%d'))
    return parsed_file


class MatchFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Match
        sqlalchemy_session = db.session

    # modes_string = FuzzyChoice(['cult', 'revolution', 'vampire', 'autotraitor', 'nuclear emergency', 'blob', 'wizard', 'ragin\' mages', 'ai malfunction', 'changeling'])
    # id = factory.Sequence(int)
    date = FuzzyDateTime(datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone('US/Eastern')))
    start_datetime = date
    end_datetime = date.fuzz() + datetime.timedelta(minutes=FuzzyInteger(15, 300).fuzz())
    parsed_file = "statistics_{}".format(date.evaluate(2, None, False).strftime('%Y.%m.%d.%Y%m%d'))
    data_version = "1.1"
    modes_string = factory.Iterator(['cult', 'ai malfunction'])

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        populationstats = popsnap.PopSnapFactory.create_batch(10)
        if obj.modes_string == 'cult':
            obj.cultstat = cult.CultStatFactory()  # This isn't how factoryboy docs say to do it but it's the only thing that worked woooo
        elif obj.modes_string == 'ai malfunction':
            obj.malfstat = malf.MalfStatFactory()
    # to be continued as factories are added


# MatchFactory.reset_sequence(1)
