#!/usr/bin/env python

import PyQt4
import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt

from dx import *
import seaborn as sns;

sns.set()

def main():
    sharpeAndCml()

def sharpeAndCml():

    # ### Sharpe Ratio

    # We start by instantiating a `market environment` object which in particular contains a list of **ticker symbols** in which we are interested in.
    ma = market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', ['AAPL', 'GOOG', 'MSFT', 'FB'])
    ma.add_constant('source', 'google')
    ma.add_constant('final date', dt.date(2014, 3, 1))

    # Using pandas under the hood, the class **retrieves historial stock price data** from either Yahoo! Finance of Google.

    port = mean_variance_portfolio('am_tech_stocks', ma)
    # instantiates the portfolio class
    # and retrieves all the time series data needed")
    
    # Often, the target of the portfolio optimization efforts is the so called **Sharpe ratio**. The `mean_variance_portfolio` class of DX Analytics assumes a **risk-free rate of zero** in this context.
    print 'Often, the target of the portfolio optimization efforts is the so called **Sharpe ratio**. The `mean_variance_portfolio` class of DX Analytics assumes a **risk-free rate of zero** in this context.'
    
    port.optimize('Sharpe')
      # maximize Sharpe ratio

    print(port)

    # ## Efficient Frontier
    
    # Another application area is to derive the **efficient frontier** in the mean-variance space. These are all these portfolios for which there is **no portfolio with both lower risk and higher return**. The method `get_efficient_frontier` yields the desired results.
    print 'Another application area is to derive the **efficient frontier** in the mean-variance space. These are all these portfolios for which there is **no portfolio with both lower risk and higher return**. The method `get_efficient_frontier` yields the desired results.'
    
    evols, erets = port.get_efficient_frontier(100)
    # 100 points of the effient frontier')
    # The plot with the **random and efficient portfolios**.
    plt.figure(figsize=(10, 6))
#     plt.scatter(vols, rets, c=rets / vols, marker='o')
    plt.scatter(evols, erets, c=erets / evols, marker='x')
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.colorbar(label='Sharpe ratio')
    plt.show()
    # ## Capital Market Line
    
    # The **capital market line** is another key element of the mean-variance portfolio approach representing all those risk-return combinations (in mean-variance space) that are possible to form from a **risk-less money market account** and **the market portfolio** (or another appropriate substitute efficient portfolio).
    print 'The **capital market line** is another key element of the mean-variance portfolio approach representing all those risk-return combinations (in mean-variance space) that are possible to form from a **risk-less money market account** and **the market portfolio** (or another appropriate substitute efficient portfolio).'
    
    cml, optv, optr = port.get_capital_market_line(riskless_asset=0.05)
    # capital market line for effiecient frontier and risk-less short rate')
    print 'capital market line for effiecient frontier and risk-less short rate'
    cml  # lambda function for capital market line
    print cml  # lambda function for capital market line
    
    # The following plot illustrates that the capital market line has an ordinate value equal to the **risk-free rate** (the safe return of the money market account) and is tangent to the **efficient frontier**.
    print 'The following plot illustrates that the capital market line has an ordinate value equal to the **risk-free rate** (the safe return of the money market account) and is tangent to the **efficient frontier**.'
    plt.figure(figsize=(10, 6))
    plt.plot(evols, erets, lw=2.0, label='efficient frontier')
    plt.plot((0, 0.4), (cml(0), cml(0.4)), lw=2.0, label='capital market line')
    plt.plot(optv, optr, 'r*', markersize=10, label='optimal portfolio')
    plt.legend(loc=0)
    plt.ylim(0)
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.show()

    # Portfolio return and risk of the efficient portfolio used are:
    print 'Portfolio return and risk of the efficient portfolio used are:'
    print optr
    print optv

    # The **portfolio composition** can be derived as follows.
    print 'The **portfolio composition** can be derived as follows.'
    port.optimize('Vol', constraint=optr, constraint_type='Exact')
    print(port)

    # Or also in this way.
    print 'Or also in this way.'
    port.optimize('Return', constraint=optv, constraint_type='Exact')
    print(port)
    
