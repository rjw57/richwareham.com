import logging
import os

from .app import app, db
from .google import create_oauth, app as google_app
from .shortlinks import app as shortlinks_app

# Write up OAuth
app.config['google'] = create_oauth(app)

# Register modules
app.register_blueprint(shortlinks_app, url_prefix='/@')
app.register_blueprint(google_app, url_prefix='/google')
