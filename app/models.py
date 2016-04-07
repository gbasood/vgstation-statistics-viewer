from app import db

class Match(db.Model):
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
    endttime = db.Column(db.Integer)

    explosions = db.relationship('Explosion', backref='match', lazy='dynamic')
    deaths = db.relationship('Death', backref='match', lazy='dynamic')
    antagobjs = db.relationship('AntagObjective', backref='match', lazy='dynamic')
    uplinkbuys = db.relationship('UplinkBuy', backref='match', lazy='dynamic')
    badassbuy = db.relationship('BadassBundleBuy', backref='match', lazy='dynamic')
    cultstat = db.relationship('CultStats', backref='match', lazy='joined', uselist=False)
    xenostat = db.relationship('XenoStats', backref='match', lazy='joined', uselist=False)


    def __repr__(self):
        return '<Match #%r | Mode %r Parsed file %r>' % (self.id, self.modes_string, self.parsed_file)

class Explosion(db.Model):
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

class UplinkBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String)
    mindkey = db.Column(db.String(30))
    traitor_buyer = db.Column(db.Boolean)
    bundle_path = db.Column(db.String)
    item_path = db.Column(db.String)

class BadassBundleBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    mindname = db.Column(db.String)
    mindkey = db.Column(db.String(30))
    traitor_buyer = db.Column(db.Boolean)

    items = db.relationship("BadassBundleItem", backref='badass_bundle_buy', lazy='joined')

class BadassBundleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    badass_bundle_id = db.Column(db.Integer, db.ForeignKey('badass_bundle_buy.id'), index=True)
    item_path = db.Column(db.String)

class CultStats(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), index=True)
    eggs_laid = db.Column(db.Integer)
    faces_hugged = db.Column(db.Integer)
    faces_protected = db.Column(db.Integer)
