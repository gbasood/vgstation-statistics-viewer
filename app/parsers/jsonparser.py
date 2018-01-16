"""For reading JSON data into the database."""
# This whole file is kinda silly.

import json
from datetime import datetime
from typing import Text, Union

# But I didn't, and so we have most of this file.
# TODO: future self, find a way to write this that actually seems good
from flask import current_app
# If I had kept names consistent between the model defintiions
# and the JSON generated files, I could just load it all in naively.
from werkzeug import LocalProxy

from app.models import (AntagObjective, BadassBundleBuy, BadassBundleItem,
                        Death, Explosion, MalfModule, Match, MatchMalfModule,
                        MatchRevsquadItem, PopulationSnapshot, RevsquadItem,
                        Survivor, UplinkBuy)

db = LocalProxy(lambda: current_app.db.session)
logger = LocalProxy(lambda: current_app.logger)


# because even though we're using JSON which has bools, BYOND does not
# so it exports only 1 or 0
def boolify(s: Union[int, None]) -> Union[bool, int]:
    if s == 1:
        return True
    elif s == 0 or s is None:
        return False
    logger.error("Invalid value passed to json parser's boolify")
    return s


def parse(filepath: Text, filename: Text) -> bool:
    f = open(filepath, 'r+')
    js = json.load(f)
    f.close()

    m = Match()
    db.add(m)
    m.parsed_file = filename

    # Okay let's get started
    parse_matchdata(js, m)
    parse_deaths(js, m)
    parse_survivors(js, m)
    parse_uplink_buys(js, m)
    parse_explosions(js, m)
    parse_antag_objectives(js, m)
    parse_badass_buys(js, m)
    parse_population_snapshots(js, m)

    return True


def timestamp_to_datetime(timestring: Text) -> datetime:
    # Format: YYYY-MM-DD HH:MM:SS
    # i.e. 2017-11-06 22:43:37
    year = int(timestring[:4])
    month = int(timestring[5:7])
    day = int(timestring[8:10])
    hour = int(timestring[11:13])
    minute = int(timestring[14:16])
    second = int(timestring[17:19])

    dt = datetime(year, month, day, hour, minute, second)
    return dt


# I feel like there's a better way to handle this but I'm trying to
# implement this before I get sucked into other projects
def parse_matchdata(js: dict, m: Match) -> None:
    m.crewscore = js['crewscore']
    m.data_version = js['data_revision']
    m.mastermode = js['mastermode']
    m.tickermode = js['tickermode']
    # m.modes_string = js['mixed_gamemodes']
    if len(js['mixed_gamemodes']) > 0:
        m.modes_string = '|'.join(js['mixed_gamemodes'])
    else:
        m.modes_string = js['tickermode']
    m.mapname = js['mapname']
    m.crates_ordered = js['crates_ordered']
    m.blood_spilled = js['blood_spilled']
    m.artifacts_discovered = js['artifacts_discovered']
    # terrible bad hotfix
    if 'tech_total' in js:
        m.tech_total = js['tech_total']
    # end bad hotfix
    if 'stationname' in js:
        m.station_name = js['stationname']
    m.borgs_at_roundend = js['borgs_at_roundend']
    m.remaining_heads = js['heads_at_roundend']
    m.nuked = boolify(js['nuked'])

    # Time stamp parsing
    m.start_datetime = timestamp_to_datetime(js['round_start_time'])
    m.end_datetime = timestamp_to_datetime(js['round_start_time'])
    m.round_length = (m.end_datetime - m.start_datetime).total_seconds()

    # cult
    m.cult_runes_written = js['cult_runes_written']
    m.cult_runes_nulled = js['cult_runes_nulled']
    m.cult_runes_fumbled = js['cult_runes_fumbled']
    m.cult_converted = js['cult_converted']
    m.cult_tomes_created = js['cult_tomes_created']
    m.cult_narsie_summoned = boolify(js['cult_narsie_summoned'])
    m.cult_narsie_corpses_fed = js['narsie_corpses_fed']
    m.cult_surviving_cultists = js['cult_surviving_cultists']
    m.cult_deconverted = js['cult_deconverted']

    # xeno
    m.xeno_eggs_laid = js['xeno_eggs_laid']
    m.xeno_faces_hugged = js['xeno_faces_hugged']
    m.xeno_faces_protected = js['xeno_faces_protected']

    # Blob
    m.blob_wins = boolify(js['blob_wins'])
    m.blob_spawned_blob_players = js['blob_spawned_blob_players']
    m.blob_spores_spawned = js['blob_spores_spawned']
    m.blob_res_generated = js['blob_res_generated']

    # Malf
    m.malf_won = boolify(js['malf_won'])
    m.malf_shunted = boolify(js['malf_shunted'])
    for mod in js['malf_modules']:
        modid = MalfModule.get_or_add(mod)
        match_mod = MatchMalfModule(match_id=m.id, module_id=modid.id)
        db.add(match_mod)

    # Revsquad
    m.revsquad_won = boolify(js['revsquad_won'])
    for item in js['revsquad_items']:
        itemid = RevsquadItem.get_or_add(item)
        rev_item = MatchRevsquadItem(match_id=m.id, item_id=itemid.id)
        db.add(rev_item)

    # And finally...
    db.commit()


