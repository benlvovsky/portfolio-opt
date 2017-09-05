import markowitz as mark
from flask import Flask
import json

app = Flask(__name__)

@app.route('/hw')
def hello_world():
    return 'Hello, World!'

@app.route('/ef')
def efficientFrontier():
    markJson =  mark.sharpeAndCml()
    parsed = json.loads(markJson)
    prettyJson = json.dumps(parsed, indent=4, sort_keys=True)
    return prettyJson
