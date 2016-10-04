import string, requests, flask, os, fnmatch, shutil, sys, datetime, re
import app
from app import models, db
from config import STATS_DIR, PROCESSED_DIR, UNPARSABLE_DIR

def batch_parse():
    parsed = 0
    errored = 0

    if not os.path.exists(STATS_DIR):
        app.logger.debug('!! ERROR: Statfile dir path is invalid. Path used: ' + STATS_DIR)
        return 1
    for file in os.listdir(STATS_DIR):
        if fnmatch.fnmatch(file, 'statistics_*.txt'):
            try:
                parse_file(os.path.join(STATS_DIR, file))
                parsed+=1
                shutil.move(os.path.join(STATS_DIR, file), os.path.join(PROCESSED_DIR, file))
            except:
                app.logger.debug('!! ERROR: File could not be parsed. Details:\n', sys.exc_info()[0])
                errored+=1
                shutil.move(os.path.join(STATS_DIR, file), os.path.join(UNPARSABLE_DIR, file))
                raise


    app.logger.debug('# DEBUG: Batch parsed ' + str(parsed) + ' files with ' + str(errored) + ' exceptions.')

def parse_file(path):
    if not os.path.exists(path):
        app.logger.error('!! ERROR: Tried to parse non-existant path ' + str(path) )
        return
    f = open(path, 'r+')
    contents = f.read()
    f.close()
    filename = os.path.basename(path)
    parse(contents, filename)

def parse_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return flask.make_response("ERROR - We were denied access to the URL supplied.", 500)
    else:
        # Generate a Match model and store it in the session. This gives us
        # access to a valid match ID so the other models can be stored properly
        filename = os.path.basename(url)
        parseResult = parse(r.text, filename)
        if parseResult:
            app.logger.debug("PARSED %r" % filename)
            return flask.make_response("OK", 200)
        else:
            return flask.make_response("DUPLICATE ENTRY", 500)

def parse(text, filename):
    q = db.session.query(models.Match.parsed_file).filter(models.Match.parsed_file == filename)
    if(q.first()):
        app.logger.warning(""" ~ ~ Duplicate parse entry detected.)
                            ~ ~ Request filename: """ + filename +
                        '\n ~ ~ Stored filename: ' + q.first().parsed_file)
        return False
    else:
        app.logger.debug('Starting parse of %r' % filename)

    match = models.Match()
    match.parsed_file = filename
    # Regex is in format yyyy-dd-mm
    file_date = re.search('^statistics_((?:19|20)\d{2})[\. .](0[1-9]|[12][0-9]|3[01])[\. .](0[1-9]|1[012])(?:.*)\.txt$', filename)
    match.date = datetime.date(int(file_date.group(1)), int(file_date.group(3)), int(file_date.group(2)))
    db.session.add(match)
    db.session.flush()

    lines = text.splitlines()
    for line in lines:
        parse_line(line, match)
        db.session.flush()
    db.session.commit()
    return True

