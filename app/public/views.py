"""View routing."""

import calendar
import datetime
import json
import os
import threading

import flask
from flask import (Blueprint, current_app, redirect, render_template, redirect,
                   request, url_for)
from sqlalchemy import func

from app import global_stats, parse
from app.helpers import add_months
from app.models import AntagObjective, Death, Explosion, Match, PopulationSnapshot as PopSnap, db
from config import basedir

blueprint = Blueprint('blueprint', __name__, static_folder='static')


@blueprint.route('/')
@blueprint.route('/index')
def index():
    """Respond with view for index page."""
    matchesTotal = Match.query.count()
    if matchesTotal is 0:
        matchesTotal = 1
    explosionratio = Explosion.query.count() / float(matchesTotal)
    deathratio = Death.query.count() / float(matchesTotal)
    nuked = Match.query.filter(Match.nuked).count()
    lastmatch = Match.query.order_by(Match.id.desc()).first()

    startdate = datetime.datetime.now()
    enddate = startdate - datetime.timedelta(days=30)
    mapPlayrate = db.session.query(Match.mapname, func.count(Match.id))\
    .group_by(Match.mapname)\
    .filter(
        Match.starttime <= startdate,
        Match.starttime >= enddate
    )\
    .all()

    mapPlayrate = db.session.query(Match.mapname, func.count(Match.id)).group_by(Match.mapname).all()
    # Map percentage
    # for mapx in matchCounts:
    #     mapx[1] = mapx[1] / float(matchesTotal) * 100

    return render_template('index.html', matchcount=matchesTotal, nukedcount=nuked, explosionratio=explosionratio,
                           deathratio=deathratio, lastmatch=lastmatch,
                           mapPlayrate=mapPlayrate)

# @blueprint.route('/import')
# def test():
#     url='http://game.ss13.moe/stats/statistics_2016.31.01.7.txt'
#     if request.args.get('url'):
#         url = request.args.get('url')
#         print(url)
#     return parse.parse_url(url)


@blueprint.route('/matchlist')
@blueprint.route('/matchlist/<int:page>')
def matchlist(page=1):
    """Respond with view for paginated match list."""
    query = Match.query.order_by(Match.id.desc())
    paginatedMatches = query.paginate(page, current_app.config['MATCHES_PER_PAGE'], False)
    return render_template('matchlist.html', matches=paginatedMatches.items, pagination=paginatedMatches)


@blueprint.route('/global')
def globalpage():
    return render_template('global.html')

@blueprint.route('/global/gamemode')
def globalgamemodes(timespan="monthly", month=None, year=None):
    """Respond with view for global statistics for gamemodes, with optional timespan grouping. Currently only all time or by month."""
    query_timespan = request.args.get("timespan") if request.args.get("timespan") else "monthly"
    request_month = int(request.args.get("month") if request.args.get("month") else datetime.datetime.now().month)
    request_year = int(request.args.get("year") if request.args.get("year") else datetime.datetime.now().year)
    request_starttime = datetime.datetime(year=request_year, month=request_month, day=1)

    request_timespan = (query_timespan, request_starttime)
    next_page = add_months(request_starttime, 1)
    prev_page = add_months(request_starttime, -1)
    (stats, counts) = global_stats.get_formatted_global_stats(request_timespan)
    return render_template('globalstats.html', matchData=stats,
                           timespan=query_timespan,
                           query_start=request_starttime,
                           matchCounts=counts,
                           nextpage=next_page,
                           prevpage=prev_page)

@blueprint.route('/global/population')
def globalpopulation():
    """Respond with view for global statitics for population, chunked by hour, over the course of the last 30 days."""
    startdate = datetime.datetime.now()
    enddate = startdate - datetime.timedelta(days=30)
    q = db.session.query(
        func.avg(PopSnap.popcount),
        func.strftime('%H', PopSnap.time)
    ).filter(
        PopSnap.time <= startdate,
        PopSnap.time >= enddate
    ).group_by(func.strftime('%H', PopSnap.time)).all()
    counts = [el[0] for el in q] # first piece of each grouped result
    hours = [el[1] for el in q] # second piece of each grouped result
    return render_template('populationstats.html', counts=counts, hours=hours)


