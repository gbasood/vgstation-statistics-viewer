from app import app, parse, models, db
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return parse.parse_url('http://ss13.undo.it/stats/statistics_2015.28.12.9.txt')

@app.route('/matchlist')
def matchlist():
    return render_template('matchlist.html', matches=models.Match.query.all())

@app.route('/match/<id>')
def match(id):
    return render_template('match.html', match = models.Match.query.get(id))
