"""Provide a URL endpoint to log GPS data to.

"""
from flask import Blueprint, request, jsonify, current_app
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

@app.route('/log')
@require_admin
def geojson():
    features = list(
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point', 'coordinates': [x.lon, x.lat, x.alt],
            },
            'properties': {
                'accuracy': x.accuracy,
                'timestamp': x.timestamp.isoformat(),
            },
        }
        for x in db.session.query(LocationRecord).order_by(LocationRecord.timestamp)
    )

    google = current_app.config['google']
    collection = {
        'type': 'FeatureCollection',
        'features': features,
        'properties': {
            'preparedFor': {
                'id': google.get('userinfo').data['id'],
                'name': google.get('userinfo').data['name'],
            },
        },
    }

    return jsonify(collection)

@app.route('/')
@require_admin
def index():
    return app.send_static_file('index.html')
