import json

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import risk_models
from pypfopt import expected_returns
import pandas as pd
from datetime import datetime
import pickle
import redis


def get_portfolio(request):
    return process_options(json.loads(request.data))


taskDict = {}

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
    "sharpe": ("max_sharpe", lambda options: dict(risk_free_rate=options['risk_free'])),
    "return": ("efficient_return", lambda options: dict(target_return=options['target_return'],
                                                        market_neutral=options['market_neutral'])),
    "volatility": ("efficient_risk",
                   lambda options: dict(target_risk=options['target_volatility'], risk_free_rate=options['risk_free']))
}


def process_options(options):
    if options.get('to_cache', ''):
        mu, S, df = calculate_mu_S(options)
        latest_prices = get_latest_prices(df)
        cache_to_save = {'mu': mu, 'S': S, 'latest_prices': latest_prices, 'url': options.url}
        store_cache_func[options['to_cache']](cache_to_save)
        ret_val = {"operation": "saved-to-cache", "hash": hash(str(cache_to_save))}
    elif options.get('reuse_cache', ''):
        cache_loaded = load_cache_func[options['reuse_cache']](options['cache_key'])
        ret_val = calculate_all(cache_loaded['mu'], cache_loaded['S'], cache_loaded['latest_prices'],
                                options, f'using cache {options["reuse_cache"]}, url {options["url"]}')
    elif options.get('no_cache_calculation', ''):
        mu, S, df = calculate_mu_S(options)
        latest_prices = get_latest_prices(df)
        ret_val = calculate_all(mu, S, latest_prices, options, 'no cache')
    else:
        ret_val = {"error": "options do not match. Either use cache result, or reuse cache or -x to calculate all"}

    return ret_val


def calculate_all(mu, S, latest_prices, options, description):
    calced = calculate_ef(mu, S, options)
    da = DiscreteAllocation(calced['weights'], latest_prices, total_portfolio_value=options['portfolio_value'])
    allocation, leftover = da.lp_portfolio()

    alloc_list = {}
    for key, val in allocation.items():
        if val > 0:
            alloc_list[key] = {'symbol': key, 'volume': val, 'price': latest_prices[key],
                               'total': round(val * latest_prices[key], 2)}
    # print(f'alloc_list={alloc_list.values()}')
    fa = {"portfolio": list(alloc_list.values()), "remaining": "${:.2f}".format(leftover)}
    return {"operation": description, "efficient-frontier": calced, 'allocation': fa}


def calculate_mu_S(options):
    now = datetime.now()
    # Read in price data
    df = pd.read_csv(options['url'], parse_dates=True, index_col="date")
    print(f'0. read_csv:                    {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    # Calculate expected returns and sample covariance
    mu = expected_returns_calc_func[options['expected_returns_calc']](df)
    print(f'1. expected_returns_calc_func:  {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    S = risk_models.sample_cov(df)
    print(f'2. risk_models.sample_cov(df):  {(datetime.now() - now).microseconds} microseconds')
    return mu, S, df


def calculate_ef(mu, S, options):
    now = datetime.now()
    ef = EfficientFrontier(mu, S, weight_bounds=(options['lower_weight_bound'], options['higher_weight_bound']))
    print(f'3. EfficientFrontier():         {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    calc_func = portfolio2return_func[options['portfolio2return']][0]
    args = portfolio2return_func[options['portfolio2return']][1](options)
    raw_weights = getattr(ef, calc_func)(**args)
    print(f'4. {calc_func}({args}):     {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    cleaned_weights = ef.clean_weights(cutoff=options['allocation_cutoff'])
    cleaned_0weights = {key: val for key, val in cleaned_weights.items() if val != 0}

    cleaned_weights_sorted_list = sorted(cleaned_0weights.items(), key=lambda x: x[1], reverse=True)
    cleaned_weights_sorted_dict = dict(cleaned_weights_sorted_list)

    print(f'5. ef.clean_weights():          {(datetime.now() - now).microseconds} microseconds')
    now = datetime.now()
    (mu_, sigma, sharpe) = ef.portfolio_performance(verbose=False, risk_free_rate=options['risk_free'])
    print(f'6. ef.portfolio_performance:    {(datetime.now() - now).microseconds} microseconds')
    ret_val = {'return': mu_, 'volatility': sigma, 'sharpe': sharpe, 'weights': cleaned_weights_sorted_dict}

    return ret_val
