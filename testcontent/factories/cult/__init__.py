import factory
from app import models, db
from factory.fuzzy import FuzzyInteger, FuzzyChoice
truefalse = [True, False]


class CultStatFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.CultStats
        sqlalchemy_session = db.session
    id = factory.Sequence(int)
    runes_written = FuzzyInteger(0, 100)
    runes_fumbled = FuzzyInteger(0, 100)
    runes_nulled = FuzzyInteger(0, 100)
    converted = FuzzyInteger(0, 100)
    tomes_created = FuzzyInteger(0, 100)
    narsie_summoned = FuzzyChoice(truefalse)
    if narsie_summoned:
        narsie_corpses_fed = FuzzyInteger(0, 100)
    surviving_cultists = FuzzyInteger(0, 100)
    deconverted = FuzzyInteger(0, 100)
