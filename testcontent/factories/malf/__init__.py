import factory
from app import models
from app.models import db
from factory.fuzzy import FuzzyInteger, FuzzyChoice
truefalse = [True, False]


class MalfStatFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.MalfStats
        sqlalchemy_session = db.session
    id = factory.Sequence(int)
    malf_won = FuzzyChoice(truefalse)
    malf_shunted = FuzzyChoice(truefalse)
    borgs_at_roundend = FuzzyInteger(0, 30)
