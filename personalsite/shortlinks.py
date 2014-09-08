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

from .app import db
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
class Redirect(db.Model):
    """Model an individual redirect with destination, key and created and
    modified timestamps."""

    __tablename__ = 'redirects'
    __bind_key__ = 'shortlinks'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String,
            default=make_random_key, nullable=False, unique=True, index=True)
    destination = db.Column(db.String)
    reserved = db.Column(db.Boolean, index=True, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    modified_at = db.Column(db.DateTime, server_default=db.func.now(),
            onupdate=db.func.current_timestamp())

def normalise_destination(destination):
    # Normalise destination URL
    if '//' not in destination:
        destination = '//' + destination
    destination = urlunparse(urlparse(destination, 'http'))
    return destination

# Web app itself

@app.route('')
def list():
    redirects = []
    for r in db.session.query(Redirect).filter_by(reserved=False).all():
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
    redirect = db.session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)
    return render_template('edit-form.html',
            action=url_for('.edit_POST', key=key), key=key,
            url_root=request.url_root, destination=redirect.destination,
            url=urljoin(request.url_root, url_for('.redirect', key=key)))

@app.route('<key>/edit', methods=['POST'])
@require_admin
def edit_POST(key):
    redirect = db.session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)

    destination = request.values['destination']
    if destination is None or destination == '':
        return flask.abort(400)

    # Normalise destination URL
    destination = normalise_destination(destination)

    redirect.destination = destination
    db.session.commit()

    return 'OK'

@app.route('<key>/delete')
@require_admin
def delete(key):
    redirect = db.session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)

    # Delete this redirect from the database and return
    db.session.delete(redirect)
    db.session.commit()

    return 'OK'

@app.route('/new', defaults={'key': None})
@app.route('<key>/new')
@require_admin
def new_GET(key):

    # Do we have a reserved redirect?
    redirect = db.session.query(Redirect).filter_by(key=key, reserved=True).first()

    if redirect is None:
        # Create a new reserved redirect
        redirect = Redirect(key=key)
        db.session.add(redirect)
        db.session.commit()

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

    redirect = db.session.query(Redirect).filter_by(key=key).first()
    if redirect is None:
        return flask.abort(404)
    if not redirect.reserved:
        return flask.abort(403)

    # Now we know that redirect is a Redirect instance which is reserved
    redirect.reserved = False
    redirect.destination = destination
    db.session.commit()

    return render_template('created.html',
        url=urljoin(request.url_root, url_for('.redirect', key=redirect.key)),
        destination=destination)

@app.route('<key>')
def redirect(key):
    # Is there a non-reserved redirect at this key?
    redirect = db.session.query(Redirect).filter_by(key=key, reserved=False).first()
    if redirect is None:
        return flask.abort(404)
    return flask.redirect(redirect.destination)
