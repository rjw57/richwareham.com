"""Common utility functions."""
import functools

import flask

def require_admin(f):
    """Decorator for flask handler which requires administrator logged in to
    succeed. IMPORTANT: this wrapper must follow all @app.route decorators.

    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        google = flask.current_app.config['google']
        if 'google_token' not in flask.session:
            flask.session['post_login_redirect'] = request.url
            return flask.redirect(url_for('google.login'))
        me = google.get('userinfo')

        # FIXME: hard-coded admin id
        if me.data['id'] != '114005052144439249039':
            return flask.abort(403)

        return f(*args, **kwargs)
    return wrapper

