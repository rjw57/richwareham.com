"""Run a development webserver.

Usage:
    personalsite [-h] [--host=HOSTNAME] [--port=NUMBER]

Options:
    -h, --help              Show a brief usage summary.

    --host=HOSTNAME         Hostname of IP to bind to [default: 127.0.0.1]
    --port=NUMBER           Port number to bind to [default: 5000]
"""
from personalsite import app

import docopt

opts = docopt.docopt(__doc__)

# When testing, allow running of this application directly. Also, enable debug mode
app.run(host=opts['--host'], port=int(opts['--port']), debug=True)
