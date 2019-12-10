#!/usr/bin/env python

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import risk_models
from pypfopt import expected_returns
import pandas as pd
import settings as st
from threading import Thread
import uuid
import json
from optparse import OptionParser
from datetime import datetime
import pickle
import redis
from deprecated import deprecated
from dateutil.relativedelta import relativedelta

taskDict = {}

back_to_future = False
back_to_future_latest_prices = None

load_cache_func = {
    'redis': lambda cache_key: pickle.loads(redis.Redis('localhost').get(cache_key)),
    'file': lambda cache_key: pickle.load(open(f'{cache_key}.ser', "rb"))
}


store_cache_func = {
    'redis': lambda cache_to_save: redis.Redis('localhost').set(hash(str(cache_to_save)), pickle.dumps(cache_to_save)),
    'file': lambda cache_to_save: pickle.dump(cache_to_save, open(f'{hash(str(cache_to_save))}.ser', "wb"))
}


expected_returns_calc_func = {
    "mean": expected_returns.mean_historical_return,
    "exp": expected_returns.ema_historical_return
}


portfolio2return_func = {
    "sharpe": ("max_sharpe", lambda options: dict(risk_free_rate=options.risk_free)),
    "return": ("efficient_return", lambda options: dict(target_return=options.target_return,
                                                        market_neutral=options.market_neutral)),
    "volatility": ("efficient_risk", lambda options: dict(target_risk=options.target_volatility,
                                                          risk_free_rate=options.risk_free,
                                                          market_neutral=options.market_neutral))
}


def main():

    parser = OptionParser()

    parser.add_option('-e', '--expected-returns-calc', dest="expected_returns_calc", type="choice",
                      help="calculation type of historical return", choices=['mean', 'exp'], default="mean")

    parser.add_option('-p', '--portfolio-to-return', dest="portfolio2return", type="choice",
                      help="what portfolio to calculate", default="sharpe",
                      choices=['sharpe', 'return', 'volatility'])

    parser.add_option('-f', '--risk-free', dest="risk_free",
                      help=f'risk free ({st.config["efficient_frontier"]["default_riskfree"]})',
                      default=st.config["efficient_frontier"]["default_riskfree"], type="float")

    parser.add_option('-r', '--return-target', dest="target_return",
                      help="target_return for minimal volatility calculation",
                      default=None, type="float")

    parser.add_option('-v', '--volatility-target', dest="target_volatility",
                      help="target_volatility for max return",
                      default=None, type="float")

    parser.add_option('-l', '--lower-weight-bound', dest="lower_weight_bound",
                      help="lower weight bound (0)", default=0, type="float")

    parser.add_option('-i', '--higher-weight-bound', dest="higher_weight_bound",
                      help="higher weight bound (1)", default=1, type="float")

    parser.add_option('-n', '--market-neutral', dest="market_neutral", action="store_true",
                      help="market neutral (False)",
                      default=False)

    parser.add_option('-u', '--url-data-upload', dest="url",
                      help=f'url ({st.config["common"]["upload_url"]})',
                      default=st.config["common"]["upload_url"])

    parser.add_option('-c', '--cache-ef', dest="to_cache", default=None,
                      choices=['redis', 'file', '', None],
                      help=f'only calculate and cache efficient frontier for later use')

    parser.add_option('-o', '--reuse-cache', dest="reuse_cache", default=None,
                      choices=['redis', 'file', '', None],
                      help=f'reuse cached ef object from the parameter filename')

    parser.add_option('-k', '--cache-key', dest="cache_key", help=f'cache key')

    parser.add_option('-a', '--allocation-portfolio-value', dest="portfolio_value", help=f'allocation portfolio value',
                      default=st.config["common"]["portfolio_value"], type="float")

    parser.add_option('-g', '--gamma', dest="gamma",
                      help=f'gamma L2 Regularisation. Adds a penalty (parameterised by gamma) on small weights',
                      default=0, type="float")

    parser.add_option('-w', '--min-value-per-instrument', dest="min_value",
                      help=f'min investment value per instrument in $ (None)',
                      default=None, type="float")

    parser.add_option('-s', '--invert-returns', dest="invert_returns",
                      help=f'invert returns (for short portfolios)', default=False)

    parser.add_option('-x', '--no-cache-calc', action="store_true", dest="no_cache_calculation",
                      help=f'no cache calculation', default=False)

    parser.add_option('-y', '--portfolio-min-allocation', dest="min_allocation",
                      help=f'min allocation for portfolio Discrete Allocation (0.01)',
                      default=0.01, type="float")

    parser.add_option('-z', '--allocation-cutoff', dest="allocation_cutoff",
                      help=f'allocation cutoff for Discrete Allocation',
                      default=1e-4, type="float")

    parser.add_option('-b', '--back-to-future-test', action="store_true", dest="back_to_future",
                      help=f'"back to future" test',
                      default=False)

    (options, args) = parser.parse_args()

    print(f'options:{options}')

    ret_val = process_options(options)

    print(f'response:\n{json.dumps(ret_val, indent=4, sort_keys=False)}')


