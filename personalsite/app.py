"""Create top-level flask webapp.

Do not use the app variable from this module directly. Instead use the value as
set up by the personalsite module. Only internal blueprints should use
variables in this module directly.

"""
import logging
import os

from flask import Flask, redirect, request, send_from_directory, jsonify, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask_sslify import SSLify

from .config import configure
from .update import update_static, check_hmac
from .util import require_admin

app = Flask(__name__, static_url_path='')
configure(app)

# Default timeout is 180 days (~ half a year)
SSLify(app, age=60*60*24*180)

db = SQLAlchemy(app)

@app.route('/env')
@require_admin
def env():
    response_body = [
        '%s: %s' % (key, value)
        for key, value in sorted(request.environ.items())
    ]
    response_body = '\n'.join(response_body)

    return response_body, 200, { 'Content-Type': 'text/plain' }

@app.route('/health')
def health():
    return '1', 200, { 'Content-Type': 'text/plain' }

# Dump database
@app.route('/dbdump')
@require_admin
def dbdump():
    sqlalchemy_db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if not sqlalchemy_db_uri.startswith('sqlite:////'):
        return abort(404)
    with open(sqlalchemy_db_uri[11:], 'rb') as f:
        return f.read(), 200, { 'Content-Type': 'application/octet-stream' }

# Static site

@app.route('/')
def root():
    return app.send_static_file('index.html')

def toplevel_endpoint(path):
    return app.send_static_file(os.path.join(path, 'index.html'))

for endpoint in ['software','publications','research','teaching','contact','cv','about','links','articles','academic']:
    toplevel_endpoint = app.route('/' + endpoint, defaults={'path': endpoint})(
            toplevel_endpoint)

@app.route('/articles/<path:slug>')
def article(slug):
    return app.send_static_file(os.path.join('articles', slug, 'index.html'))

@app.route('/static-content', methods=['POST'])
def update_static_content():
    # If we don't have a shared secret defined, fail.
    if 'STATIC_SITE_SECRET' not in os.environ:
        return abort(500)

    # Get a file object pointing to the archive sent with the request
    archive = request.files['archive'].stream

    # Check the HMAC which was provided matches the shared secret
    archive.seek(0)
    hmac_ok = check_hmac(archive,
            os.environ['STATIC_SITE_SECRET'].encode('utf8'),
            request.values['hmac'])
    if not hmac_ok:
        return abort(403)

    # Unzip the static files
    archive.seek(0)
    update_static(app.static_folder, archive)
    return jsonify({ 'status': 200, 'message': 'OK' })
