"""
Provides a flask blueprint (shortlinks.app) which acts as a URL shortener
implementation. Note that the blueprint does *not* start its URL routes with
'/' and so one should use a URL prefix when registering the blueprint.
"""
import datetime
import functools
import logging
import os
import random
import tempfile
from urllib.parse import urljoin, urlparse, urlunparse

import flask
from flask import Blueprint, url_for, jsonify, request, render_template, current_app
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from .env import TEMPLATE_ROOT

# Characters from which an id will be randomly generated
ID_CHARS = 'ABCDEFGHJKLMNOPQRSTUVWXYZ23456789'

# Directory holding templates
app = Blueprint('shortlinks', __name__,
        template_folder=os.path.join(TEMPLATE_ROOT, 'shortlinks'))

# Where on-disk is the datastore for this module?
if 'OPENSHIFT_DATA_DIR' in os.environ:
    SQLITE_PATH=os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'shortlinks.sqlite')
else:
    SQLITE_PATH=os.path.join(tempfile.gettempdir(), 'shortlinks.sqlite')
    logging.warn('Not running on OpenShift. Using {0} for SQLite'.format(SQLITE_PATH))

def make_random_key(cls):
    return ''.join(random.sample(ID_CHARS, 5))

# Data model
Base = declarative_base()

class Redirect(Base):
    """Model an individual redirect with destination, key and created and
    modified timestamps."""

    __tablename__ = 'redirects'

    id = Column(Integer, primary_key=True)
    key = Column(String, default=make_random_key, nullable=False, unique=True, index=True)
    destination = Column(String)
    reserved = Column(Boolean, index=True, default=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

def make_session():
    """Configure the SQLalchemy session."""

    # Create a SQLalchemy engine which will be used as a persistent data store
    engine = create_engine('sqlite:////' + SQLITE_PATH)

    # Ensure we have created all of the tables
    Base.metadata.create_all(engine)

    # Define the SQLalchemy session
    Session = sessionmaker()

    # Configure the session by binding it to this engine
    Session.configure(bind=engine)

    # Return the class
    return Session

Session = make_session()

def require_admin(f):
    """Decorator which requires administrator logged in to succeed."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        google = current_app.config['google']
        if 'google_token' not in flask.session:
            flask.session['post_login_redirect'] = request.url
            return flask.redirect(url_for('google.login'))
        me = google.get('userinfo')
        # FIXME: hard-coded admin id
        if me.data['id'] != '114005052144439249039':
            return flask.abort(403)
        return f(*args, **kwargs)
    return wrapper

# Web app itself

@app.route('')
def list():
    session = Session()
    redirects = []
    for r in session.query(Redirect).filter_by(reserved=False).all():
        redirects.append({
            'from': r.key,
            'to': r.destination,
            'created': r.created_at.isoformat(),
            'modified': r.modified_at.isoformat(),
            'urls': {
                'self': urljoin(request.url_root, url_for('.redirect', key=r.key)),
                #'edit': url_for('.edit', key=r.key),
                #'delete': url_for('.delete', key=r.key),
            },
        })

    return jsonify(redirects=redirects)

@app.route('/new', defaults={'key': None})
@app.route('<key>/new')
@require_admin
def new_GET(key):
    session = Session()

    # Do we have a reserved redirect?
    redirect = session.query(Redirect).filter_by(key=key, reserved=True).first()

    if redirect is None:
        # Create a new reserved redirect
        redirect = Redirect(key=key)
        session.add(redirect)
        session.commit()

    # If the key was not specified in the URL, redirect to it
    if key is None:
        return flask.redirect(url_for('.new_GET', key=redirect.key))

    return render_template('new-form.html',
            action=url_for('.new_POST', key=key),
            url=urljoin(request.url_root, url_for('.redirect', key=key)))

@app.route('<key>/new', methods=['POST'])
@require_admin
def new_POST(key):
    if key is None or key == '':
        return flask.abort(400)

    destination = request.values['destination']
    if destination is None or destination == '':
        return flask.abort(400)

    # Normalise destination URL
    if '//' not in destination:
        destination = '//' + destination
    destination = urlunparse(urlparse(destination, 'http'))

    session = Session()
    redirect = session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)
    if not redirect.reserved:
        return flask.abort(403)

    # Now we know that redirect is a Redirect instance which is reserved
    redirect.reserved = False
    redirect.destination = destination
    session.commit()

    return render_template('created.html',
        url=urljoin(request.url_root, url_for('.redirect', key=redirect.key)),
        destination=destination)

@app.route('<key>')
def redirect(key):
    # Is there a non-reserved redirect at this key?
    session = Session()
    redirect = session.query(Redirect).filter_by(key=key, reserved=False).first()
    if redirect is None:
        return flask.abort(404)
    return flask.redirect(redirect.destination)
