import markowitz as mark
from flask import Flask
from flask import request
import json
import settings as st
import os

app = Flask(__name__)

@app.route('/health')
def healthcheck():
    return '''
    {
    result: OK
    }'''


def determineSource(val):
    # source = request.args.get('source')
    defaultDataSource = st.config["efficient_frontier"]["default_datasource"]
    overrideDataSource = st.config["efficient_frontier"]["override_datasource"]
    print 'dataSource provided=' + val
    print 'defaultDataSource=' + defaultDataSource
    print 'overrideDataSource=' + str(overrideDataSource)

    retVal = val
    if retVal is None:
        retVal = defaultDataSource
    if retVal is None:
        retVal = 'yahoo'
    if (overrideDataSource and defaultDataSource):
        retVal = defaultDataSource
    print ('data source determined={}'.format(retVal))

    return retVal

@app.route('/ef')
def efficientFrontier():
    print ('request source={}'.format(request.args.get('source')))
    print ('request symbols={}'.format(request.args.get('symbols')))
    symbols=request.args.get('symbols')
    if request.args.get('symbols') is None:
        symbols = mark.asxTop20 #['AAPL', 'GOOG', 'MSFT', 'FB']
    else:
        symbols = request.args.get('symbols').split(",")

    return prettyJson(mark.sharpeAndCml(determineSource(request.args.get('source')), determineRiskFree(request.args.get('riskfree')), symbols))

@app.route('/upload', methods=['POST'])
def uploadcsv():
    print 'upload'
    f = request.files['the_file']
    uploadDir = st.config["common"]["upload_directory"]

    if not os.path.exists(uploadDir):
        os.makedirs(uploadDir)
    f.save('{}/{}'.format(uploadDir, st.config["common"]["upload_file_name"]))

    return prettyJson(mark.sharpeAndCml('upload', determineRiskFree(request.form.get('riskfree')), []))

def determineRiskFree(riskFree):
    # riskFree = request.form.get('riskfree')
    print ('request riskfree={}'.format(riskFree))
    if riskFree is None:
        riskFree = st.config["efficient_frontier"]["default_riskfree"]
        print 'No riskfree provided in request arguments => take a default value of {}'.format(riskFree)
    else:
        print 'Using provided riskfree = {}'.format(riskFree)

    return float(riskFree)

def prettyJson(notPretty):
    parsed = json.loads(notPretty)
    return json.dumps(parsed, indent=4, sort_keys=True)
