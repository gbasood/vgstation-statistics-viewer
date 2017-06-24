"""View routing."""

import datetime
import threading
from app import app, parse, global_stats
from app.models import db
from app.models import Death
from app.models import Explosion
from app.models import Match
from app.helpers import add_months
from config import MATCHES_PER_PAGE
from flask import render_template
from flask import request
from sqlalchemy import func

parse_lock = threading.RLock()


@app.route('/')
@app.route('/index')
def index():
    """Respond with view for index page."""
    matchesTotal = Match.query.count()
    if matchesTotal is 0:
        matchesTotal = 1
    explosionratio = Explosion.query.count() / float(matchesTotal)
    deathratio = Death.query.count() / float(matchesTotal)
    nuked = Match.query.filter(Match.nuked).count()
    lastmatch = Match.query.order_by(Match.id.desc()).first()
    mapPlayrate = db.session.query(Match.mapname, func.count(Match.id)).group_by(Match.mapname).all()
    # Map percentage
    # for mapx in matchCounts:
    #     mapx[1] = mapx[1] / float(matchesTotal) * 100

    return render_template('index.html', matchcount=matchesTotal, nukedcount=nuked, explosionratio=explosionratio,
                           deathratio=deathratio, lastmatch=lastmatch,
                           mapPlayrate=mapPlayrate)

# @app.route('/import')
# def test():
#     url='http://game.ss13.moe/stats/statistics_2016.31.01.7.txt'
#     if request.args.get('url'):
#         url = request.args.get('url')
#         print(url)
#     return parse.parse_url(url)


@app.route('/matchlist')
@app.route('/matchlist/<int:page>')
def matchlist(page=1):
    """Respond with view for paginated match list."""
    query = Match.query.order_by(Match.id.desc())
    paginatedMatches = query.paginate(page, MATCHES_PER_PAGE, False)
    return render_template('matchlist.html', matches=paginatedMatches.items, pagination=paginatedMatches)


@app.route('/globalstats')
def globalstats(timespan="monthly", month=None, year=None):
    """Respond with view for global statistics, with optional timespan grouping. Currently only all time or by month."""
    query_timespan = request.args.get("timespan") if request.args.get("timespan") else "monthly"
    request_month = int(request.args.get("month") if request.args.get("month") else datetime.datetime.now().month)
    request_year = int(request.args.get("year") if request.args.get("year") else datetime.datetime.now().year)
    request_starttime = datetime.datetime(year=request_year, month=request_month, day=1)

    request_timespan = (query_timespan, request_starttime)
    next_page = add_months(request_starttime, 1)
    prev_page = add_months(request_starttime, -1)
    stats = global_stats.get_formatted_global_stats(request_timespan)
    return render_template('globalstats.html', matchData=stats,
                           timespan=query_timespan,
                           query_start=request_starttime, nextpage=next_page,
                           prevpage=prev_page)


@app.route('/match/<id>')
def match(id=0):
    """Respond with view for a match."""
    return render_template('match.html', match=Match.query.get(id))


# This is the route that the bot will use to notify the app to process files.
@app.route('/alert_new_file')
def alert_new_file():
    """A GET request for this URL will cause the server to check for new statfiles in the configured dir."""
    with parse_lock:
        returnval = parse.batch_parse()
        if returnval is 530:
            return 'Database busy, try later.', 530
        elif returnval is not None or returnval is -1:
            return 'ERROR', 500
        return 'OK'
    return 'Already parsing.', 531


@app.errorhandler(404)
def page_not_found(e):
    """404 view."""
    return render_template('404.html'), 404


@app.errorhandler(500)
@app.route('/error')
def errorpage():
    """Error view."""
    return render_template('500.html'), 500
