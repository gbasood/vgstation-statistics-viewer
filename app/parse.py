"""This file handles code for parsing CSV-formatted statfiles into the database."""
from __future__ import unicode_literals
import os
import fnmatch
import shutil
import sys
import datetime
import re
from app import app, models, db
from config import STATS_DIR, PROCESSED_DIR, UNPARSABLE_DIR

database_busy = False


def batch_parse():
    """Parse all statfiles in configured directory."""
    parsed = 0
    errored = 0

    database_busy = False  # Just in case

    if not os.path.exists(STATS_DIR):
        app.logger.debug('!! ERROR: Statfile dir path is invalid. Path used: ' + STATS_DIR)
        return -1
    for file in os.listdir(STATS_DIR):
        if fnmatch.fnmatch(file, 'statistics_*.txt'):
            try:
                parse_file(os.path.join(STATS_DIR, file))
                parsed += 1
                shutil.move(os.path.join(STATS_DIR, file), os.path.join(PROCESSED_DIR, file))
            except:
                if database_busy:
                    app.logger.warning('Could not write file changes: database busy. Try again later.')
                    return 530
                app.logger.error('!! ERROR: File could not be parsed. Details: \n${0}'.format(str(sys.exc_info()[0])))
                errored += 1
                shutil.move(os.path.join(STATS_DIR, file), os.path.join(UNPARSABLE_DIR, file))
                raise

    app.logger.debug('# DEBUG: Batch parsed ' + str(parsed) + ' files with ' + str(errored) + ' exceptions.')


def parse_file(path):
    """Parse the contents of a CSV statfile."""
    if not os.path.exists(path):
        app.logger.error('!! ERROR: Tried to parse non-existant path ' + str(path))
        return False
    f = open(path, 'r+')
    contents = f.read()
    f.close()
    filename = os.path.basename(path)
    return parse(contents, filename)


# def parse_url(url):
#     """Parse the contents of a plain text statfile located at public-facing URL. Unused."""
#     r = requests.get(url)
#     if r.status_code != 200:
#         return flask.make_response("ERROR - We were denied access to the URL supplied.", 500)
#     else:
#         # Generate a Match model and store it in the session. This gives us
#         # access to a valid match ID so the other models can be stored properly
#         filename = os.path.basename(url)
#         parseResult = parse(r.text, filename)
#         if parseResult:
#             app.logger.debug("PARSED %r" % filename)
#             return flask.make_response("OK", 200)
#         else:
#             return flask.make_response("DUPLICATE ENTRY", 500)


def parse(text, filename):
    """Parse the raw text of a stat file. Requires a file name to check for a duplicate entry."""
    q = db.session.query(models.Match.parsed_file).filter(models.Match.parsed_file == filename)
    if(q.first()):
        app.logger.warning(" ~ ~ Duplicate parse entry detected.)\n ~ ~ Request filename: %s\n ~ ~ Stored filename: %s",
                           filename, q.first().parsed_file)
        return False
    else:
        app.logger.debug('Starting parse of %r' % filename)

    match = models.Match()
    match.parsed_file = filename
    # Regex is in format yyyy-dd-mm
    search_str = '^statistics_((?:19|20)\d{2})[\. .](0[1-9]|[12][0-9]|3[01])[\. .](0[1-9]|1[012])(?:.*)\.txt$'
    file_date = re.search(search_str, filename)
    if file_date is None or len(file_date.groups()) != 3:
        app.logger.warning('Invalid filename for timestamp: %r' % filename)
        return False
    match.date = datetime.date(int(file_date.group(1)), int(file_date.group(3)), int(file_date.group(2)))
    db.session.add(match)
    try:
        db.session.flush()
    except:
        # database_busy = True
        return False
    lines = text.splitlines()
    for line in lines:
        try:
            parse_line(line, match)
        except:
            app.logger.error('Error parsing line: %r' % line)
            db.session.rollback()
            raise
            return
        db.session.flush()
    db.session.commit()
    return True


# Format is YYYY.MM.DD.HH.MM.SS
def format_timestamp(timestamp):
    """Format a timestamp stored in stat files to a DateTime."""
    expected_timestamp_format = '^(\d{4})\.(0?[1-9]|1[012])\.(0?[1-9]|[12][0-9]|3[01])\.(?:(?:([01]?\d|2[0-3])\.)?([0-5]?\d)\.)?([0-5]?\d)$'
    searched = re.search(expected_timestamp_format, timestamp)
    year = int(searched.group(1))
    month = int(searched.group(2))
    day = int(searched.group(3))
    hour = int(searched.group(4))
    minute = int(searched.group(5))
    second = int(searched.group(6))

    dated = datetime.datetime(year, month, day, hour, minute, second)
    return dated


