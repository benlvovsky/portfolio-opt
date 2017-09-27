import markowitz as mark
from flask import Flask
from flask import request
import json
import settings as st
import os

app = Flask(__name__)

@app.route('/health')
def hello_world():
    return '''
    {
    result: OK
    }'''

@app.route('/ef')
def efficientFrontier():
    markJson =  mark.sharpeAndCml()
    parsed = json.loads(markJson)
    prettyJson = json.dumps(parsed, indent=4, sort_keys=True)
    return prettyJson

@app.route('/upload', methods=['POST'])
def uploadcsv():
    f = request.files['the_file']
    uploadDir = st.config["common"]["upload_directory"]
    
    if not os.path.exists(uploadDir):
        os.makedirs(uploadDir)
    f.save('{}/{}'.format(uploadDir, st.config["common"]["upload_file_name"]))
    return '''
    {
    result: OK
    }
    '''