def parse_deaths(js: dict, match: Match) -> None:
    for death in js['deaths']:
        d = Death(match_id=match.id)

        d.mindkey = death['key']
        d.mindname = death['realname']
        d.assigned_role = death['assigned_role']
        d.special_role = death['special_role']
        d.typepath = death['mob_typepath']
        d.time_of_death = death['time_of_death']
        d.death_x = death['death_x']
        d.death_y = death['death_y']
        d.death_z = death['death_z']
        # Damage stuff
        d.damage_brute = death['damagevalues']['BRUTE']
        d.damage_fire = death['damagevalues']['FIRE']
        d.damage_toxin = death['damagevalues']['TOXIN']
        d.damage_oxygen = death['damagevalues']['OXY']
        d.damage_clone = death['damagevalues']['CLONE']
        d.damage_brain = death['damagevalues']['BRAIN']

        db.add(d)
        db.commit()


def parse_survivors(js: dict, match: Match) -> None:
    for survivor in js['survivors']:
        s = Survivor(match_id=match.id)

        s.mindkey = survivor['key']
        s.mindname = survivor['realname']
        s.assigned_role = survivor['assigned_role']
        s.special_role = survivor['special_role']
        s.typepath = survivor['mob_typepath']
        s.escaped = boolify(survivor['escaped'])
        # Damage stuff
        s.damage_brute = survivor['damagevalues']['BRUTE']
        s.damage_fire = survivor['damagevalues']['FIRE']
        s.damage_toxin = survivor['damagevalues']['TOXIN']
        s.damage_oxygen = survivor['damagevalues']['OXY']
        s.damage_clone = survivor['damagevalues']['CLONE']
        s.damage_brain = survivor['damagevalues']['BRAIN']

        db.add(s)
        db.commit()


def parse_antag_objectives(js: dict, match: Match) -> None:
    for obj in js['antag_objectives']:
        o = AntagObjective(match_id=match.id)
        o.mindkey = obj['key']
        o.mindname = obj['realname']
        o.special_role = obj['special_role']
        o.objective_type = obj['objective_type']
        o.objective_desc = obj['objective_desc']
        o.objective_succeeded = boolify(obj['objective_succeeded'])
        o.target_name = obj['target_name']
        o.target_role = obj['target_role']

        db.add(o)
        db.commit()


def parse_explosions(js: dict, match: Match) -> None:
    for explosion in js['explosions']:
        e = Explosion(match_id=match.id)

        e.epicenter_x = explosion['epicenter_x']
        e.epicenter_y = explosion['epicenter_y']
        e.epicenter_z = explosion['epicenter_z']
        e.devastation_range = explosion['devastation_range']
        e.heavy_impact_range = explosion['heavy_impact_range']
        e.light_impact_range = explosion['light_impact_range']

        db.add(e)
        db.commit()


def parse_uplink_buys(js: dict, match: Match) -> None:
    for buy in js['uplink_purchases']:
        up = UplinkBuy(match_id=match.id)

        up.item_path = buy['itemtype']
        up.bundle_path = buy['bundle']
        up.mindkey = buy['purchaser_key']
        up.mindname = buy['purchaser_name']
        up.traitor_buyer = boolify(buy['purchaser_is_traitor'])

        db.add(up)
        db.commit()


def parse_badass_buys(js: dict, match: Match) -> None:
    for bbuy in js['badass_bundles']:
        bad = BadassBundleBuy(match_id=match.id)

        bad.mindkey = bbuy['purchaser_key']
        bad.mindname = bbuy['purchaser_name']

        db.add(bad)
        db.commit()
        for item in bbuy['contains']:
            i = BadassBundleItem(badass_bundle_id=bad.id, item_path=item)

            db.add(i)
            db.commit()


def parse_population_snapshots(js: dict, match: Match) -> None:
    print(js['population_polls'])
    for snapdata in js['population_polls']:
        snap = PopulationSnapshot(match_id=match.id)
        snap.time = timestamp_to_datetime(snapdata['time'])
        snap.popcount = snapdata['popcount']
        db.add(snap)
    db.commit()
