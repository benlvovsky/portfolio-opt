import dx
import math
import scipy.interpolate as sci
import scipy.optimize as sco
import numpy as np

class CPL(object):
    def __init__(self, port, vol, ret):
        self.port = port
        self.vol = vol
        self.ret = ret
        self.port.optimize('Vol', constraint=float(self.ret), constraint_type='Exact')

    def toJson(self):
        s = '{"OptimalPorfolio":\n{'
        s += '"opt_vol":{:},\n"opt_ret":{:}\n,"OP":'.format(self.vol, self.ret)
        s += self.port.toJson()
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

    def __init__(self, name, mar_env):
        super(MeanVariancePortfolio, self).__init__(name, mar_env)

    def toJson(self):
        s = '{"Portfolio":\n {\n'
        s += '"name":"%s",\n' % self.name
        s += '"return":%10.3f,\n' % self.portfolio_return
        s += '"volatility":%10.3f,\n' % math.sqrt(self.variance)
        s += '"Sharpe ratio":%10.3f,\n' % (self.portfolio_return /
                                             math.sqrt(self.variance))
        s += '"Positions":[\n'
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
        f_eff_der = f_eff.derivative(1)

        def tangent(x, rl=riskless_asset):
            return f_eff_der(x) * x / (f_eff(x) - rl) - 1

        left_start = x[0]
        right_start = x[-1]

        left, right = self.search_sign_changing(
            left_start, right_start, tangent, right_start - left_start)
        if left == 0 and right == 0:
            raise ValueError('Can not find tangent.')

        zero_x = sco.brentq(tangent, left, right)

        opt_return = f_eff(zero_x)
        cpl = lambda x: f_eff_der(zero_x) * x + riskless_asset
#         return cpl, zero_x, float(opt_return)

        return CPL(self, zero_x, float(opt_return))

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
