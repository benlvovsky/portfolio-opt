#!/usr/bin/env python

import json
from dx import *
import seaborn as sns;
import copy
import settings as st
import meanvarianceportfolio as mvp

sns.set()

def main():
    sharpeAndCml(source='upload')

def getEfficientFrontierPortfolios(port, evols):
    portfolios = list()
    for v in evols:
        port.optimize('Return', constraint=v, constraint_type='Exact')
        portfolios.append(copy.copy(port))
    
    return portfolios

def sharpeAndCml(source='google', symbols=['AAPL', 'GOOG', 'MSFT', 'FB']):
    ma = market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', symbols)
    ma.add_constant('source', source)
    ma.add_constant('final date', dt.date(2014, 3, 1))
    port = mvp.MeanVariancePortfolio('am_tech_stocks', ma)
    effFrontier = port.get_efficient_frontier_bl(st.config["efficient_frontier"]["points_number"])
    
    retVal = '{\n'
    retVal += '"EfficientPortfolios":'
    retVal += effFrontier.toJson()
    cpl = port.get_capital_market_line_bl(effFrontier.vols, effFrontier.rets, riskless_asset=0.05)
# 
    retVal += ',\n'
    retVal += '"CML":' + cpl.toJson()
    retVal += "\n}"

    print retVal
    
    return retVal

if __name__ == "__main__":
    main()
