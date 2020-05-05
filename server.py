from flask import Flask, request

import json
from model.NewModel import runModel
from collections import namedtuple


# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print(" * note: flask_cors not installed, service will not be accessible externally")


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    # magic to turn json into an object instead of a dict
    # https://stackoverflow.com/a/15882054
    policySettings = json.load(request.stream, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    if policySettings.NumPatients:
        results = runModel(policySettings, policySettings.NumPatients)
    else:
        results = runModel(policySettings)

    # patient objects are not inherently serializable,
    # and contain some attributes which are not serializable.
    # here we convert patient objects to dicts (which are serializable)
    # and remove the attributes which are not serializable
    for p in results['patients']:
        d = p.__dict__
        d.pop('plan', None)
        d.pop('policySettings', None)

    results['patients'] = [p.__dict__ for p in results['patients']]

    return results
