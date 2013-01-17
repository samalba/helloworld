#!/usr/bin/env python

import os
import flask
from flask import Flask


app = Flask(__name__)
app.debug = True


def response(data, code=200):
    headers = {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Expires': '-1',
            'Content-Type': 'text/plain'
            }
    if not isinstance(data, basestring):
        try:
            data = flask.json.dumps(data, indent=4, sort_keys=True, skipkeys=True)
            headers['Content-type'] = 'application/json'
        except TypeError:
            data = str(data)
    return app.make_response((data, code, headers))


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/simple')
def simple():
    return 'ok'


@app.route('/env')
def environ():
    return response(dict(os.environ))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    # For uwsgi
    application = app
