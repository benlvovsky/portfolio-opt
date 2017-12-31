import matplotlib
#matplotlib.use('qt4agg')
#matplotlib.use('qt5agg')
#import PyQt5
import matplotlib.pyplot as plt

import dx
import math
import scipy
import scipy.interpolate as sci
import scipy.optimize as sco
import numpy as np
import pandas as pd
import datetime as dt
import copy
from sympy.physics.quantum.cartesian import YOp

# from pylab import plot,show

class CPL(object):
    def __init__(self, port, vol, ret, riskFree):
        self.port = copy.deepcopy(port)
        self.vol = vol
        self.ret = ret
        self.riskFree = riskFree
        self.port.optimize('Vol', constraint=float(self.ret), constraint_type='Exact')

    def toJson(self):
        s = '{"OptimalPorfolio":\n{'
        s += '"opt_vol":{:},\n"opt_ret":{:}\n,"riskfree_ret":{:}\n,'.format(self.vol, self.ret, self.riskFree)
        s += '"OP":' + self.port.toJson()
        s += '\n}\n}'
        return s

class EfficientFrontier(object):
    def __init__(self, vols, rets, sharpe, weights, symbols):
        self.vols = vols
        self.rets = rets
        self.sharpe = sharpe
        self.weights = weights
        self.symbols = symbols

    def toJson(self):
        s = '{"Points":[\n'
        for i in range(len(self.vols)):
            s += '{\n'
            s += '"volatility":{:}'.format(self.vols[i]) + ",\n"
            s += '"return":{:}'.format(self.rets[i]) + ",\n"
            s += '"sharpe":{:}'.format(self.sharpe[i]) + ",\n"
            s += '"weights":[\n'

            for j in range(len(self.symbols)):
                s += '{\n'
                s += '"symbol":"{:}"'.format(self.symbols[j]) + ",\n"
                s += '"weight":{:}'.format(self.weights[i][j]) + "\n"
                s += '}\n'
                if j < len(self.symbols) - 1:
                    s += ','
                    
            s += ']\n}\n'

            if i < len(self.vols) - 1:
                s += ','

        s += ']\n}'

        return s


class MeanVariancePortfolio(dx.mean_variance_portfolio):

    def preInit(self):
        if self.mar_env.get_constant('source') == 'upload':
            self.dfUploadData = pd.DataFrame()
            self.dfUploadData = pd.read_csv('upload/data.csv', header=None, names = ['symbol', 'date', 'close', 'open', 'high', 'low', 'volume'], 
                             sep=';', parse_dates=['date'])
            self.symbolsDf = self.dfUploadData.drop_duplicates(['symbol'])['symbol'].values
            self.mar_env.add_list('symbols', self.symbolsDf)
            self.mar_env.add_constant('final date', dt.date(2014, 3, 1)) # ust arbitraty constant as it is not used for upload

    def __init__(self, name, mar_env):
        self.mar_env = mar_env
        self.preInit()
        super(MeanVariancePortfolio, self).__init__(name, self.mar_env)

    def toJson(self):
        s = '{"Portfolio":\n {\n'
        s += '"name":"%s",\n' % self.name
        s += '"return":%10.3f,\n' % self.portfolio_return
        s += '"volatility":%10.3f,\n' % math.sqrt(self.variance)
        s += '"sharpe":%10.3f,\n' % (self.portfolio_return /
                                             math.sqrt(self.variance))
        s += '"weights":[\n'
    #         s += 'symbol | weight | ret. con. \n'
        for i in range(len(self.symbols)):
            s += '{\n'
            s += '"symbol":"{:}"'.format(self.symbols[i]) + ",\n"
            s += '"weight":{:6.3f}'.format(self.weights[i]) + ",\n"
            s += '"mean_return":{:9.3f}'.format(self.mean_returns[i]) + "\n"
            s += '}\n'
            if i < len(self.symbols) - 1:
                s += ','
    
        s += ']\n}\n}\n'
    
        return s
    
    def draw_tangent(self, x,y,a, lineType="--b"):
        # interpolate the data with a spline
        spl = sci.splrep(x,y)   # bl Find the B-spline representation of 1-D curve
