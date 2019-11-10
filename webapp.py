from flask import Flask
from pflib import markowitz as mark
from flask import request

app = Flask(__name__)


@app.route('/health')
def health_check():
    return '''
    {
    result: OK
    }'''


@app.route('/portfolio-request', methods=['POST'])
def portfolio_request():
    return mark.get_portfolio(request)
