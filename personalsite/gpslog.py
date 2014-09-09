"""Provide a URL endpoint to log GPS data to.

"""
from calendar import timegm
import json

from flask import Blueprint, request, jsonify, current_app, render_template
from dateutil.parser import parse as date_parse
from dateutil.tz import tzutc

from .app import db
from .util import require_admin

app = Blueprint('gpslog', __name__)

# Data model
class LocationRecord(db.Model):
    """Model an individual redirect with destination, key and created and
    modified timestamps."""

    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)

    speed = db.Column(db.Float)
    direction = db.Column(db.Float)

    accuracy = db.Column(db.Float)

    remote_addr = db.Column(db.String)
    forwarded_for = db.Column(db.String)
    user_agent = db.Column(db.String)
    client_id = db.Column(db.String, index=True)

    timestamp = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@app.route('/record')
def record():
    lat, lon, alt = tuple(float(request.values[x]) for x in ('lat', 'lon', 'alt'))
    speed, direction = tuple(float(request.values[x]) for x in ('speed', 'direction'))
    accuracy = float(request.values['accuracy'])

    user_agent = request.environ['HTTP_USER_AGENT']
    try:
        forwarded_for = request.headers['X-Forwarded-For']
    except KeyError:
        forwarded_for = None
    remote_addr = request.environ['REMOTE_ADDR']

    timestamp = date_parse(request.values['time'])
    timestamp = timestamp.astimezone(tzutc())

    record = LocationRecord(lat=lat, lon=lon, alt=alt,
            speed=speed, direction=direction, accuracy=accuracy,
            timestamp=timestamp,
            user_agent=user_agent, forwarded_for=forwarded_for, remote_addr=remote_addr)
    db.session.add(record)
    db.session.commit()

    return 'ok'

def _log_as_linestring():
    features = []

    line_string_coords = []
    line_string_props = { 'accuracies': [], 'timestamps': [] }
    for x in db.session.query(LocationRecord).order_by(LocationRecord.timestamp):
        line_string_coords.append((x.lon, x.lat, x.alt))
        line_string_props['accuracies'].append(x.accuracy)
        line_string_props['timestamps'].append(timegm(x.timestamp.utctimetuple()))
    features.append({
        'type': 'Feature',
        'geometry': { 'type': 'LineString', 'coordinates': line_string_coords },
        'properties': line_string_props,
    })

    collection = {
        'type': 'FeatureCollection',
        'features': features,
    }

    return collection

@app.route('/log')
@require_admin
def geojson():
    return jsonify(_log_as_linestring())

@app.route('/')
@require_admin
def index():
    return render_template('index.html', geojsonlog=_log_as_linestring())
