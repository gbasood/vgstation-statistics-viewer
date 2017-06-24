"""Helper functions for Jinja2 templates."""
from app import app
from app import models
from app.models import db
import calendar
from config import basedir
import datetime
import flask
import json
import os


def add_months(sourcedate, months):
    """Add months to original date. Returns a datetime."""
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


@app.context_processor
def utility_processor():
    """Define helper methods for Jinja2 templates."""
    def modethumb(name):
        """Return a URL for an image related to the match mode."""
        name = name.lower()
        if os.path.isfile(os.path.join(basedir, 'app', 'static', 'img', 'modethumbs', name + '.png')):
            return flask.url_for('static', filename='img/modethumbs/' + name + '.png')
        else:
            return flask.url_for('static', filename='img/modethumbs/othermode.png')

    def antag_objs(matchid, antagkey):
        """Retrieve the objectives for an antag from a given match."""
        return db.session.query(models.Match).get(matchid).antagobjs.filter(models.AntagObjective.mindkey == antagkey)

    # def add_months(sourcedate, months):
    #     """Add months to original date. Returns a datetime."""
    #     month = sourcedate.month - 1 + months
    #     year = int(sourcedate.year + month / 12)
    #     month = month % 12 + 1
    #     day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    #     return datetime.date(year, month, day)

    def population_timeline_chart_data(matchid):
        """Get some population data for Chart.JS in JSON format."""
        ps = models.Match.query.get(matchid).populationstats.all()
        labels = []
        popcounts = []
        lowestPop = 100

        for snapshot in ps:
            labels.append(snapshot.time.strftime('%H:%M'))
            popcounts.append(snapshot.popcount)
            if snapshot.popcount is None or snapshot.popcount < lowestPop:
                lowestPop = snapshot.popcount

        return json.dumps(labels), json.dumps(popcounts), lowestPop

    return dict(add_months=add_months, antag_objs=antag_objs, modethumb=modethumb, population_timeline_chart_data=population_timeline_chart_data)
