"""Old stat file parser, kept as legacy code and unmaintained due to the files no longer being generated."""
import re
from datetime import datetime
from typing import Text

from flask import current_app
from werkzeug import LocalProxy

from app import models

logger = LocalProxy(lambda: current_app.logger)
db = LocalProxy(lambda: current_app.db)


def parse(text, filename):
    """Parse the raw text of a stat file. Requires a file name to check for a duplicate entry."""
    q = db.session.query(models.Match.parsed_file).filter(models.Match.parsed_file == filename)
    try:
        if(q.first()):
                logger.warning(" ~ ~ Duplicate parse entry detected.)\n ~ ~ Request filename: %s" +
                               "\n ~ ~ Stored filename: %s",
                               filename, q.first().parsed_file)
                return False
        else:
                logger.debug('Starting parse of %r' % filename)

        match = models.Match()
        match.parsed_file = filename
        # Regex is in format yyyy-dd-mm
        search_str = '^statistics_((?:19|20)\d{2})[\. .](0[1-9]|[12][0-9]|3[01])[\. .](0[1-9]|1[012])(?:.*)\.txt$'
        file_date = re.search(search_str, filename)
        if file_date is None or len(file_date.groups()) != 3:
            logger.warning('Invalid filename for timestamp: %r' % filename)
            return False
        match.date = datetime.date(int(file_date.group(1)), int(file_date.group(3)), int(file_date.group(2)))
        db.session.add(match)
        try:
            db.session.flush()
        except Exception:
            print("PANIC")
            logger.error('Error flushing DB session: {0}'.format(Exception.message))
            return False
        lines = text.splitlines()
        for line in lines:
            try:
                parse_line(line, match)
            except Exception:
                print("PANIC")
                logger.error('Error parsing line: {0}\n{1}'.format(line, Exception.message))
                db.session.rollback()
                return False
            db.session.flush()
        db.session.commit()
    except Exception:
        logger.error('Error parsing line: {0}\n{1}'.format(line, Exception.message))
        return False
    return True


# Format is YYYY.MM.DD.HH.MM.SS
def format_timestamp(timestamp: Text) -> datetime:
    """Format a timestamp stored in stat files to a DateTime."""
    expected_timestamp_format = '^(\d{4})\.(0?[1-9]|1[012])\.(0?[1-9]|[12][0-9]|3[01])\.(?:(?:([01]?\d|2[0-3])\.)?([0-5]?\d)\.)?([0-5]?\d)$'  # noqa: E501
    searched = re.search(expected_timestamp_format, timestamp)
    year = int(searched.group(1))
    month = int(searched.group(2))
    day = int(searched.group(3))
    hour = int(searched.group(4))
    minute = int(searched.group(5))
    second = int(searched.group(6))

    dated = datetime(year, month, day, hour, minute, second)
    return dated


def parse_line(line: Text, match: models.Match) -> bool:
    """Parse a single line from a stat file."""
    x = line.split('|')
    x = nullparse(x)

    if x[0] in lineParseFunctions:
        lineParseFunctions[x[0]](x, match)
    elif x[0] not in 'WRITE_COMPLETE':
        logger.warning('Unhandled line during parsing: %r\n Full line:\n%r', str(x[0]), '|'.join(x))

    return True


# Someone pointed out that I might have been using this incorrectly, but it's legacy stuff so oh well
def nullparse(s: Text) -> Text:
    """Convert 'null' or empty entries in a statfile line to None."""
    for sstring in s:
        if sstring == '' or sstring.lower() == 'null':
            sstring = None
    return s


def truefalse(s: Text) -> bool:
    """Parse 1/0 to true/false."""
    if s == '1':
        return True
    return False


lineParseFunctions = {}


def lineparse_function(string: Text):
    """Decorate a function so we don't have to type an otherwise cumbersome array addition."""
    def inner(func):
        lineParseFunctions[string] = func
    return inner


@lineparse_function('STATLOG_START')
def lineparse_statlog_start(line: Text, match: models.Match):
    match.data_version = line[1]
    match.mapname = line[2]
    match.start_datetime = format_timestamp(line[3])
    match.end_datetime = format_timestamp(line[4])
    match.round_length = (match.end_datetime - match.start_datetime).total_seconds()


@lineparse_function('MASTERMODE')
def lineparse_mastermode(line: Text, match: models.Match):
    match.mastermode = line[1]


@lineparse_function('GAMEMODE')
def lineparse_gamemode(line: Text, match: models.Match):
    del line[0]
    match.modes_string = '|'.join(line)


@lineparse_function('TECH_TOTAL')
def lineparse_techtotal(line: Text, match: models.Match):
    match.tech_total = line[1]


@lineparse_function('BLOOD_SPILLED')
def lineparse_bloodspilled(line: Text, match: models.Match):
    match.blood_spilled = line[1]


@lineparse_function('CRATES_ORDERED')
def lineparse_crates_ordered(line: Text, match: models.Match):
    match.crates_ordered = line[1]


@lineparse_function('ARTIFACTS_DISCOVERED')
def lineparse_artifacts_discovered(line: Text, match: models.Match):
    match.artifacts_discovered = line[1]


@lineparse_function('CREWSCORE')
def lineparse_crewscore(line: Text, match: models.Match):
    match.crewscore = line[1]


