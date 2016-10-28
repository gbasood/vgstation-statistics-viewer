import factory
from app import models, db
from testcontent import factory as ourfactory
from factory.fuzzy import FuzzyInteger, FuzzyChoice

class MatchFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Match
        sqlalchemy_session = db.session
    # modes_string = FuzzyChoice('cult', 'revolution', 'vampire', 'autotraitor', 'nuclear emergency', 'blob', 'wizard', 'ragin\' mages', 'ai malfunction', 'revolutionary squad', 'changeling')
    modes_string = FuzzyChoice('cult')
    if modes_string === 'cult':
        cultstat = factory.RelatedFactory(ourfactory.CultStatFactory, 'match_id')
