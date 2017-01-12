from __future__ import unicode_literals
from app import models, db, logging
from app.helpers import add_months
from sqlalchemy import and_
from werkzeug.contrib.cache import SimpleCache
import datetime
import json

cache = SimpleCache()

antag_objective_victory_modes = ["traitor+changeling", "double agents", "autotraitor", "changeling", "vampire", 'wizard', 'ragin\' mages', 'revolution']
do_not_show = ['extended', 'heist', 'meteor']
objective_success_threshold = 0.49

class MatchTypeVictory:
    victory = False
    secret = False
    mode = None

    def __init__(self, v, s, m):
        if v:
            self.victory = v
        if s:
            self.secret = s
        if m:
            self.mode = m

    def __str__(self):
        return 'Mode: %s Victory: %s Secret: %s' % (self.mode, self.victory, self.secret)

def get_formatted_global_stats(timespan):
    stats = get_global_stats(timespan)

    matchData = {}
    matchData['types'] = json.dumps(list(stats.keys()), ensure_ascii=True)
    matchData['matches'] = json.dumps(stats, ensure_ascii=True)
    wins = []
    losses = []
    for mode in stats:
        wins.append(stats[mode]['wins'])
        losses.append(stats[mode]['losses'])
    matchData['wins'] = json.dumps(wins, ensure_ascii=True)
    matchData['losses'] = json.dumps(losses, ensure_ascii=True)
    return matchData


def get_global_stats(timespan):

    victories = dict()
    total = dict()
    cachestring = "globalstatsalltime"
    if timespan[0]!="all":
        cachestring = 'globalstats{}{}'.format(timespan[1].year, timespan[1].month)

    q = cache.get(cachestring)

    if q is None:
        logging.debug('Cache miss on globalstats')

        m = match_stats(timespan)
        for match in m:
            if match.mode not in victories:
                victories[match.mode] = {'wins': 0, 'losses': 0}
                victories[match.mode]['wins'] = 0
                victories[match.mode]['losses'] = 0
            if match.victory is True:
                victories[match.mode]['wins'] = victories[match.mode]['wins'] + 1
            else:
                victories[match.mode]['losses'] = victories[match.mode]['losses'] + 1

        cache.set(cachestring, victories, timeout=15 * 60)  # 15 minutes
    else:
        victories = q
        logging.debug('Cache hit on globalstats')
    return victories


def match_stats(timespan):
    """
    Returns all match victories/losses that match timespan.

    Returns all matches that match timespan. Then checks the match's victory conditions in checkModeVictory.

    Parameters
    ----------
    timespan : tuple
        Three-part tuple. First part is "monthly" or "all". Second part is a datetime with month and year as the starting month.

    Returns
    -------
    Array of MatchTypeVictory.

    """
    q = models.Match.query
    if timespan[0] != "all": #TODO add browsing through dates that aren't  the current date
        query_start = timespan[1]
        query_end = add_months(query_start, 1)

        q =q.filter(and_(models.Match.date is not None, models.Match.date >= query_start, models.Match.date < query_end))

    q = q.filter(~models.Match.modes_string.contains('|'), ~models.Match.mastermode.contains('mixed'))
    q = q.all()

    matches = []

    for match in q:
        if match.modes_string.lower() in do_not_show:
            continue
        if match.is_mixed():
            continue
        victory = checkModeVictory(match)
        if victory is None:
            continue
        s = True if match.mastermode == "secret" else False
        t = match.modes_string
        m = MatchTypeVictory(victory, s, t)
        matches.append(m)
    return matches


def checkModeVictory(match):
    modestring = match.modes_string.lower()
    if modestring == "nuclear emergency" in modestring:
        if match.nuked is True:
            return True
        else:
            return False
    elif "cult" in modestring:
        if match.cultstat.narsie_summoned is True:
            return True
        else:
            return False
    elif "meteor" in modestring:
        return False  # No one wins in meteor let's be honest
    elif "blob" in modestring:
        if match.blobstat:
            return match.blobstat.blob_wins
        else:
            return None
    elif "ai malfunction" in modestring:
        if match.malfstat:
            return match.malfstat.malf_won
        else:
            return None
    elif "revolution squad" in modestring:
        if match.revsquadstat:
            return match.revsquadstat.revsquad_won
        else:
            return None
    elif any(modestring in s for s in antag_objective_victory_modes):
        succeeded = 0
        total = 0
        for objective in match.antagobjs:
            total += 1
            if objective.objective_succeeded:
                succeeded += 1
        if succeeded == 0:
            return False
        elif total == 0:
            return False
        ratio = float(succeeded) / float(total)
        if ratio >= objective_success_threshold:
            return True
        else:
            return False
