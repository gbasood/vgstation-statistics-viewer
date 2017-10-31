import bson
from app.models import Match
from flask import Blueprint
from flask import render_template

blueprint = Blueprint('api', __name__)


@blueprint.route('/api/match/<int:id>')
def match_as_json(id=0):
    """Respond with match data as JSON."""
    if id is not 0:
        json = Match.query.get(id).as_json()
        print(json)
        return json, 201, {'Content-Type': 'application/json', 'charset': 'utf-8'}
    else:
        return 'error', 404
