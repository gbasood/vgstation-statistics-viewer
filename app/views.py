from app import app, parse, models, db, global_stats
from config import MATCHES_PER_PAGE
from flask import render_template, request

@app.route('/')
@app.route('/index')
def index():
    matchesTotal = len(models.Match.query.all())
    nuked = models.Match.query.filter(models.Match.nuked).count()

    return render_template('index.html', matchcount = matchesTotal, nukedcount = nuked)

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
    paginatedMatches=query.paginate(page, MATCHES_PER_PAGE, False)
    return render_template('matchlist.html', matches=paginatedMatches.items, pagination=paginatedMatches)

def matchlistpage(page):
    return
#TODO: Use caching to store global stats results and only recalculate when needed, reducing load on server
@app.route('/globalstats')
def globalstats():
    return render_template('globalstats.html', modes=global_stats.get_global_stats())

@app.route('/match/<id>')
def match(id):
    return render_template('match.html', match = models.Match.query.get(id))

# This is the route that the bot will use to notify the app to process files.
@app.route('/alert_new_file')
def alert_new_file():
    returnval = parse.batch_parse()
    if returnval is not None:
        return 'ERROR', 500
    return 'OK'