def parse_line(line, match):
    """Parse a single line from a stat file."""
    x = line.split('|')
    x = nullparse(x)

    if x[0] == 'STATLOG_START':
        match.data_version = x[1]
        match.mapname = x[2]
        match.starttime = x[3]
        match.endtime = x[4]
        if float(match.data_version) >= 1.1:
            match.start_datetime = format_timestamp(match.starttime)
            match.end_datetime = format_timestamp(match.endtime)
            match.round_length = (match.end_datetime - match.start_datetime).total_seconds()
            # TODO: Test this once PR merges
    elif x[0] == 'MASTERMODE':
        match.mastermode = x[1]
    elif x[0] == "GAMEMODE":
        prefix = len("GAMEMODE|")
        match.modes_string = line[prefix:]
        match.modes_string = match.modes_string
    elif x[0] == "TECH_TOTAL":
        match.tech_total = x[1]
    elif x[0] == "BLOOD_SPILLED":
        match.blood_spilled = x[1]
    elif x[0] == "CRATES_ORDERED":
        match.crates_ordered = x[1]
    elif x[0] == "ARTIFACTS_DISCOVERED":
        match.artifacts_discovered = x[1]
    elif x[0] == "CREWSCORE":
        match.crewscore = x[1]
    elif x[0] == "NUKED":
        match.nuked = truefalse(x[1])
    elif x[0] == "ESCAPEES":
        match.escapees = x[1]
    elif x[0] == "MOB_DEATH":
        d = models.Death(match_id=match.id)
        d.mindname = nullparse(x[9])
        d.mindkey = nullparse(x[8])
        d.timeofdeath = x[3]
        d.typepath = x[1]
        d.special_role = x[2]
        d.last_assailant = x[4]
        d.death_x = x[5]
        d.death_y = x[6]
        d.death_z = x[7]

        db.session.add(d)
    elif x[0] == "ANTAG_OBJ":
        a = models.AntagObjective(match_id=match.id)
        a.mindname = nullparse(x[1])
        a.mindkey = nullparse(x[2])
        a.special_role = x[3]
        a.objective_type = x[4]
        a.objective_desc = x[6]
        # Check if this is a targeted objective or not.
        if x[5].isdigit():
            a.objective_succeeded = int(x[5])
        else:
            a.objective_succeeded = int(x[8])
            a.target_name = x[7]
            a.target_role = x[6]
        if a.objective_succeeded >= 2:  # Mutiny gives 2 as an additional success value.
            a.objective_succeeded = 1
        db.session.add(a)
    elif x[0] == "EXPLOSION":
        e = models.Explosion(match_id=match.id)
        e.epicenter_x = x[1]
        e.epicenter_y = x[2]
        e.epicenter_z = x[3]
        e.devestation_range = x[4]
        e.heavy_impact_range = x[5]
        e.light_impact_range = x[6]
        e.max_range = x[7]

        db.session.add(e)
    elif x[0] == "UPLINK_ITEM":
        u = models.UplinkBuy(match_id=match.id)
        u.mindname = x[2]
        u.mindkey = x[1]
        u.traitor_buyer = truefalse(x[3])
        u.bundle_path = x[4]
        u.item_path = x[5]

        db.session.add(u)
    elif x[0] == "BADASS_BUNDLE":
        bb = models.BadassBundleBuy(match_id=match.id)
        bb.mindname = x[2]
        bb.mindkey = x[1]
        bb.traitor_buyer = truefalse(x[3])

        db.session.add(bb)
        items = x[4]
        for item in items:
            i = models.BadassBundleItem(badass_bundle_id=bb.id)
            i.item_path = item
            db.session.add(i)
    elif x[0] == "CULTSTATS":
        c = models.CultStats(match_id=match.id)
        c.runes_written = x[1]
        c.runes_fumbled = x[2]
        c.runes_nulled = x[3]
        c.converted = x[4]
        c.tomes_created = x[5]
        c.narsie_summoned = truefalse(x[6])
        c.narsie_corpses_fed = x[7]
        c.surviving_cultists = x[8]
        c.deconverted = x[9]

        db.session.add(c)
    elif x[0] == "XENOSTATS":
        xn = models.XenoStats(match_id=match.id)
        xn.eggs_laid = x[1]
        xn.faces_hugged = x[2]
        xn.faces_protected = x[3]

        db.session.add(xn)
    elif x[0] == 'BLOBSTATS':
        bs = models.BlobStats(match_id=match.id)
        bs.blob_wins = x[1]
        bs.spawned_blob_players = x[2]
        bs.spores_spawned = x[3]
        bs.res_generated = x[3]

        db.session.add(bs)
    elif x[0] == 'MALFSTATS':
        ms = models.MalfStats(match_id=match.id)
        ms.malf_won = x[1]
        ms.malf_shunted = x[2]
        ms.borgs_at_roundend = x[3]

        db.session.add(ms)
    elif x[0] == 'MALFMODULES':
        try:
            match.malfstat.malf_modules = '|'.join(x.pop(0))
        except:
            raise
    elif x[0] == 'REVSQUADSTATS':
        rss = models.RevsquadStats(match_id=match.id)
        rss.revsquad_won = x[1]
        rss.remaining_heads = x[2]

        db.session.add(rss)
    elif x[0] == 'POPCOUNT':
        pc = models.PopulationSnapshot(match_id=match.id)
        pc.popcount = x[2]
        timestamp_string = x[1]
        # yyyy-mm-dd hh:mm:ss
        timestamp_pattern = '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})'
        timestamp_regex = re.search(timestamp_pattern, timestamp_string)

        year = int(timestamp_regex.group(1))
        month = int(timestamp_regex.group(2))
        day = int(timestamp_regex.group(3))
        hour = int(timestamp_regex.group(4))
        minute = int(timestamp_regex.group(5))
        second = int(timestamp_regex.group(6))

        timestamp_dt = datetime.datetime(year, month, day, hour, minute, second)
        pc.time = timestamp_dt

        db.session.add(pc)
    return True


def nullparse(s):
    """Convert 'null' or empty entries in a statfile line to None."""
    for sstring in s:
        if sstring == '' or sstring.lower() == 'null':
            sstring = None
    return s


def truefalse(s):
    """Parse 1/0 to true/false."""
    if s == '1':
        return True
    return False
