"""
OAuth flow for Google+ signin
"""
from flask import Blueprint, url_for, session, redirect, current_app
from flask_oauthlib.client import OAuth

GOOGLE_ID='147241297970-7ouoqfjb56dklf4j6c0qh35jidmful2m.apps.googleusercontent.com'
GOOGLE_SECRET='bW2SYo7NYKVvuh2sLPyO6thf'

def create_oauth(app):
    oauth = OAuth(app)
    google = oauth.remote_app('google',
        consumer_key=GOOGLE_ID,
        consumer_secret=GOOGLE_SECRET,
        request_token_params={
            'scope': 'https://www.googleapis.com/auth/userinfo.email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')

    return google

app = Blueprint('google', __name__)

@app.route('/login')
def login():
    google = current_app.config['google']
    return google.authorize(callback=url_for('.authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return 'Logged out'

@app.route('/authorized')
def authorized():
    google = current_app.config['google']
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')

    if 'post_login_redirect' in session:
        return redirect(session.pop('post_login_redirect', None))
    return 'Logged in'
