"""This file contains code that handles logic for displaying global stats on the global stats view.

This includes queries, logical operations, and formatting so that the view can render it as a readable graph.
"""

from __future__ import unicode_literals

import json

from sqlalchemy import and_, func
# from sqlalchemy import between
from werkzeug.contrib.cache import SimpleCache

from app import models
from app.app import logging
from app.helpers import add_months

from flask import current_app
from werkzeug import LocalProxy

cache = SimpleCache()

antag_objective_victory_modes = ["traitor+changeling", "double agents", "autotraitor", "changeling",
                                 "vampire", 'wizard', 'ragin\' mages', 'revolution']
do_not_show = ['extended', 'heist', 'meteor']
objective_success_threshold = 0.49


class MatchTypeVictory:
    """Simple container for match victory data."""

    victory = False
    secret = False
    mode = None

    def __init__(self, v, s, m):
        """Constructor.

        Parameters:
        v(boolean): Whether or not the match was an antag victory.
        s(boolean): Whether or not the match mode was secret.
        m(string):  What mode the match was.
        """
        if v:
            self.victory = v
        if s:
            self.secret = s
        if m:
            self.mode = m

    def __str__(self):
        """Return string representation for debug purposes."""
        return 'Mode: %s Victory: %s Secret: %s' % (self.mode, self.victory, self.secret)


def get_formatted_global_stats(timespan):
    """Return a big ol' object that contains all the matches in two separate arrays of JSON."""  # TODO more doc
    (winrateStats, allMatches, counts) = get_global_stats(timespan)
    # winrateStats = stats[0]
    # allMatches = stats[1]

    allplayed = []

    matchData = {}
    matchData['types'] = json.dumps(list(winrateStats.keys()), ensure_ascii=True)
    matchData['matches'] = json.dumps(winrateStats, ensure_ascii=True)
    wins = []
    losses = []
    for mode in winrateStats:
        wins.append(winrateStats[mode]['wins'])
        losses.append(winrateStats[mode]['losses'])
    for mode in allMatches:
        allplayed.append(allMatches[mode])
    matchData['wins'] = json.dumps(wins, ensure_ascii=True)
    matchData['losses'] = json.dumps(losses, ensure_ascii=True)
    matchData['all'] = json.dumps(allplayed, ensure_ascii=True)
    matchData['alltypes'] = json.dumps(list(allMatches.keys()), ensure_ascii=True)

    return matchData, counts


def get_global_stats(timespan):
    """Handle the querying of match win/loss info. Returns an array of match types."""
    victories = dict()
    all_matches = dict()
    counts = None

    cachestring = "globalstatsalltime"
    if timespan[0] != "all":
        cachestring = 'globalstats{}{}'.format(timespan[1].year, timespan[1].month)

    q = cache.get(cachestring)

    if q is None:
        logging.debug('Cache miss on globalstats')

        m, counts = match_stats(timespan)
        for match in m:
            # Pie chart data
            if match.mode not in all_matches:
                all_matches[match.mode] = 1
            else:
                all_matches[match.mode] = all_matches[match.mode] + 1

        # Global winrate
            if match.mode.lower() in do_not_show:
                continue
            if match.mode not in victories:
                victories[match.mode] = {'wins': 0, 'losses': 0}
                victories[match.mode]['wins'] = 0
                victories[match.mode]['losses'] = 0
            if match.victory is True:
                victories[match.mode]['wins'] = victories[match.mode]['wins'] + 1
            else:
                victories[match.mode]['losses'] = victories[match.mode]['losses'] + 1

        cache.set(cachestring, (victories, all_matches, counts), timeout=15 * 60)  # 15 minutes
    else:
        victories, all_matches, counts = q
        logging.debug('Cache hit on globalstats')

    return victories, all_matches, counts


def match_stats(timespan):
    """
    Return all match victories/losses that match timespan.

    Return all matches that match timespan. Then checks the match's victory conditions in checkModeVictory.

    Parameters:
        timespan(tuple): Three-part tuple. First part is "monthly" or "all".
        Second part is a datetime with month and year as the starting month.

    Returns:
        array: Array of MatchTypeVictory.

    """
    db = LocalProxy(lambda: current_app.db.session)
    q = models.Match.query
    timespan_criteria = None
    count_query = db.query(models.Match.modes_string, func.count(models.Match.id))
    if timespan[0] != "all":
        query_start = timespan[1]
        query_end = add_months(query_start, 1)
        print(query_start, query_end)
        timespan_criteria = and_(models.Match.start_datetime is not None,
                                 models.Match.start_datetime.between(query_start, query_end))
        q = q.filter(timespan_criteria)
        count_query = count_query.filter(timespan_criteria)

    # completion-agnostic playrate first

    counts = count_query.group_by(models.Match.modes_string).all()
    formattedCounts = [list(a) for a in (zip(*counts))]

    q = q.filter(~models.Match.modes_string.contains('|'), ~models.Match.mastermode.contains('mixed'))
    q = q.all()

    matches = []

    for match in q:
        if match.is_mixed():
            continue
        victory = checkModeVictory(match)
        if victory is None:
            continue
        s = True if match.mastermode == "secret" else False
        t = match.modes_string
        m = MatchTypeVictory(victory, s, t)
        matches.append(m)
    return matches, formattedCounts


def checkModeVictory(match):
    """Given a Match model instance, returns whether the antags were succesful or not."""
    modestring = match.modes_string.lower()
    if modestring == "nuclear emergency" in modestring:
        if match.nuked is True:
            return True
        else:
            return False
    elif "cult" in modestring:
        if match.cult_narsie_summoned is True:
            return True
        else:
            return False
    elif "meteor" in modestring:
        return False  # No one wins in meteor let's be honest
    elif "blob" in modestring:
        return match.blob_wins
    elif "ai malfunction" in modestring:
        return match.malf_won
    elif "revolution squad" in modestring:
        return match.revsquad_won
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
