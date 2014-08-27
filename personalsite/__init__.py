import os

from flask import Flask

from .shortlinks import app as shortlinks_app
from .google import create_oauth, app as google_app

app = Flask(__name__)

# TODO: make this more secure
app.secret_key = 'development'.encode('utf8')

# Write up OAuth
app.config['google'] = create_oauth(app)

# Register modules
app.register_blueprint(shortlinks_app, url_prefix='/@')
app.register_blueprint(google_app, url_prefix='/google')

@app.route('/')
def root():
    return 'Hello, world'