def parse_line(line, match):
    w = line.decode("utf-8",errors='ignore')
    x = w.split('|')
    x = nullparse(x)

    if x[0] == 'STATLOG_START':
        match.data_version = x[1].encode('ascii')
        match.mapname = x[2].encode('ascii')
        match.starttime = x[3].encode('ascii')
        match.endtime = x[4].encode('ascii')
        if float(match.data_version) >= 1.1:
            # Format is YYYY.MM.DD.HH.MM.SS
            expected_timestamp_format = '^(\d{4})\.(0?[1-9]|1[012])\.(0?[1-9]|[12][0-9]|3[01])\.(?:(?:([01]?\d|2[0-3])\.)?([0-5]?\d)\.)?([0-5]?\d)$'
            start_reg = re.search(expected_timestamp_format, match.starttime)
            end_reg = re.search(expected_timestamp_format, match.endtime)
            start_datetime = datetime.datetime(int(start_reg.group(1)),int(start_reg.group(2)),int(start_reg.group(3)),int(start_reg.group(4)),int(start_reg.group(5)),int(start_reg.group(6)))
            end_datetime = datetime.datetime(int(end_reg.group(1)),int(end_reg.group(2)),int(end_reg.group(3)),int(end_reg.group(4)),int(end_reg.group(5)),int(end_reg.group(6)))
            match.round_length = (end_datetime - start_datetime).total_seconds()
            # TODO: Test this once PR merges
    elif x[0] == 'MASTERMODE':
        match.mastermode = x[1].encode('ascii')
    elif x[0] == "GAMEMODE":
        prefix = len("GAMEMODE|")
        match.modes_string = w[prefix:]
        match.modes_string= match.modes_string.encode('ascii')
    elif x[0] == "TECH_TOTAL":
        match.tech_total = x[1].encode('ascii')
    elif x[0] == "BLOOD_SPILLED":
        match.blood_spilled = x[1].encode('ascii')
    elif x[0] == "CRATES_ORDERED":
        match.crates_ordered = x[1].encode('ascii')
    elif x[0] == "ARTIFACTS_DISCOVERED":
        match.artifacts_discovered = x[1].encode('ascii')
    elif x[0] == "CREWSCORE":
        match.crewscore = x[1].encode('ascii')
    elif x[0] == "NUKED":
        match.nuked = truefalse(x[1])
    elif x[0] == "ESCAPEES":
        match.escapees = x[1].encode('ascii')
    elif x[0] == "MOB_DEATH":
        d = models.Death(match_id = match.id)
        d.mindname=nullparse(x[9]).encode('ascii')
        d.mindkey=nullparse(x[8]).encode('ascii')
        d.timeofdeath=x[3].encode('ascii')
        d.typepath=x[1].encode('ascii')
        d.special_role=x[2].encode('ascii')
        d.last_assailant=x[4].encode('ascii')
        d.death_x=x[5].encode('ascii')
        d.death_y=x[6].encode('ascii')
        d.death_z=x[7].encode('ascii')

        db.session.add(d)
    elif x[0] == "ANTAG_OBJ":
        a = models.AntagObjective(match_id = match.id)
        a.mindname = nullparse(x[1]).encode('ascii')
        a.mindkey = nullparse(x[2]).encode('ascii')
        a.special_role = x[3].encode('ascii')
        a.objective_type = x[4].encode('ascii')
        a.objective_desc = x[6].encode('ascii')
        # Check if this is a targeted objective or not.
        if x[5].isdigit():
            a.objective_succeeded = int(x[5].encode('ascii'))
        else:
            a.objective_succeeded = int(x[8].encode('ascii'))
            a.target_name = x[7].encode('ascii')
            a.target_role = x[6].encode('ascii')
        if a.objective_succeeded >= 2: # Mutiny gives 2 as an additional success value.
            a.objective_succeeded = 1
        db.session.add(a)
    elif x[0] == "EXPLOSION":
        e = models.Explosion(match_id = match.id)
        e.epicenter_x = x[1].encode('ascii')
        e.epicenter_y = x[2].encode('ascii')
        e.epicenter_z = x[3].encode('ascii')
        e.devestation_range  = x[4].encode('ascii')
        e.heavy_impact_range = x[5].encode('ascii')
        e.light_impact_range = x[6].encode('ascii')
        e.max_range = x[7].encode('ascii')

        db.session.add(e)
    elif x[0] == "UPLINK_ITEM":
        u = models.UplinkBuy(match_id = match.id)
        u.mindname = x[2].encode('ascii')
        u.mindkey = x[1].encode('ascii')
        u.traitor_buyer = truefalse(x[3])
        u.bundle_path = x[4].encode('ascii')
        u.item_path = x[5].encode('ascii')

        db.session.add(u)
    elif x[0] == "BADASS_BUNDLE":
        bb = models.BadassBundleBuy(match_id = match.id)
        bb.mindname = x[2].encode('ascii')
        bb.mindkey = x[1].encode('ascii')
        bb.traitor_buyer = truefalse(x[3])

        db.session.add(bb)
        items = x[4].encode('ascii')
        for item in items:
            i = models.BadassBundleItem(badass_bundle_id = bb.id)
            i.item_path = item
            db.session.add(i)
    elif x[0] == "CULTSTATS":
        c = models.CultStats(match_id = match.id)
        c.runes_written = x[1].encode('ascii')
        c.runes_fumbled = x[2].encode('ascii')
        c.runes_nulled = x[3].encode('ascii')
        c.converted = x[4].encode('ascii')
        c.tomes_created = x[5].encode('ascii')
        c.narsie_summoned = truefalse(x[6])
        c.narsie_corpses_fed = x[7].encode('ascii')
        c.surviving_cultists = x[8].encode('ascii')
        c.deconverted = x[9].encode('ascii')

        db.session.add(c)
    elif x[0] == "XENOSTATS":
        xn = models.XenoStats(match_id = match.id)
        xn.eggs_laid = x[1].encode('ascii')
        xn.faces_hugged = x[2].encode('ascii')
        xn.faces_protected = x[3].encode('ascii')

        db.session.add(xn)
    elif x[0] == 'BLOBSTATS':
        bs = models.BlobStats(match_id = match.id)
        bs.blob_wins = x[1].encode('ascii')
        bs.spawned_blob_players = x[2].encode('ascii')
        bs.spores_spawned = x[3].encode('ascii')
        bs.res_generated = x[3].encode('ascii')

        db.session.add(bs)
    elif x[0] == 'MALFSTATS':
        ms = models.MalfStats(match_id = match.id)
        ms.malf_won = x[1].encode('ascii')
        ms.malf_shunted = x[2].encode('ascii')
        ms.borgs_at_roundend = x[3].encode('ascii')

        db.session.add(ms)
    elif x[0] == 'MALFMODULES':
        try:
            match.malfstat.malf_modules = '|'.join(x.pop(0))
        except:
            raise
    return True

def nullparse(s):
    for string in s:
        if string == '' or string.lower() == 'null':
            string = None
    return s

# Parses 1/0 to true/false
def truefalse(s):
    if s == '1':
        return True
    return False
