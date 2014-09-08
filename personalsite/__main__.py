"""Run a development webserver.
"""
from personalsite import app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.run()
