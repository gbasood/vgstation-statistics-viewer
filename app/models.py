"""
Model definitions for SQLAlchemy models used in this app.
"""
import datetime
import json

from app import db
from sqlalchemy import and_, or_

def to_json(mdl):
    """
    Jsonify a SQLAlchemy model.
    """
    d = mdl.__dict__
    return dict_to_json(d)


def dict_to_json(d):
    d = dict_to_safe_for_json(d)
    return json.dumps(d, ensure_ascii=False)


def dict_to_safe_for_json(d):
    # TODO add a serialize method to classes that need special handling
    # e.g. deaths/explosions can have their xyz converted to an array instead of three separate values
    if '_sa_instance_state' in d:
        d.pop('_sa_instance_state')
    for key, value in d.items():
        if type(value) is datetime.datetime:
            d[key] = value.isoformat()
        elif type(value) is dict:
            d[key] = dict_to_safe_for_json(value)
        elif type(value) is list:
            for n, i in enumerate(value):
                # should only hit this line if one-to-many model,
                # so it should always be a list
                if isinstance(i, db.Model):
                    if hasattr(value, "serialize_to_json"):
                        d[key] = value.serialize_to_json()
                    else:
                        value[n] = dict_to_safe_for_json(i.__dict__)
    return d


class Match(db.Model):
    """Match model."""

    id = db.Column(db.Integer, primary_key=True)
    parsed_file = db.Column(db.String(255), index=False, unique=True, nullable=False)
    data_version = db.Column(db.String(45), unique=False)
    mastermode = db.Column(db.String(255), index=True, unique=False)
    modes_string = db.Column(db.String(65535), unique=False)
    crewscore = db.Column(db.Integer)
    nuked = db.Column(db.Boolean)
    crates_ordered = db.Column(db.Integer)
    blood_spilled = db.Column(db.Integer)
    artifacts_discovered = db.Column(db.Integer)
    tech_total = db.Column(db.Integer)
    mapname = db.Column(db.String)
    borgs_at_roundend = db.Column(db.Integer)
    remaining_heads = db.Column(db.Integer)
    station_name = db.Column(db.String)

    starttime = db.Column(db.Integer)
    endtime = db.Column(db.Integer)
    # Calculated value in seconds
    round_length = db.Column(db.Integer)

    explosions = db.relationship('Explosion', backref='match', lazy='dynamic')
    deaths = db.relationship('Death', backref='match', lazy='dynamic')
    antagobjs = db.relationship('AntagObjective', backref='match', lazy='dynamic')
    uplinkbuys = db.relationship('UplinkBuy', backref='match', lazy='dynamic')
    badassbuy = db.relationship('BadassBundleBuy', backref='match', lazy='dynamic')
    survivors = db.relationship('Survivor', backref='match', lazy='dynamic')
    malf_modules = db.relationship('MatchMalfModule', backref='match', lazy='dynamic')

    # Cult
    cult_runes_written = db.Column(db.Integer)
    cult_runes_nulled = db.Column(db.Integer)
    cult_runes_fumbled = db.Column(db.Integer)
    cult_converted = db.Column(db.Integer)
    cult_tomes_created = db.Column(db.Integer)
    cult_narsie_summoned = db.Column(db.Boolean)
    cult_narsie_corpses_fed = db.Column(db.Integer)
    cult_surviving_cultists = db.Column(db.Integer)
    cult_deconverted = db.Column(db.Integer)

    # Xeno
    xeno_eggs_laid = db.Column(db.Integer)
    xeno_faces_hugged = db.Column(db.Integer)
    xeno_faces_protected = db.Column(db.Integer)

    # Blob
    blob_wins = db.Column(db.Boolean)
    blob_spawned_blob_players = db.Column(db.Integer)
    blob_spores_spawned = db.Column(db.Integer)
    blob_res_generated = db.Column(db.Integer)

    # Malf
    malf_won = db.Column(db.Boolean)
    malf_shunted = db.Column(db.Boolean)

    # Revsquad
    revsquad_won = db.Column(db.Boolean)
    revsquad_items = db.relationship('MatchRevsquadItem', backref='match', lazy='dynamic')

    populationstats = db.relationship('PopulationSnapshot', backref='match', lazy='dynamic')

    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)

    def __repr__(self):
        """Represent match for debug purposes."""
        return '<Match #%r | Mode %r Parsed file %r>' % (self.id, self.modes_string, self.parsed_file)

    def is_mixed(self):
        """Return a boolean based on whether or not the match is mixed mode."""
        return self.mastermode == "mixed" or '|' in self.modes_string

    def get_antags(self):
        """Return all antags' key, name, and role."""
        antags = []
        for obj in self.antagobjs.group_by(AntagObjective.mindkey):
            antag = {'key': obj.mindkey, 'name': obj.mindname, 'role': obj.special_role}
            antags.append(antag)
        return antags

    def get_objs_for_antag(self, antagkey):
        """Return the objectives for an antag from this match."""
        return self.antagobjs.filter(AntagObjective.mindkey == antagkey)

    def player_deaths(self):
        """
        Return all Death entries associated with this match, whose keys are not null, and are not manifested ghosts.
        """
        return self.deaths.filter(and_(Death.mindkey != 'null', Death.mindkey != None, Death.mindname != 'Manifested Ghost'))

    def nonplayer_deaths(self):
        """Return all Death entries associated with this match, whose keys are null."""
        return self.deaths.filter(or_(Death.mindkey == 'null', Death.mindkey == None))

    def duration(self):
        """Return the number of minutes this round was played."""
        if(float(self.data_version) < 1.1):
            return None

        if self.start_datetime and self.end_datetime:
            delta = self.start_datetime - self.end_datetime
            return int(abs(delta.total_seconds() - delta.total_seconds() % 60) / 60)

        s = self.starttime.split('.')
        e = self.endtime.split('.')
        # yyyy mm dd hh mm ss
        start = datetime.datetime(year=int(s[0]), month=int(s[1]), day=int(s[2]),
                                  hour=int(s[3]), minute=int(s[4]), second=int(s[5]))
        end = datetime.datetime(year=int(e[0]), month=int(e[1]), day=int(e[2]),
                                hour=int(e[3]), minute=int(e[4]), second=int(e[5]))

        delta = start - end
        return int(abs((delta.total_seconds() - delta.total_seconds() % 60) / 60))

    def uplink_buys_by_key(self, key):
        """Return any UplinkBuy entries associated with a player key."""
        buys = []
        for buy in self.uplinkbuys:
            if buy.mindkey == key:
                buys.append(buy)
        return buys

    def badass_buys_by_key(self, key):
        """Return any BadassBundleBuy entries associated with a player key."""
        badbuys = []
        for badbuy in self.badassbuy:
            if badbuy.mindkey == key:
                badbuys.append(badbuy)
        return badbuys

    def as_json(self):
        """Return self and children as JSON data."""
        # if we don't convert it to a dict we'll get a whole bunch of 'can't be serialized' things
        # match = self.__dict__
        # match.pop('_sa_instance_state', None)
        # for k in match:
        #
        # match['date'] = match['date'].isoformat()
        m = self.__dict__
        m['explosions'] = self.explosions.all()
        m['deaths'] = self.deaths.all()
        m['antagobjs'] = self.antagobjs.all()
        m['uplinkbuys'] = self.uplinkbuys.all()
        m['badassbuys'] = self.badassbuy.all()
        m['populationstats'] = self.populationstats.all()

        return dict_to_json(m)


