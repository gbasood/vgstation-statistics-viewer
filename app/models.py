"""Model definitions for SQLAlchemy models used in this app."""
from app import db
from os import listdir, path
from config import basedir
from sqlalchemy import and_
import datetime


class Match(db.Model):
    """Match model."""

    id = db.Column(db.Integer, primary_key=True)
    parsed_file = db.Column(db.String(255), index=False, unique=True, nullable=False)
    data_version = db.Column(db.String(45), unique=False)
    mastermode = db.Column(db.String(255), index=True, unique=False)
    modes_string = db.Column(db.String(65535), unique=False)
    crewscore = db.Column(db.Integer)
    escapees = db.Column(db.Integer)
    nuked = db.Column(db.Boolean)
    crates_ordered = db.Column(db.Integer)
    blood_spilled = db.Column(db.Integer)
    artifacts_discovered = db.Column(db.Integer)
    tech_total = db.Column(db.Integer)
    mapname = db.Column(db.String)

    starttime = db.Column(db.Integer)
    endtime = db.Column(db.Integer)
    # Calculated value in seconds
    round_length = db.Column(db.Integer)

    explosions = db.relationship('Explosion', backref='match', lazy='dynamic')
    deaths = db.relationship('Death', backref='match', lazy='dynamic')
    antagobjs = db.relationship('AntagObjective', backref='match', lazy='dynamic')
    uplinkbuys = db.relationship('UplinkBuy', backref='match', lazy='dynamic')
    badassbuy = db.relationship('BadassBundleBuy', backref='match', lazy='dynamic')
    cultstat = db.relationship('CultStats', backref='match', lazy='joined', uselist=False)
    xenostat = db.relationship('XenoStats', backref='match', lazy='joined', uselist=False)
    blobstat = db.relationship('BlobStats', backref='match', lazy='joined', uselist=False)
    malfstat = db.relationship('MalfStats', backref='match', lazy='joined', uselist=False)
    revsquadstat = db.relationship('RevsquadStats', backref='match', lazy='joined', uselist=False)
    populationstats = db.relationship('PopulationSnapshot', backref='match', lazy='dynamic')

    date = db.Column(db.DateTime)
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
        """Return all Death entries associated with this match, whose keys are not null, and are not manifested ghosts."""
        return self.deaths.filter(and_(Death.mindkey != 'null', Death.mindname != 'Manifested Ghost'))

    def nonplayer_deaths(self):
        """Return all Death entries associated with this match, whose keys are null."""
        return self.deaths.filter(Death.mindkey == 'null')

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
        start = datetime.datetime(year=int(s[0]), month=int(s[1]), day=int(s[2]), hour=int(s[3]), minute=int(s[4]), second=int(s[5]))
        end = datetime.datetime(year=int(e[0]), month=int(e[1]), day=int(e[2]), hour=int(e[3]), minute=int(e[4]), second=int(e[5]))

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


class Explosion(db.Model):
    """Explosion model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    epicenter_x = db.Column(db.Integer)
    epicenter_y = db.Column(db.Integer)
    epicenter_z = db.Column(db.Integer)
    devestation_range = db.Column(db.Integer)
    heavy_impact_range = db.Column(db.Integer)
    light_impact_range = db.Column(db.Integer)
    max_range = db.Column(db.Integer)


class Death(db.Model):
    """Death model."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String(100))
    mindkey = db.Column(db.String(30))
    typepath = db.Column(db.String(200))
    special_role = db.Column(db.String(100))
    last_assailant = db.Column(db.String(100))
    time_of_death = db.Column(db.Integer)
    death_x = db.Column(db.Integer)
    death_y = db.Column(db.Integer)
    death_z = db.Column(db.Integer)
    realname = db.Column(db.String)

    # def __repr__(self):
    #     return '<Death #%r>' % (self.id)


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
        return '<AntagObjective #%r | Name %r | Key %r| Type #%r | Succeeded %r>' % (self.id, self.mindname, self.mindkey, self.objective_type, self.objective_succeeded)


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


class CultStats(db.Model):
    """Cult statistics for a match."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    runes_written = db.Column(db.Integer)
    runes_fumbled = db.Column(db.Integer)
    runes_nulled = db.Column(db.Integer)
    converted = db.Column(db.Integer)
    tomes_created = db.Column(db.Integer)
    narsie_summoned = db.Column(db.Boolean)
    narsie_corpses_fed = db.Column(db.Integer)
    surviving_cultists = db.Column(db.Integer)
    deconverted = db.Column(db.Integer)


class XenoStats(db.Model):
    """Xenomorph statistics for a match."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    eggs_laid = db.Column(db.Integer)
    faces_hugged = db.Column(db.Integer)
    faces_protected = db.Column(db.Integer)


class BlobStats(db.Model):
    """Blob statistics for a match."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    blob_wins = db.Column(db.Boolean)
    spawned_blob_players = db.Column(db.Integer)
    spores_spawned = db.Column(db.Integer)
    res_generated = db.Column(db.Integer)


class MalfStats(db.Model):
    """AI malfunction statistics."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    malf_won = db.Column(db.Boolean)
    malf_shunted = db.Column(db.Boolean)
    borgs_at_roundend = db.Column(db.Integer)
    malf_modules = db.Column(db.String)


class RevsquadStats(db.Model):
    """Revolution Squad statistics."""

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    revsquad_won = db.Column(db.Boolean)
    remaining_heads = db.Column(db.Integer)


class PopulationSnapshot(db.Model):
    """ Population count and timestamp. """

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    popcount = db.Column(db.Integer)
    time = db.Column(db.DateTime)
