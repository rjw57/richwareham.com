#!/usr/bin/env python
import os

from personalsite import app as application

# Uncomment to get tracebck in logs on OpenShift
application.config['PROPAGATE_EXCEPTIONS'] = True

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