class Explosion(db.Model):
    """Explosion model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    epicenter_x = db.Column(db.Integer)
    epicenter_y = db.Column(db.Integer)
    epicenter_z = db.Column(db.Integer)
    devastation_range = db.Column(db.Integer)
    heavy_impact_range = db.Column(db.Integer)
    light_impact_range = db.Column(db.Integer)

    def serialize_to_json(self):
        """
        Return self as JSON.
        """
        d = self.__dict__
        x = d.pop('epicenter_x')
        y = d.pop('epicenter_y')
        z = d.pop('epicenter_z')
        d['epicenter'] = [x, y, z]

        return dict_to_safe_for_json(d)


class Death(db.Model):
    """Death model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String(100))
    mindkey = db.Column(db.String(30))
    typepath = db.Column(db.String(200))
    special_role = db.Column(db.String(100))
    assigned_role = db.Column(db.String(100))
    time_of_death = db.Column(db.Integer)

    death_x = db.Column(db.Integer)
    death_y = db.Column(db.Integer)
    death_z = db.Column(db.Integer)

    damage_brute = db.Column(db.Integer)
    damage_fire = db.Column(db.Integer)
    damage_toxin = db.Column(db.Integer)
    damage_oxygen = db.Column(db.Integer)
    damage_clone = db.Column(db.Integer)
    damage_brain = db.Column(db.Integer)

    def serialize_to_json(self):
        d = self.__dict__
        x = d.pop("death_x")
        y = d.pop("death_y")
        z = d.pop("death_z")
        d['location'] = [x, y, z]

        return dict_to_safe_for_json(d)


