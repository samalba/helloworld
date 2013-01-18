#!/usr/bin/env python

import os
import string
import random
import flask
from flask import Flask

import models


app = Flask(__name__)
app.debug = True


def detect_paas():
    if 'DOTCLOUD_PROJECT' in os.environ:
        return 'dotcloud'
    if 'VCAP_APPLICATION' in os.environ:
        return 'appfog'
    if os.environ.get('PYTHONHOME') and os.environ.get('PYTHONHOME').startswith('/app/.heroku/'):
        return 'heroku'
    return 'local'


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


@app.route('/db')
def db():
    gen_rand = lambda: ''.join(random.choice(string.letters) for i in xrange(256))
    paas = detect_paas()
    session = models.get_session(paas)
    # Test writing to the DB
    for i in xrange(50):
        session.add(models.Test(payload=gen_rand()))
    session.commit()
    # Test reading
    for obj in session.query(models.Test).all():
        session.delete(obj)
    session.commit()
    return 'ok'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    # For uwsgi
    application = app