def various():
    # ## Market Environment and Portfolio Object

    # We start by instantiating a `market environment` object which in particular contains a list of **ticker symbols** in which we are interested in.
    ma = market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', ['AAPL', 'GOOG', 'MSFT', 'FB'])
    ma.add_constant('source', 'google')
    ma.add_constant('final date', dt.date(2014, 3, 1))

    # Using pandas under the hood, the class **retrieves historial stock price data** from either Yahoo! Finance of Google.

    port = mean_variance_portfolio('am_tech_stocks', ma)
    # instantiates the portfolio class
    # and retrieves all the time series data needed")
    
    # ## Basic Statistics
    
    # Since no **portfolio weights** have been provided, the class defaults to equal weights.
    print 'default to equal weights.'
    print port.get_weights()
    # defaults to equal weights
   
    # Given these weights you can calculate the **portfolio return** via the method `get_portfolio_return`.
    print '**portfolio return** via the method `get_portfolio_return` for these weights:'
    
    print port.get_portfolio_return()
    # expected (= historical mean) return
    
    # Analogously, you can call `get_portfolio_variance` to get the historical **portfolio variance**.
    print '`get_portfolio_variance` to get the historical **portfolio variance**'
    print port.get_portfolio_variance()
     # expected (= historical) variance
    
    # The class also has a neatly printable `string` representation.
    print 'neatly printable `string` representation:'
    print(port)

      # ret. con. is "return contribution"
      # given the mean return and the weight
      # of the security
      
    print '''
      ret. con. is "return contribution"
      given the mean return and the weight
      of the security
    '''
    # ## Setting Weights
    # Via the method `set_weights` the weights of the single portfolio components can be adjusted.
    print 'Via the method `set_weights` the weights of the single portfolio components can be adjusted.'
    port.set_weights([0.6, 0.2, 0.1, 0.1])
    print port

    # You cal also easily **check results for different weights** with changing the attribute values of an object.
    print 'You cal also easily **check results for different weights** with changing the attribute values of an object'
    port.test_weights([0.6, 0.2, 0.1, 0.1])
    print '''
    returns av. return + vol + Sharp ratio
    without setting new weights
    '''
    # Let us implement a **Monte Carlo simulation** over potential portfolio weights.
    
    # Monte Carlo simulation of portfolio compositions
    rets = []
    vols = []
    
    for w in range(500):
        weights = np.random.random(4)
        weights /= sum(weights)
        r, v, sr = port.test_weights(weights)
        rets.append(r)
        vols.append(v)
    
    rets = np.array(rets)
    vols = np.array(vols)
    
    # And the simulation results **visualized**.

    # get_ipython().magic(u'matplotlib inline')
    plt.figure(figsize=(10, 6))
    plt.scatter(vols, rets, c=rets / vols, marker='o')
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.colorbar(label='Sharpe ratio')
    plt.show()
    # ## Optimizing Portfolio Composition
    
    # One of the major application areas of the mean-variance portfolio theory and therewith of this DX Analytics class it the **optimization of the portfolio composition**. Different target functions can be used to this end.
    
    # ### Return
    
    # The first target function might be the **portfolio return**.
    
    port.optimize('Return')
    # maximizes expected return of portfolio
    # no volatility constraint
    
    print(port)

    # Instead of maximizing the portfolio return without any constraints, you can also set a (sensible/possible) **maximum target volatility** level as a constraint. Both, in an **exact sense** ("equality constraint") ...
    print 'Instead of maximizing the portfolio return without any constraints, you can also set a (sensible/possible) **maximum target volatility** level as a constraint. Both, in an **exact sense** ("equality constraint") ...'

    port.optimize('Return', constraint=0.225, constraint_type='Exact')
      # interpretes volatility constraint as equality
    
    print(port)
    
    # ... or just a an **upper bound** ("inequality constraint").
    print '... or just a an **upper bound** ("inequality constraint").'
    port.optimize('Return', constraint=0.4, constraint_type='Bound')
      # interpretes volatility constraint as inequality (upper bound)
    print(port)

    # ### Risk
    
    # The class also allows you to minimize **portfolio risk**.
    print 'The class also allows you to minimize **portfolio risk**.'
    port.optimize('Vol')
      # minimizes expected volatility of portfolio
      # no return constraint
    
    print(port)
    
    
    # And, as before, to set **constraints** (in this case) for the target return level.
    
    port.optimize('Vol', constraint=0.175, constraint_type='Exact')
      # interpretes return constraint as equality
    
    print(port)
    
    port.optimize('Vol', constraint=0.20, constraint_type='Bound')
      # interpretes return constraint as inequality (upper bound)
    
    print(port)
    
    # ### Sharpe Ratio
    
    # Often, the target of the portfolio optimization efforts is the so called **Sharpe ratio**. The `mean_variance_portfolio` class of DX Analytics assumes a **risk-free rate of zero** in this context.
    print 'Often, the target of the portfolio optimization efforts is the so called **Sharpe ratio**. The `mean_variance_portfolio` class of DX Analytics assumes a **risk-free rate of zero** in this context.'
    
    port.optimize('Sharpe')
      # maximize Sharpe ratio

    print(port)

    # ## Efficient Frontier
    
    # Another application area is to derive the **efficient frontier** in the mean-variance space. These are all these portfolios for which there is **no portfolio with both lower risk and higher return**. The method `get_efficient_frontier` yields the desired results.
    print 'Another application area is to derive the **efficient frontier** in the mean-variance space. These are all these portfolios for which there is **no portfolio with both lower risk and higher return**. The method `get_efficient_frontier` yields the desired results.'
    
    evols, erets = port.get_efficient_frontier(100)
    # 100 points of the effient frontier')
    # The plot with the **random and efficient portfolios**.
    plt.figure(figsize=(10, 6))
    plt.scatter(vols, rets, c=rets / vols, marker='o')
    plt.scatter(evols, erets, c=erets / evols, marker='x')
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.colorbar(label='Sharpe ratio')
    plt.show()
    # ## Capital Market Line
    
    # The **capital market line** is another key element of the mean-variance portfolio approach representing all those risk-return combinations (in mean-variance space) that are possible to form from a **risk-less money market account** and **the market portfolio** (or another appropriate substitute efficient portfolio).
    print 'The **capital market line** is another key element of the mean-variance portfolio approach representing all those risk-return combinations (in mean-variance space) that are possible to form from a **risk-less money market account** and **the market portfolio** (or another appropriate substitute efficient portfolio).'
    
    cml, optv, optr = port.get_capital_market_line(riskless_asset=0.05)
    # capital market line for effiecient frontier and risk-less short rate')
    print 'capital market line for effiecient frontier and risk-less short rate'
    cml  # lambda function for capital market line
    print cml  # lambda function for capital market line
    
    # The following plot illustrates that the capital market line has an ordinate value equal to the **risk-free rate** (the safe return of the money market account) and is tangent to the **efficient frontier**.
    print 'The following plot illustrates that the capital market line has an ordinate value equal to the **risk-free rate** (the safe return of the money market account) and is tangent to the **efficient frontier**.'
    plt.figure(figsize=(10, 6))
    plt.plot(evols, erets, lw=2.0, label='efficient frontier')
    plt.plot((0, 0.4), (cml(0), cml(0.4)), lw=2.0, label='capital market line')
    plt.plot(optv, optr, 'r*', markersize=10, label='optimal portfolio')
    plt.legend(loc=0)
    plt.ylim(0)
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.show()

    # Portfolio return and risk of the efficient portfolio used are:
    print 'Portfolio return and risk of the efficient portfolio used are:'
    print optr
    print optv

    # The **portfolio composition** can be derived as follows.
    print 'The **portfolio composition** can be derived as follows.'
    port.optimize('Vol', constraint=optr, constraint_type='Exact')
    print(port)

    # Or also in this way.
    print 'Or also in this way.'
    port.optimize('Return', constraint=optv, constraint_type='Exact')
    print(port)

