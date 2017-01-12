import datetime
import calendar
import flask
import os
from config import basedir
from app import app, db, models


def modethumb(name):
    name = name.lower()
    if os.path.isfile(os.path.join(basedir, 'app', 'static', 'img', 'modethumbs', name + '.png')):
        return flask.url_for('static', filename='img/modethumbs/' + name + '.png')
    else:
        return flask.url_for('static', filename='img/modethumbs/othermode.png')

app.jinja_env.globals.update(modethumb=modethumb)


def antag_objs(matchid, antagkey):
    '''Retrieves the objectives for an antag from a given match.'''
    return db.session.query(models.Match).get(matchid).antagobjs.filter(models.AntagObjective.mindkey == antagkey)


app.jinja_env.globals.update(antag_objs=antag_objs)


def add_months(sourcedate, months):
    '''Adds months to original date. Returns a datetime.'''
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

app.jinja_env.globals.update(add_months=add_months)
