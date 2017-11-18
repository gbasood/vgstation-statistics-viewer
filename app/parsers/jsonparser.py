"""For reading JSON data into the database."""
# This whole file is kinda silly.
# If I had kept names consistent between the model defintiions
# and the JSON generated files, I could just load it all in naively.
# But I didn't, and so we have most of this file.
from flask import current_app
from werkzeug import LocalProxy
from typing import Text, Union
from app.models import Match, Death, AntagObjective, BadassBundleBuy, BadassBundleItem, \
    Survivor
import json
import os
from datetime import datetime

logger = LocalProxy(lambda: current_app.logger)
db = LocalProxy(lambda: current_app.db)


def boolify(s: Union[int, None]) -> Union[bool, int]:
    if s == 1:
        return True
    elif s == 0 or s is None:
        return False
    logger.error("Invalid value passed to json parser's boolify")
    return s


def GetBridgeEntry(mdl: db.Model):
    

def parse(filepath: Text):
    f = open(filepath, 'r+')
    js = json.load(f)
    f.close()

    m = Match()
    m.parsed_file = os.path.basename(filepath)

    # Okay let's get started
    parse_matchdata(js, m)
    parse_deaths(js, m)


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


def parse_matchdata(js: dict, m: Match):
    m.crewscore = js['crewscore']
    m.data_version = js['data_revision']
    m.mastermode = js['mastermode']
    m.tickermode = js['tickermode']
    m.modes_string = js['mixed_gamemodes']
    if len(json['mixed_gamemodes']) > 0:
        m.modes_string = '|'.join(js['mixed_gamemodes'])
    else:
        m.modes_string = js['tickermode']
    m.mapname = js['mapname']
    m.escapees = js['escapees']
    m.crates_ordered = js['crates_ordered']
    m.blood_spilled = js['blood_spilled']
    m.artifacts_discovered = js['artifacts_discovered']
    m.tech_total = js['tech_total']
    m.borgs_at_roundend = js['borgs_at_roundend']
    m.remaining_heads = js['remaining_heads']
    m.nuked = boolify(js['nuked'])

    # Time stamp parsing
    m.start_datetime = timestamp_to_datetime(m['round_start_time'])
    m.end_datetime = timestamp_to_datetime(m['round_start_time'])
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
    m.malf_modules = js['malf_modules']

    # Revsquad
    revsquad_won = boolify(js['revsquad-won'])
    revsquad_items

def parse_deaths(js: dict, match: Match):
    for death in js['deaths']:
        d = Death()
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
