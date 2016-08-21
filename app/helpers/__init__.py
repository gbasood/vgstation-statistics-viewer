import os, flask
from config import basedir
from app import app, db, models

def modethumb(name):
    name=name.lower()
    if os.path.isfile(os.path.join(basedir, 'app','static','img','modethumbs', name + '.png')):
        return flask.url_for('static', filename='img/modethumbs/' + name + '.png')
    else:
        return flask.url_for('static', filename='img/modethumbs/othermode.png')

app.jinja_env.globals.update(modethumb=modethumb)

def antag_objs(matchid, antagkey):
    '''Retrieves the objectives for an antag from a given match.'''
    return db.session.query(models.Match).get(matchid).antagobjs.filter(models.AntagObjective.mindkey == antagkey)


app.jinja_env.globals.update(antag_objs=antag_objs)
