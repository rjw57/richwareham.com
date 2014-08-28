import os

from flask import Flask, redirect, request

from .shortlinks import app as shortlinks_app
from .google import create_oauth, app as google_app
from .util import require_admin

app = Flask(__name__)

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

@app.route('/')
def root():
    return redirect('https://rjw57.github.io/blog')

@app.route('/env')
@require_admin
def env():
    response_body = [
        '%s: %s' % (key, value)
        for key, value in sorted(request.environ.items())
    ]
    response_body = '\n'.join(response_body)

    return response_body, 200, { 'Content-Type': 'text/plain' }
