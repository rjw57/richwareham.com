import logging
import os

from flask import Flask, redirect, request, send_from_directory, jsonify, abort

from .shortlinks import app as shortlinks_app
from .google import create_oauth, app as google_app
from .update import update_static, check_hmac
from .util import require_admin

# Where to find the static site on disk
if 'OPENSHIFT_DATA_DIR' not in os.environ:
    STATIC_SITE_DIR = '/tmp/rw-static-site'
    logging.warn('OPENSHIFT_DATA_DIR not set, using {0} for static HTML'.format(STATIC_SITE_DIR))
else:
    STATIC_SITE_DIR = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'static')

app = Flask(__name__, static_url_path='', static_folder=STATIC_SITE_DIR)

# If running on OpenShift be a little more sensible about generating secret
# data.
if 'OPENSHIFT_DATA_DIR' in os.environ:
    secret_key_path = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'session.key')
    if os.path.isfile(secret_key_path):
        app.secret_key = open(secret_key_path, 'rb').read()
    else:
        import ssl
        app.secret_key = ssl.RAND_bytes(64)
        open(secret_key_path, 'wb').write(app.secret_key)
else:
    app.secret_key = 'development'.encode('utf8')

# Write up OAuth
app.config['google'] = create_oauth(app)

# Register modules
app.register_blueprint(shortlinks_app, url_prefix='/@')
app.register_blueprint(google_app, url_prefix='/google')

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

# Static site

@app.route('/')
def root():
    return app.send_static_file('index.html')

def toplevel_endpoint(path):
    return app.send_static_file(os.path.join(path, 'index.html'))

for endpoint in ['software','publications','research','teaching','contact','cv','about','links','articles']:
    toplevel_endpoint = app.route('/' + endpoint, defaults={'path': endpoint})(
            toplevel_endpoint)

@app.route('/articles/<path:slug>')
def article(slug):
    return app.send_static_file(os.path.join('articles', slug, 'index.html'))

@app.route('/components/platform/<path:path>')
def components_platform(path):
    return send_from_directory(
        os.path.join(STATIC_SOURCE_DIR, 'js/bower_components/platform'), path)

@app.route('/components/MathJax/<path:path>')
def components_mathjax(path):
    return send_from_directory(
        os.path.join(STATIC_SOURCE_DIR, 'js/bower_components/MathJax'), path)

@app.route('/static-content', methods=['POST'])
def update_static_content():
    if 'STATIC_SITE_SECRET' not in os.environ:
        return abort(500)
    hmac_ok = check_hmac(request.files['archive'].stream,
            os.environ['STATIC_SITE_SECRET'].encode('utf8'),
            request.values['hmac'])
    if not hmac_ok:
        return abort(403)
    update_static(STATIC_SITE_DIR, request.files['archive'].stream)
    return jsonify({ 'status': 200, 'message': 'OK' })