def process_options(options):
    global back_to_future
    back_to_future = options.back_to_future

    if options.invert_returns:
        short_fix(options)
        ret_val = {"operation": "invert-returns", "filename": options.invert_returns}
    elif options.to_cache:
        mu, S, df = calculate_mu_S(options)
        latest_prices = get_latest_prices(df)
        cache_to_save = {'mu': mu, 'S': S, 'latest_prices': latest_prices, 'url': options.url}
        store_cache_func[options.to_cache](cache_to_save)
        ret_val = {"operation": "saved-to-cache", "hash": hash(str(cache_to_save))}
    elif options.reuse_cache:
        cache_loaded = load_cache_func[options.reuse_cache](options.cache_key)
        description = f'using cache {options.reuse_cache}, url {cache_loaded["url"]}'
        ret_val = calculate_all(cache_loaded['mu'], cache_loaded['S'], cache_loaded['latest_prices'], options,
                                description)
    elif options.no_cache_calculation:
        mu, S, df = calculate_mu_S(options)
        latest_prices = get_latest_prices(df)
        ret_val = calculate_all(mu, S, latest_prices, options, 'no cache')
    else:
        ret_val = {"error": "options do not match. Either use cache result, or reuse cache or -x to calculate all"}

    return ret_val


def short_fix(options):
    df = pd.read_csv(options.url)
    new_df = pd.DataFrame()
    new_df['date'] = df['date']
    for column in df:
        if column != 'date':
            new_df[column] = -df[column]

    new_df = new_df.set_index('date')
    new_df.to_csv(options.invert_returns)


def calculate_all(mu, S, latest_prices, options, description):
    back_to_future_total = 0
    calced = calculate_ef(mu, S, options)
    da = DiscreteAllocation(calced['weights'], latest_prices, total_portfolio_value=options.portfolio_value,
                            min_allocation=options.min_allocation)
    # allocation, leftover = da.greedy_portfolio()
    allocation, leftover = da.lp_portfolio()

    alloc_list = {}
    for key, val in allocation.items():
        if options.min_value is None or abs(val * latest_prices[key]) >= options.min_value:
            alloc_list[key] = {'symbol': key, 'quantity': val, 'price': latest_prices[key],
                               'total': round(val * latest_prices[key], 4)}
            if back_to_future:
                alloc_list[key]['back_to_future_return'] = (back_to_future_latest_prices[key] - latest_prices[key])*val
                back_to_future_total += alloc_list[key]['back_to_future_return']
    # print(f'alloc_list={alloc_list.values()}')
    fa = {"portfolio": list(alloc_list.values()), "remaining": "${:.2f}".format(leftover)}
    ret_val = {"operation": description, "efficient-frontier": calced, 'allocation': fa}
    if back_to_future:
        ret_val['back_to_future_total'] = back_to_future_total
        ret_val['back_to_future_percent'] = back_to_future_total/options.portfolio_value
    return ret_val


