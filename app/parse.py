import string, requests, flask, os
from app import models, db

def parse_url(url):
    r = requests.get(url)
    print(r.status_code)
    if r.status_code != 200:
        return flask.make_response("ERROR", 500)
    else:
        # Generate a Match model and store it in the session. This gives us
        # access to a valid match ID so the other models can be stored properly
        filename = os.path.basename(url)
        q = db.session.query(models.Match.id).filter(models.Match.parsed_file == filename)
        if(q.first()):
            print(' ~ ~ Duplicate parse entry detected.')
            print(' Request filename:' + filename)
            print(' Stored filename:' + q.first().parsed_file)
            return flask.make_response("DUPLICATE ENTRY", 500)

        match = models.Match()
        match.parsed_file = filename
        db.session.add(match)

        lines = r.iter_lines()
        for line in lines:
            parse_line(line, match)

        print("PARSED")
        return flask.make_response("OK", 200)

def parse_line(line, match):
    w = line.decode("utf-8")
    x = w.split('|')
    x = nullparse(x)

    if x[0] == 'STATLOG_START':
        match.data_version = x[1].encode('ascii').encode('ascii')
        match.mapname = x[2].encode('ascii').encode('ascii')
        match.starttime = x[3].encode('ascii').encode('ascii')
        match.endtime = x[4].encode('ascii').encode('ascii')
    elif x[0] == 'MASTERMODE':
        match.mastermode = x[1].encode('ascii').encode('ascii')
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
        # d.realname=x[10]

        db.session.add(d)
    elif x[0] == "ANTAG_OBJ":
        a = models.AntagObjective(match_id = match.id)
        a.mindname = nullparse(x[1])
        a.mindkey = nullparse(x[2])
        a.special_role = x[3].encode('ascii')
        a.objective_type = x[4].encode('ascii')
        a.objective_desc = x[6].encode('ascii')
        # Check if this is a targeted objective or not.
        if x[5].isdigit():
            a.objective_succeeded = x[5].encode('ascii')
        else:
            a.objective_succeeded = x[8].encode('ascii')
            a.target_name = x[7].encode('ascii')
            a.target_role = x[6].encode('ascii')
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

    db.session.commit()
    return None

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

# Because BYOND's epoch isn't the same as linux epoch woo
def timeparse():
    epoch = datetime.datetime(2000, 1, 1)
