import os, flask
from config import basedir
from app import app
def modethumb(name):
    name=name.lower()
    if os.path.isfile(os.path.join(basedir, 'app','static','img','modethumbs', name + '.png')):
        return flask.url_for('static', filename='img/modethumbs/' + name + '.png')
    else:
        return flask.url_for('static', filename='img/modethumbs/othermode.png')

app.jinja_env.globals.update(modethumb=modethumb)