#    bl: original        small_t = scipy.arange(a-5,a+5)
#         small_t = scipy.arange(x[0], a*1.2, 0.01)
        small_t = scipy.arange(0, a*1.2, 0.01)
#         print 'segment x array: {}'.format(small_t)
#         exit(0)
        
        # bl Evaluate a B-spline (derivative = 0) for x point 'a'
        # return the value (y coordinate) of the smoothed spline at x coordinate 'a'
        fa = sci.splev(a,spl,der=0)     # f(a)
        
        # bl Evaluate a 1st derivative of B-spline (tangent)
        # return the value (y coordinate) of the smoothed spline at x coordinate 'a' of derivative 1 (tangent)
        fprime = sci.splev(a,spl,der=1) # f'(a)
        tan = fa+fprime*(small_t-a) # tangent y array (x: small_t)
#         print 'segment y array: {}'.format(tan)
        plt.plot(a,fa,'om',small_t,tan, lineType)

    def calcYforZeroXOfTangent(self, spl, a):
        # bl Evaluate a B-spline (derivative = 0) for x point 'a'
        # return the value (y coordinate) of the smoothed spline at x coordinate 'a'
        fa = sci.splev(a,spl,der=0)     # f(a)
        # bl Evaluate a 1st derivative of B-spline (tangent)
        # return the value (y coordinate) of the smoothed spline at x coordinate 'a' of derivative 1 (tangent)
        small_t = scipy.arange(0, a*1.2, 0.01)

        fprime = sci.splev(a,spl,der=1) # f'(a)
        tanYArr = fa+fprime*(small_t-a) # tangent y coords array
#         print 'zero X tangent segment y array: {}'.format(tanYArr)
        return tanYArr[0]

    def findXForOptimalTangent(self, xSegment, spl, risklessY):
        prevTangentY = -1
        for i in range(1, len(xSegment)-1):
            tangentY = self.calcYforZeroXOfTangent(spl, xSegment[i])
            if tangentY > risklessY:
                print 'tangentY Found {} at xSegment[{}]={}, len(xSegment) = {}, previous prevTangentY={}'\
                    .format(tangentY, i, xSegment[i], len(xSegment), prevTangentY)
                return xSegment[i], tangentY, i
            else:
                prevTangentY = tangentY

        print 'tangentY Not found'
        return xSegment[1], prevTangentY, 1

    def get_capital_market_line_bl_1(self, x, y, riskless_asset):
        print 'len(x)={}'.format(len(x))
        spl = sci.splrep(x,y)   # bl Find the B-spline representation of 1-D curve

        (xOpt, yOnZeroX, idx) = self.findXForOptimalTangent(x, spl, riskless_asset)
        fineGrainedXArr = scipy.arange(x[idx-1], x[idx], (x[idx] - x[idx - 1]) / 20)
        (xOpt, yOnZeroX, idx) = self.findXForOptimalTangent(fineGrainedXArr, spl, riskless_asset)
        fineGrainedXArr = scipy.arange(fineGrainedXArr[idx-1], fineGrainedXArr[idx], (fineGrainedXArr[idx] - fineGrainedXArr[idx - 1]) / 20)
        (xOpt, yOnZeroX, idx) = self.findXForOptimalTangent(fineGrainedXArr, spl, riskless_asset)

        self.draw_tangent(x, y, xOpt, lineType="--g")
        plt.plot(x, y, alpha=0.5)
        plt.plot(0, riskless_asset, 'om')
        plt.plot(0, yOnZeroX,'og')
#         plt.show()
        yOpt = sci.splev(xOpt, spl, der=0)     # f(a)
        plt.plot(xOpt, yOpt, 'b^')
        plt.savefig("efffrontier.png")

        weights = self.get_optimal_weights('Return', constraint=xOpt)
#TODO: incorporate weights        return CPL(weights, xOpt, yOnZeroX, riskless_asset)
        return CPL(self, xOpt, yOpt, riskless_asset)
#         exit(0)

    def get_capital_market_line_bl(self, x, y, riskless_asset):
        '''
        Returns the capital market line as a lambda function and
        the coordinates of the intersection between the captal market
        line and the efficient frontier

        Parameters
        ==========

        riskless_asset: float
            the return of the riskless asset
        x, y arrays - result from previously called get_efficient_frontier
        '''
