#!/usr/bin/env python
import os

from personalsite import app as site_app

def application(environ, start_response):

    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value) for key, value in sorted(environ.items())]
        response_body = '\n'.join(response_body)
    else:
        # Pass-through to main app
        return site_app(environ, start_response)

    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]

    start_response(status, response_headers)
    return [response_body.encode('utf-8') ]
#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