@blueprint.route('/globalstats')
def globalstats_redir():
    return redirect(url_for(".globalpage"))

@blueprint.route('/match/latest')
def latest_match():
    """Redirect to latest match."""
    lastmatch = Match.query.order_by(Match.id.desc()).first()
    return redirect(url_for('blueprint.match', id=lastmatch.id))


@blueprint.route('/match/<id>')
def match(id=0):
    """Respond with view for a match."""
    match = Match.query.get(id)
    if match is not None:
        return render_template('match.html', match=Match.query.get(id))
    abort(404)


# This is the route that the bot will use to notify the app to process files.
@blueprint.route('/alert_new_file')
def alert_new_file():
    """A GET request for this URL will cause the server to check for new statfiles in the configured dir."""
    if current_app.parse_lock.locked():
        return 'Already parsing.', 530
    with current_app.parse_lock:
        thread = threading.Thread(target=parse.batch_parse, args=[current_app._get_current_object()])
        thread.start()
        return 'OK, parsing', 200
    return 'Already parsing.', 531


@blueprint.route('/changelog')
def changelog_view():
    """wow a changelog"""
    return render_template('changelog.html')


@blueprint.route('/error')  # legacy
def errorpage():
    """Error view."""
    return render_template('500.html'), 500


@blueprint.context_processor
def utility_processor():
    """Define helper methods for Jinja2 templates."""
    def modethumb(name):
        """Return a URL for an image related to the match mode."""
        name = name.lower()
        if os.path.isfile(os.path.join(basedir,
                          'app', 'static', 'img', 'modethumbs', name + '.png')):
            return flask.url_for('static', filename='img/modethumbs/' + name + '.png')
        else:
            return flask.url_for('static', filename='img/modethumbs/othermode.png')

    def antag_objs(matchid, antagkey):
        """Retrieve the objectives for an antag from a given match."""
        return db.session.query(Match).get(matchid).antagobjs.filter(AntagObjective.mindkey == antagkey)

    # def add_months(sourcedate, months):
    #     """Add months to original date. Returns a datetime."""
    #     month = sourcedate.month - 1 + months
    #     year = int(sourcedate.year + month / 12)
    #     month = month % 12 + 1
    #     day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    #     return datetime.date(year, month, day)

    def population_timeline_chart_data(matchid):
        """Get some population data for Chart.JS in JSON format."""
        ps = Match.query.get(matchid).populationstats.all()
        labels = []
        popcounts = []
        lowestPop = 100

        for snapshot in ps:
            labels.append(snapshot.time.strftime('%H:%M'))
            popcounts.append(snapshot.popcount)
            if snapshot.popcount is None or snapshot.popcount < lowestPop:
                lowestPop = snapshot.popcount

        return json.dumps(labels), json.dumps(popcounts), lowestPop

    return dict(add_months=add_months, antag_objs=antag_objs, modethumb=modethumb,
                population_timeline_chart_data=population_timeline_chart_data)


@blueprint.app_template_filter('format_timestamp')
def format_timestamp(value, format='matchtime'):
    """Format textual timestamps into more readable timestamps."""
    if format == 'matchtime':
        # yyyy mm dd hh mm ss
        value = value.split('.')
        return "{} {} {}:{}".format(calendar.month_name[int(value[1])], int(value[2]), int(value[3]), value[4])
    elif format == 'shortmatchtime':
        value = value.split('.')
        return "{}/{} {}:{}".format(int(value[1]), int(value[2]), int(value[3]), value[4])
    elif format == 'hhmm':  # datetime hour/min
        value = value.split('.')
        return "{}:{}".format(value[4], value[5])


@blueprint.app_template_filter('obj_successfail')
def obj_successfail(succeeded):
    """Return a styled span to show if an antag was successful or not.

    Keyword arguments:
    succeeded -- Boolean. Did the antag win?
    """
    if succeeded:
        return "<span class='objective success'>Success</span>"
    else:
        return "<span class='objective failure'>Failure</span>"


@blueprint.app_template_filter('obj_pretty')
def obj_pretty(objective):
    """Make antag objectives pretty for template views."""
    if objective.objective_type == u'/datum/objective/assassinate':
        return 'Asassinate {} the {}.'.format(objective.target_name, objective.target_role)
    else:
        return objective.objective_desc