def dowjones() :

    # ## Dow Jones Industrial Average
    
    # As a larger, more realistic example, consider **all symbols of the Dow Jones Industrial Average 30 index**.
    
    symbols = ['AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE',
        'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
        'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'T', 'TRV', 'UNH', 'UTX',
        'V', 'VZ','WMT', 'XOM']
      # all DJIA 30 symbols
    
    ma = market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', symbols)
    ma.add_constant('source', 'google')
    ma.add_constant('final date', dt.date(2014, 3, 1))
    
    
    # **Data retrieval** in this case takes a bit.
    
    djia = mean_variance_portfolio('djia', ma)
    # defining the portfolio and retrieving the data")
    
    djia.optimize('Vol')
    print(djia.variance, djia.variance ** 0.5)
    # minimium variance & volatility in decimals")
    
    # Given the larger data set now used, **efficient frontier** ...
    
    evols, erets = djia.get_efficient_frontier(25)
    # efficient frontier of DJIA')
    # ... and **capital market line** derivations take also longer.
    cml, optv, optr = djia.get_capital_market_line(riskless_asset=0.01)
    # capital market line and optimal (tangent) portfolio')
    
    plt.figure(figsize=(10, 6))
    plt.plot(evols, erets, lw=2.0, label='efficient frontier')
    plt.plot((0, 0.4), (cml(0), cml(0.4)), lw=2.0, label='capital market line')
    plt.plot(optv, optr, 'r*', markersize=10, label='optimal portfolio')
    plt.legend(loc=0)
    plt.ylim(0)
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.show()

if __name__ == "__main__":
    main()
