"""Run a development webserver.
"""
from personalsite import app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.run()
