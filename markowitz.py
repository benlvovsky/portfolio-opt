#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')
#matplotlib.use('qt5agg')
#matplotlib.use('qt4agg')
#import PyQt4
import matplotlib.pyplot as plt

import json
from dx import *
import seaborn as sns;
import copy
import settings as st
import meanvarianceportfolio as mvp
from scipy import interpolate
import sympy

sns.set()

asxTop20 = ['CBA.AX','WBC.AX','BHP.AX','ANZ.AX','NAB.AX','CSL.AX','WES.AX','TLS.AX','WOW.AX',\
            'MQG.AX','RIO.AX','TCL.AX','WPL.AX','SCG.AX',\
#             'SUN.AX',\
            'WFD.AX','IAG.AX','AMP.AX','BXB.AX','QBE.AX']
original = ['AAPL', 'GOOG', 'MSFT', 'FB']

def main():
    sharpeAndCml(source='upload')

def getEfficientFrontierPortfolios(port, evols):
    portfolios = list()
    for v in evols:
        port.optimize('Return', constraint=v, constraint_type='Exact')
        portfolios.append(copy.copy(port))
    
    return portfolios


def calcCPL(x, y, y_zero):
    '''
    Find an equation for the line that is tangent to the curve x^{3} - x at point (-1, 0)
    Confirm your estimates of the coordinates of the second intersection point by solving the equations for the curve
    and tangent simultaneously
    '''
    # interpolate the data with a spline
    spl = interpolate.splrep(x,y)
    y = x**3 - x
      
    # find the derivative of y
    dy = sympy.diff(y, x)
      
    # find slope of the tangent line and equation
    m = dy.subs(x, -1)
    y1 = m*(x + 1)
      
    # draw the curve and line
    plot(y, y1, (x, -5, 5), ylim=(-10, 10))
      
    # above line equation = the curve function, 2x + 2 = x**3 - x
    rt = sympy.solve(x**3 - 3*x - 2, x)
    print rt
    # the roots are -1 and 2
#     [-1, 2]
      
    # checking the roots better use boolean operation but visual inspection is simple
    y1.subs(x, -1), y.subs(x, -1), y1.subs(x, 2), y.subs(x, 2)
    # Output[105]: (0, 0, 6, 6)

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
#         cpl = calcCPL(effFrontier.vols, effFrontier.rets, riskless_asset=0.05)
        cpl = port.get_capital_market_line_bl_1(effFrontier.vols, effFrontier.rets, riskless_asset=0.05)
        exit(0)
#         retVal += '"CML":' + cpl.toJson()
    except Exception, e:
#         cpl = mvp.CPL(port, effFrontier.vols[0], effFrontier.rets[0], 0.05)
        retVal += '"CML": {{"error":"{}"}}'.format(str(e))
#         retVal += '"CML":' + cpl.toJson()

    retVal += "\n}"

    print retVal
    
    return retVal

if __name__ == "__main__":
    main()
