"""
Factory for PopulationSnapshot
"""

import factory
import datetime
from app import models
from app.models import db
from factory.fuzzy import FuzzyInteger, FuzzyNaiveDateTime


class PopSnapFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.PopulationSnapshot
        sqlalchemy_session = db.session
    id = factory.Sequence(int)
    popcount = FuzzyInteger(0, 150)
    time = FuzzyNaiveDateTime(datetime.datetime.now())
