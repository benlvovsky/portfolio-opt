from flask import Flask
from pflib import markowitz as mark
from flask import request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/health')
def health_check():
    return '''
    {
    result: OK
    }'''


@app.route('/portfolio-request', methods=['POST'])
def portfolio_request():
    return mark.get_portfolio(request)


@app.route('/upload-file/<file_name>', methods=['POST'])
def upload_file(file_name):
    return jsonify(mark.upload_file(request, file_name))


@app.route('/portfolio-point', methods=['POST'])
def portfolio_point():
    return mark.get_portfolio_point(request)