class AntagObjective(db.Model):
    """Antagonist objective model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String(100))
    mindkey = db.Column(db.String(30))
    special_role = db.Column(db.String(30))
    objective_type = db.Column(db.String(45))
    objective_desc = db.Column(db.String)
    objective_succeeded = db.Column(db.Boolean)
    target_name = db.Column(db.String(100))
    target_role = db.Column(db.String(100))

    def __repr__(self):
        """Represent self for debug purposes."""
        return '<AntagObjective #%r | Name %r | Key %r| Type #%r | Succeeded %r>' % (self.id, self.mindname,
                                                                                     self.mindkey, self.objective_type,
                                                                                     self.objective_succeeded)


class UplinkBuy(db.Model):
    """Uplink purchase model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String)
    mindkey = db.Column(db.String(30))
    traitor_buyer = db.Column(db.Boolean)
    bundle_path = db.Column(db.String)
    item_path = db.Column(db.String)


class BadassBundleBuy(db.Model):
    """Badass bundle purchase model. Has many BassBundleItem."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String)
    mindkey = db.Column(db.String(30))
    traitor_buyer = db.Column(db.Boolean)

    items = db.relationship("BadassBundleItem", backref='badass_bundle_buy', lazy='joined')


class BadassBundleItem(db.Model):
    """Badass bundle item model."""

    id = db.Column(db.Integer, primary_key=True)
    badass_bundle_id = db.Column(db.Integer, db.ForeignKey('badass_bundle_buy.id'), index=True)
    item_path = db.Column(db.String)


class PopulationSnapshot(db.Model):
    """Population count and timestamp."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    popcount = db.Column(db.Integer)
    time = db.Column(db.DateTime)


class Survivor(db.Model):
    """Players who were alive at round end."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    # mind stuff
    mindname = db.Column(db.String)
    mindkey = db.Column(db.String(30))
    special_role = db.Column(db.String)
    mob_typepath = db.Column(db.String)
    # damage stuff
    damage_brute = db.Column(db.Integer)
    damage_fire = db.Column(db.Integer)
    damage_toxin = db.Column(db.Integer)
    damage_oxygen = db.Column(db.Integer)
    damage_clone = db.Column(db.Integer)
    damage_brain = db.Column(db.Integer)


# Auto-populated reference tables
class MalfModule(db.Model):
    """A reference table for malf AI modules."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    @staticmethod
    def get_or_add(nameval):
        # So since our reference tables' values are much more volatile than
        # I'd like, we're going to have to automatically generate them.
        model = MalfModule.query.filter_by(name=nameval).first()
        if model == None:
            mm = MalfModule()
            mm.name = nameval
            db.session.add(mm)
            db.session.commit()
            return mm
        else:
            return model

    def __repr__(self):
        return '<MalfModule {id} "{name}"'.format(**self)


class RevsquadItem(db.Model):
    """A reference table for revsquad items."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    @staticmethod
    def get_or_add(nameval):
        model = RevsquadItem.query.filter_by(name=nameval).first()
        if model == None:
            mm = RevsquadItem()
            mm.name = nameval
            db.session.add(mm)
            db.session.commit()
            return mm
        else:
            return model


# BRIDGE TABLES WOO
class MatchMalfModule(db.Model):
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('malf_module.id'), primary_key=True)


class MatchRevsquadItem(db.Model):
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('revsquad_item.id'), primary_key=True)
