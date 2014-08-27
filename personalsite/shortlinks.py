"""
Provides a flask blueprint (shortlinks.app) which acts as a URL shortener
implementation. Note that the blueprint does *not* start its URL routes with
'/' and so one should use a URL prefix when registering the blueprint.
"""
from flask import Blueprint, url_for

app = Blueprint('shortlinks', __name__)

@app.route('<key>')
def redirect(key):
    return 'Key: {0} at {1}'.format(key, url_for('shortlinks.redirect', key=key))
