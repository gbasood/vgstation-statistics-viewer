"""
Factory for Match
"""

import factory
import datetime
import pytz
from app import models
from app.models.models import db
from tests.factories import popsnap
from factory.fuzzy import FuzzyInteger, FuzzyDateTime, FuzzyChoice


def filename():
    parsed_file_date = FuzzyDateTime(datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone('US/Eastern')))
    parsed_file = "statistics_{}".format(parsed_file_date.evaluate(2, None, False).strftime('%Y.%m.%d.%Y%m%d'))
    return parsed_file


class MatchFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Match
        sqlalchemy_session = db.session

    # modes_string = FuzzyChoice(['cult', 'revolution', 'vampire', 'autotraitor', 'nuclear emergency',
    # 'blob', 'wizard', 'ragin\' mages', 'ai malfunction', 'changeling', 'mixed'])
    # id = factory.Sequence(int)
    start_datetime = FuzzyDateTime(datetime.datetime(2012, 1, 1, tzinfo=pytz.timezone('US/Eastern')))
    end_datetime = start_datetime.fuzz() + datetime.timedelta(minutes=FuzzyInteger(15, 300).fuzz())
    parsed_file = "statistics_{}".format(start_datetime.evaluate(2, None, False).strftime('%Y.%m.%d.%Y%m%d'))
    data_version = "1.1"
    modes_string = factory.Iterator(['cult', 'ai malfunction'])

    # General stats
    borgs_at_roundend = FuzzyInteger(0, 30)

    # Cult
    cult_runes_written = FuzzyInteger(0, 100)
    cult_runes_fumbled = FuzzyInteger(0, 100)
    cult_runes_nulled = FuzzyInteger(0, 100)
    cult_converted = FuzzyInteger(0, 100)
    cult_tomes_created = FuzzyInteger(0, 100)
    cult_narsie_summoned = FuzzyChoice([True, False])
    if cult_narsie_summoned:
        cult_narsie_corpses_fed = FuzzyInteger(0, 100)
    cult_surviving_cultists = FuzzyInteger(0, 100)
    cult_deconverted = FuzzyInteger(0, 100)

    # Malfunction
    malf_won = FuzzyChoice([True, False])
    malf_shunted = FuzzyChoice([True, False])

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        populationstats = popsnap.PopSnapFactory.create_batch(10) # noqa F841
    # to be continued as factories are added


# MatchFactory.reset_sequence(1)
