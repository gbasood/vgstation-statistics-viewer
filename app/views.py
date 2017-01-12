from app import app, parse, models, db, global_stats
from app.helpers import add_months
import datetime
from config import MATCHES_PER_PAGE
from flask import render_template, request
import threading

parse_lock = threading.RLock()


@app.route('/')
@app.route('/index')
def index():
    matchesTotal = models.Match.query.count()
    nuked = models.Match.query.filter(models.Match.nuked).count()
    lastmatch = models.Match.query.order_by(models.Match.id.desc()).first()

    return render_template('index.html', matchcount=matchesTotal, nukedcount=nuked, lastmatch=lastmatch)

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
    query = models.Match.query.order_by(models.Match.id.desc())
    paginatedMatches = query.paginate(page, MATCHES_PER_PAGE, False)
    return render_template('matchlist.html', matches=paginatedMatches.items, pagination=paginatedMatches)


# TODO: Use caching to store global stats results and only recalculate when needed, reducing load on server
@app.route('/globalstats')
def globalstats(timespan="monthly", month=None, year=None):
    query_timespan = request.args.get("timespan") if request.args.get("timespan") else "monthly"
    request_month = int(request.args.get("month") if request.args.get("month") else datetime.datetime.now().month)
    request_year = int(request.args.get("year") if request.args.get("year") else datetime.datetime.now().year)
    request_starttime = datetime.datetime(year=request_year, month=request_month, day=1)

    request_timespan = (query_timespan, request_starttime)
    next_page = add_months(request_starttime, 1)
    prev_page = add_months(request_starttime, -1)
    return render_template('globalstats.html', matchData=global_stats.get_formatted_global_stats(request_timespan), timespan=query_timespan, query_start=request_starttime, nextpage = next_page, prevpage = prev_page)


@app.route('/match/<id>')
def match(id=0):
    return render_template('match.html', match=models.Match.query.get(id))


# This is the route that the bot will use to notify the app to process files.
@app.route('/alert_new_file')
def alert_new_file():
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
    return render_template('404.html'), 404


@app.errorhandler(500)
@app.route('/error')
def errorpage():
    return render_template('500.html'), 500
