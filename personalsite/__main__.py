"""Run a development webserver.
"""
from personalsite import app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from .config import configure
configure(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.run()
