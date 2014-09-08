"""Configuration of webapp.

This module provides a single function which sets the various configuration
parameters for the webapp.

"""
import logging
import os
import tempfile

def configure(app, **kwargs):
    """Configure a flask webapp with the configuration parameters we use.
    Detected if we're running on OpenShift and uses deployment configuration or
    development configuration as appropriate. Individual configuration
    parameters may be overridden by setting keyword arguments. Configuration
    which can be overridden includes:

    (Items stored in app object directly.)

        * secret_key: the key used for encrypting session cookies
        * static_filder: the directory static content is served from

    (Items stored in app.config.)

        * shortlinks_datastore: on-disk location of short links database
    """
    ## SECRET KEY FOR SESSIONS

    # If running on OpenShift be a little more sensible about generating secret
    # data.
    try:
        app.secret_key = kwargs['secret_key']
    except KeyError:
        if 'OPENSHIFT_DATA_DIR' in os.environ:
            secret_key_path = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'session.key')
            if os.path.isfile(secret_key_path):
                secret_key = open(secret_key_path, 'rb').read()
            else:
                import ssl
                app.secret_key = ssl.RAND_bytes(64)
                open(secret_key_path, 'wb').write(app.secret_key)
        else:
            app.secret_key = 'development'.encode('utf8')

    try:
        app.static_folder = kwargs['static_dir']
    except KeyError:
        # Where to find the static site on disk
        if 'OPENSHIFT_DATA_DIR' not in os.environ:
            app.static_folder = '/tmp/rw-static-site'
            logging.warn('OPENSHIFT_DATA_DIR not set, using {0} for static HTML'.format(
                app.static_folder))
        else:
            app.static_folder = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'static')

    # Where on-disk is the datastore for short links
    try:
        app.config['shortlinks_datastore'] = kwargs['shortlinks_datastore']
    except KeyError:
        if 'OPENSHIFT_DATA_DIR' in os.environ:
            app.config['shortlinks_datastore']=os.path.join(os.environ['OPENSHIFT_DATA_DIR'],
                    'shortlinks.sqlite')
        else:
            app.config['shortlinks_datastore']=os.path.join(tempfile.gettempdir(),
                    'shortlinks.sqlite')
            logging.warn('Not running on OpenShift. Using {0} for SQLite'.format(
                app.config['shortlinks_datastore']))
