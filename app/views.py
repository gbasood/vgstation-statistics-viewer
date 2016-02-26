from app import app, parse, models, db, global_stats
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return parse.parse_url('http://game.ss13.moe/stats/statistics_2016.31.01.7.txt')

@app.route('/matchlist')
def matchlist():
    return render_template('matchlist.html', matches=models.Match.query.all())

@app.route('/globalstats')
def globalstats():
    return render_template('globalstats.html', modes=global_stats.get_global_stats())

@app.route('/match/<id>')
def match(id):
    return render_template('match.html', match = models.Match.query.get(id))
