from flask import Flask

from .shortlinks import app as shortlinks

app = Flask(__name__)
app.register_blueprint(shortlinks, url_prefix='/@')

@app.route('/')
def root():
    return 'Hello, world'