# use x,y fromparameters - no need to call again get_efficient_frontier       x, y = self.get_efficient_frontier(100)

        if len(x) == 1:
            raise ValueError('Efficient Frontier seems to be constant.')
        f_eff = sci.UnivariateSpline(x, y, s=0)
# bl        f_eff = sci.InterpolatedUnivariateSpline(x, y)
        f_eff_der = f_eff.derivative(1)

        def tangent(x, rl=riskless_asset):
            return f_eff_der(x) * x / (f_eff(x) - rl) - 1

        left_start = x[0]
        right_start = x[-1]

        left, right = self.search_sign_changing_bl(
            left_start, right_start, tangent, right_start - left_start)
        if left == 0 and right == 0:
            sErr = "error: Can not find tangent. left == 0 and right == 0"
            print sErr
            raise ValueError(sErr)
#             return CPL(self, x[0], y[0], riskless_asset) # temp fix

        zero_x = sco.brentq(tangent, left, right)

        opt_return = f_eff(zero_x)
        cpl = lambda x: f_eff_der(zero_x) * x + riskless_asset

        print "return CPL()"
        return CPL(self, zero_x, float(opt_return), riskless_asset)

    def search_sign_changing_bl(self, l, r, f, d):
        print 'search_sign_changing_bl: left={}, right={}, d={}'.format(l, r, d)
        if d < 0.000001:
# orig            return (0, 0)
            return (l, r) # bl: if [d] is too small - return what we got so far
        for x in np.arange(l, r + d, d):
            if f(l) * f(x) < 0:
                ret = (x - d, x)
                return ret

        ret = self.search_sign_changing_bl(l, r, f, d / 2.)
        return ret

    def get_efficient_frontier_bl(self, n):
        '''
        Returns the efficient frontier in form of lists containing the x and y
        coordinates of points of the frontier.

        Parameters
        ==========
        n : int >= 3
            number of points
        '''
        if type(n) is not int:
            raise TypeError('n must be an int')
        if n < 3:
            raise ValueError('n must be at least 3')

        min_vol_weights = self.get_optimal_weights('Vol')
        min_vol = self.test_weights(min_vol_weights)[1]
        min_return_weights = self.get_optimal_weights('Return',
                                                      constraint=min_vol)
        min_return = self.test_weights(min_return_weights)[0]
        max_return_weights = self.get_optimal_weights('Return')
        max_return = self.test_weights(max_return_weights)[0]

        delta = (max_return - min_return) / (n - 1)

        vols = list()
        rets = list()
        sharpe = list()
        weights = list()
        
        if delta > 0:
            returns = np.arange(min_return, max_return + delta, delta)
            for r in returns:
                w = self.get_optimal_weights('Vol', constraint=r,
                                             constraint_type='Exact')
                if w is not False:
                    result = self.test_weights(w)
                    rets.append(result[0])
                    vols.append(result[1])
                    sharpe.append(result[2])
                    weights.append(w)
        else:
            rets.apppend(max_return)
            vols.append(min_vol)
            weights.append([0,])
            sharpe.append(0)

        return EfficientFrontier(vols, rets, sharpe, weights, self.symbols)

    def load_data(self):
        '''
        Overridden loads csv if was uploaded or calls super implementation
        '''

        if self.source == 'upload':
            dfRet = pd.DataFrame()
            for i, sym in enumerate(self.symbolsDf):
                newSymData = self.dfUploadData.loc[self.dfUploadData['symbol'] == sym][['date', 'close']]
                newSymData.columns = ['date', sym]
                if i < 1:
                    dfRet = newSymData.copy()
                else:
                    dfRet = pd.merge(dfRet, newSymData, on='date')

            reversed = dfRet.set_index('date')
#             reversed.to_csv('set_index_date.csv')
            reversed = reversed.reindex(index=reversed.index[::-1])
#             reversed.to_csv('set_index_date.csv')
#             self.data = reversed.drop('date', axis = 1)
            self.data = reversed
            self.data.columns = self.symbolsDf

            self.data.to_csv('symbolsTransposed.csv')
        else:
            super(MeanVariancePortfolio, self).load_data()
