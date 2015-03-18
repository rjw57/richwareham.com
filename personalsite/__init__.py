import logging
import os

from .app import app, db
from .google import create_oauth, app as google_app
from .shortlinks import app as shortlinks_app
from .gpslog import app as gpslog_app

from .apps.scrapbook import scrapbook

# Write up OAuth
app.config['google'] = create_oauth(app)

# Register modules
app.register_blueprint(shortlinks_app, url_prefix='/@')
app.register_blueprint(google_app, url_prefix='/google')

app.register_blueprint(scrapbook, url_prefix='/apps/scrapbook/')

#gpslog_app.static_folder = os.path.join(app.static_folder, 'apps', 'gpslog')
#gpslog_app.template_folder = os.path.join(app.static_folder, 'apps', 'gpslog')
#app.register_blueprint(gpslog_app, url_prefix='/apps/gpslog/')