@lineparse_function('NUKED')
def lineparse_nuked(line: Text, match: models.Match):
    match.nuked = truefalse(line[1])


@lineparse_function('ESCAPEES')
def lineparse_escapees(line: Text, match: models.Match):
    match.escapees = line[1]


@lineparse_function('MOB_DEATH')
def lineparse_mobdeath(line: Text, match: models.Match):
    d = models.Death(match_id=match.id)
    d.mindname = nullparse(line[9])
    d.mindkey = nullparse(line[8])
    d.timeofdeath = line[3]
    d.typepath = line[1]
    d.special_role = nullparse(line[2])
    d.last_assailant = line[4]
    d.death_x = line[5]
    d.death_y = line[6]
    d.death_z = line[7]

    db.session.add(d)


@lineparse_function('ANTAG_OBJ')
def lineparse_antagobj(line: Text, match: models.Match):
    a = models.AntagObjective(match_id=match.id)
    a.mindname = nullparse(line[1])
    a.mindkey = nullparse(line[2])
    a.special_role = nullparse(line[3])
    a.objective_type = line[4]
    a.objective_desc = line[6]
    # Check if this is a targeted objective or not.
    if line[5].isdigit():
        a.objective_succeeded = int(line[5])
    else:
        a.objective_succeeded = int(line[8])
        a.target_name = line[7]
        a.target_role = line[6]
    if a.objective_succeeded >= 2:  # Mutiny gives 2 as an additional success value.
        a.objective_succeeded = 1

    db.session.add(a)


@lineparse_function('EXPLOSION')
def lineparse_explosion(line: Text, match: models.Match):
    e = models.Explosion(match_id=match.id)
    e.epicenter_x = line[1]
    e.epicenter_y = line[2]
    e.epicenter_z = line[3]
    e.devestation_range = line[4]
    e.heavy_impact_range = line[5]
    e.light_impact_range = line[6]
    e.max_range = line[7]

    db.session.add(e)


@lineparse_function('UPLINK_ITEM')
def lineparse_uplinkitem(line: Text, match: models.Match):
    u = models.UplinkBuy(match_id=match.id)
    u.mindname = line[2]
    u.mindkey = line[1]
    u.traitor_buyer = truefalse(line[3])
    u.bundle_path = line[4]
    u.item_path = line[5]

    db.session.add(u)


@lineparse_function('BADASS_BUNDLE')
def lineparse_badassbundle(line: Text, match: models.Match):
    bb = models.BadassBundleBuy(match_id=match.id)
    bb.mindname = line[2]
    bb.mindkey = line[1]
    bb.traitor_buyer = truefalse(line[3])

    db.session.add(bb)
    items = line[4]
    for item in items:
        i = models.BadassBundleItem(badass_bundle_id=bb.id)
        i.item_path = item
        db.session.add(i)


@lineparse_function('CULTSTATS')
def lineparse_cultstats(line: Text, match: models.Match):
    match.cult_runes_written = line[1]
    match.cult_runes_fumbled = line[2]
    match.cult_runes_nulled = line[3]
    match.cult_converted = line[4]
    match.cult_tomes_created = line[5]
    match.cult_narsie_summoned = truefalse(line[6])
    match.cult_narsie_corpses_fed = line[7]
    match.cult_surviving_cultists = line[8]
    match.cult_deconverted = line[9]


@lineparse_function('XENOSTATS')
def lineparse_xenostats(line: Text, match: models.Match):
    match.xeno_eggs_laid = line[1]
    match.xeno_faces_hugged = line[2]
    match.xeno_faces_protected = line[3]


@lineparse_function('BLOBSTATS')
def lineparse_blobstats(line: Text, match: models.Match):
    match.blob_wins = line[1]
    match.blob_spawned_blob_players = line[2]
    match.spores_spawned = line[3]
    match.res_generated = line[3]


@lineparse_function('MALFSTATS')
def lineparse_malfstats(line: Text, match: models.Match):
    match.malf_won = line[1]
    match.malf_shunted = line[2]
    match.borgs_at_roundend = line[3]


@lineparse_function('MALFMODULES')
def lineparse_malfmodules(line: Text, match: models.Match):
    del line[0]
    match.malf_modules = '|'.join(line)


@lineparse_function('REVSQUADSTATS')
def lineparse_revsquadstats(line: Text, match: models.Match):
    match.revsquad_won = line[1]
    match.remaining_heads = line[2]


@lineparse_function('POPCOUNT')
def lineparse_popcount(line: Text, match: models.Match):
    pc = models.PopulationSnapshot(match_id=match.id)
    pc.popcount = line[2]
    timestamp_string = line[1]
    # yyyy-mm-dd hh:mm:ss
    timestamp_pattern = '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})'
    timestamp_regex = re.search(timestamp_pattern, timestamp_string)

    year = int(timestamp_regex.group(1))
    month = int(timestamp_regex.group(2))
    day = int(timestamp_regex.group(3))
    hour = int(timestamp_regex.group(4))
    minute = int(timestamp_regex.group(5))
    second = int(timestamp_regex.group(6))

    timestamp_dt = datetime(year, month, day, hour, minute, second)
    pc.time = timestamp_dt

    db.session.add(pc)
