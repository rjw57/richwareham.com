"""
Provides a flask blueprint (shortlinks.app) which acts as a URL shortener
implementation. Note that the blueprint does *not* start its URL routes with
'/' and so one should use a URL prefix when registering the blueprint.
"""
import datetime
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
from .util import require_admin

# Characters from which an id will be randomly generated
ID_CHARS = 'ABCDEFGHJKLMNOPQRSTUVWXYZ23456789'

# Directory holding templates
app = Blueprint('shortlinks', __name__,
        template_folder=os.path.join(TEMPLATE_ROOT, 'shortlinks'))

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
    sqlite_path = current_app.config['shortlinks_datastore']
    engine = create_engine('sqlite:////' + sqlite_path)

    # Ensure we have created all of the tables
    Base.metadata.create_all(engine)

    # Define the SQLalchemy session
    Session = sessionmaker()

    # Configure the session by binding it to this engine
    Session.configure(bind=engine)

    # Return the class
    return Session()

def normalise_destination(destination):
    # Normalise destination URL
    if '//' not in destination:
        destination = '//' + destination
    destination = urlunparse(urlparse(destination, 'http'))
    return destination

# Web app itself

@app.route('')
def list():
    session = make_session()
    redirects = []
    for r in session.query(Redirect).filter_by(reserved=False).all():
        redirects.append({
            'from': r.key,
            'to': r.destination,
            'created': r.created_at.isoformat(),
            'modified': r.modified_at.isoformat(),
            'urls': {
                'self': urljoin(request.url_root, url_for('.redirect', key=r.key)),
                'edit': urljoin(request.url_root, url_for('.edit_GET', key=r.key)),
                'delete': urljoin(request.url_root, url_for('.delete', key=r.key)),
            },
        })

    return jsonify(redirects=redirects)

@app.route('<key>/edit')
@require_admin
def edit_GET(key):
    session = make_session()
    redirect = session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)
    return render_template('edit-form.html',
            action=url_for('.edit_POST', key=key), key=key,
            url_root=request.url_root, destination=redirect.destination,
            url=urljoin(request.url_root, url_for('.redirect', key=key)))

@app.route('<key>/edit', methods=['POST'])
@require_admin
def edit_POST(key):
    session = make_session()
    redirect = session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)

    destination = request.values['destination']
    if destination is None or destination == '':
        return flask.abort(400)

    # Normalise destination URL
    destination = normalise_destination(destination)

    redirect.destination = destination
    session.commit()

    return 'OK'

@app.route('<key>/delete')
@require_admin
def delete(key):
    session = make_session()
    redirect = session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)

    # Delete this redirect from the database and return
    session.delete(redirect)
    session.commit()

    return 'OK'

@app.route('/new', defaults={'key': None})
@app.route('<key>/new')
@require_admin
def new_GET(key):
    session = make_session()

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
    destination = normalise_destination(destination)

    session = make_session()
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
    session = make_session()
    redirect = session.query(Redirect).filter_by(key=key, reserved=False).first()
    if redirect is None:
        return flask.abort(404)
    return flask.redirect(redirect.destination)
