#!/usr/bin/env python

import json
from dx import *
import seaborn as sns;
import copy
import settings as st
import meanvarianceportfolio as mvp

sns.set()

asxTop20 = ['CBA.AX','WBC.AX','BHP.AX','ANZ.AX','NAB.AX','CSL.AX','WES.AX','TLS.AX','WOW.AX',\
            'MQG.AX','RIO.AX','TCL.AX','WPL.AX','SCG.AX',\
#             'SUN.AX',\
            'WFD.AX','IAG.AX','AMP.AX','BXB.AX','QBE.AX']
original = ['AAPL', 'GOOG', 'MSFT', 'FB']

def main():
    sharpeAndCml(source='google')

def getEfficientFrontierPortfolios(port, evols):
    portfolios = list()
    for v in evols:
        port.optimize('Return', constraint=v, constraint_type='Exact')
        portfolios.append(copy.copy(port))
    
    return portfolios

def sharpeAndCml(source='google', symbols=original):
    ma = market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', symbols)
    ma.add_constant('source', source)
    ma.add_constant('final date', dt.date(2014, 3, 1))
    port = mvp.MeanVariancePortfolio('am_tech_stocks', ma)
    effFrontier = port.get_efficient_frontier_bl(st.config["efficient_frontier"]["points_number"])
    
    retVal = '{\n'
    retVal += '"EfficientPortfolios":'
    retVal += effFrontier.toJson()
    retVal += ',\n'

    try:
        cpl = port.get_capital_market_line_bl(effFrontier.vols, effFrontier.rets, riskless_asset=0.05)
        retVal += '"CML":' + cpl.toJson()
    except Exception, e:
        cpl = None
        retVal += '"CML": {{"error":"{}"}}'.format(str(e))

    retVal += "\n}"

    print retVal
    
    return retVal

if __name__ == "__main__":
    main()
