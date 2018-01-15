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
    return uploadcsvGeneric('/upload', 'upload', mark.sharpeAndCml)


@app.route('/upload1', methods=['POST'])
def uploadcsv1():
    return uploadcsvGeneric('/upload1', 'upload1', mark.sharpeAndCml)


@app.route('/uploadasync', methods=['POST'])
def uploadasync():
    return uploadcsvGeneric('/uploadasync', 'upload1', mark.sharpeAndCmlAsync)


@app.route('/getasynctaskresult')
def checkAsyncCompletion():
    uuid = request.args.get('uuid')
    print ('request uuid={}'.format(uuid))
    return prettyJson(mark.getAsyncTaskResult(uuid))


@app.route('/getlistasynctasks')
def getlistasynctasks():
    return prettyJson(mark.getListAsyncTasks())


@app.route('/getasynctaskstatus')
def getasynctaskstatus():
    uuid = request.args.get('uuid')
    print ('request uuid={}'.format(uuid))
    return prettyJson(mark.getAsyncTaskStatus(uuid))


def uploadcsvGeneric(endPointName, sourceName, calcFunc):
    print 'Endpoint Name = {}, Source Name = {}'.format(endPointName, sourceName)
    f = request.files['the_file']
    uploadDir = st.config["common"]["upload_directory"]

    if not os.path.exists(uploadDir):
        os.makedirs(uploadDir)
    f.save('{}/{}'.format(uploadDir, st.config["common"]["upload_file_name"]))

    return prettyJson(calcFunc(sourceName, determineRiskFree(request.form.get('riskfree')), []))

def determineRiskFree(riskFree):
    print ('request riskfree={}'.format(riskFree))
    if riskFree is None:
        riskFree = st.config["efficient_frontier"]["default_riskfree"]
        print 'No riskfree provided in request arguments => take a default value of {}'.format(riskFree)
    else:
        print 'Using provided riskfree = {}'.format(riskFree)

    return float(riskFree)

def prettyJson(notPretty):
    outDir = 'output'
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    with open(outDir + '/lastjson_notpretty.js', 'w') as outfile:
        outfile.write(notPretty)
    notPretty = notPretty.replace('\r\n', '')
    parsed = json.loads(notPretty)
    jsStr = json.dumps(parsed, indent=4, sort_keys=True)
    # with open(outDir + '/lastjsonresponse.js', 'w') as outfile:
    #     outfile.write(jsStr)
    return jsStr

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