@deprecated(version='1.2.1', reason="You should use another function. All webapp.py should be migrated")
def eff_front(options):
    mu, S, df = calculate_mu_S(options)
    latest_prices = get_latest_prices(df)
    return calculate_ef(mu, S, options), latest_prices


def calculate_mu_S(options):
    now = datetime.now()
    # Read in price data
    df = pd.read_csv(options.url, parse_dates=True, index_col="date")
    if back_to_future:
        global back_to_future_latest_prices
        back_to_future_latest_prices = get_latest_prices(df)
        last_date = df.index[-1]
        df = df[df.index < last_date - relativedelta(years=1)]

    print(f'0. read_csv (with negation):    {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    # Calculate expected returns and sample covariance
    mu = expected_returns_calc_func[options.expected_returns_calc](df)
    print(f'1. expected_returns_calc_func:  {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    S = risk_models.sample_cov(df)
    print(f'2. risk_models.sample_cov(df):  {(datetime.now() - now).microseconds} microseconds')
    return mu, S, df


def calculate_ef(mu, S, options):
    now = datetime.now()
    ef = EfficientFrontier(mu, S, weight_bounds=(options.lower_weight_bound, options.higher_weight_bound))
    print(f'3. EfficientFrontier():         {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    calc_func = portfolio2return_func[options.portfolio2return][0]
    args = portfolio2return_func[options.portfolio2return][1](options)
    raw_weights = getattr(ef, calc_func)(**args)
    print(f'4. {calc_func}({args}):     {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    cleaned_weights = ef.clean_weights(cutoff=options.allocation_cutoff)
    cleaned_0weights = {key: val for key, val in cleaned_weights.items() if val != 0}

    cleaned_weights_sorted_list = sorted(cleaned_0weights.items(), key=lambda x: x[1], reverse=True)
    cleaned_weights_sorted_dict = dict(cleaned_weights_sorted_list)

    print(f'5. ef.clean_weights():          {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    (mu_, sigma, sharpe) = ef.portfolio_performance(verbose=False, risk_free_rate=options.risk_free)
    print(f'6. ef.portfolio_performance:    {(datetime.now() - now).microseconds} microseconds')
    ret_val = {'return': mu_, 'volatility': sigma, 'sharpe': sharpe, 'weights': cleaned_weights_sorted_dict}

    return ret_val


def eff_front_thread(options):
    def thread_func(options_, uid_):
        taskDict[uid_] = (False, '')         #not completed yet but started
        jsonStr = process_options(options_)
        taskDict[uid_] = (True, jsonStr)     #completed and result is there

    uid = uuid.uuid4()
    t = Thread(target=thread_func, args=(options, uid))
    t.start()
    return '{{"response":{{"uid":"{}","success":true}}}}'.format(str(uid))


def task_status(uid):
    task = taskDict.get(uuid.UUID(uid), None)
    return '{{"response":{{"taskexists":{}, "taskcompleted":{}}}}}'.\
        format(str(task is not None).lower(), str(task[0]).lower())


def task_result(uid):
    task = taskDict.get(uuid.UUID(uid), None)
    if task is None:
        return '{"response":{"taskexists":false, "taskcompleted":false}}'
    else:
        if task[0]:
            taskDict.pop(uuid.UUID(uid))
            return task[1]
        else:
            return '{"response":{"taskexists":true, "taskcompleted":false}}'


def tasks_list():
    uidsList = list(taskDict.keys())
    csvList = ",".join(map(str, uidsList))
    return '{{"response":{{"tasklist":"{}"}}}}'.format(csvList)


if __name__ == "__main__":
    main()
