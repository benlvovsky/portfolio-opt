#!/usr/bin/env python

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import pandas as pd
import settings as st
from threading import Thread
import uuid
import json
from optparse import OptionParser
from datetime import datetime, timedelta
import pickle
from collections import OrderedDict

taskDict = {}


def main():
    parser = OptionParser()

    parser.add_option('-e', '--expected_returns_calc', dest="expected_returns_calc", type="choice",
                      help="calculation type of historical return", choices=['mean', 'exp'], default="mean")

    parser.add_option('-p', '--portfolio_to_return', dest="portfolio2return", type="choice",
                      help="what portfolio to calculate", default="sharpe",
                      choices=['sharpe', 'return', 'volatility'])

    parser.add_option('-f', '--risk_free', dest="risk_free",
                      help=f'risk free ({st.config["efficient_frontier"]["default_riskfree"]})',
                      default=st.config["efficient_frontier"]["default_riskfree"])

    parser.add_option('-r', '--target_return', dest="target_return",
                      help="target_return for minimal volatility calculation",
                      default=None, type="float")

    parser.add_option('-v', '--target_volatility', dest="target_volatility",
                      help="target_volatility for max return",
                      default=None, type="float")

    parser.add_option('-l', '--lower_weight_bound', dest="lower_weight_bound",
                      help="lower weight bound (0)", default=0, type="float")

    parser.add_option('-i', '--higher_weight_bound', dest="higher_weight_bound",
                      help="higher weight bound (1)", default=1, type="float")

    parser.add_option('-n', '--market_neutral', dest="market_neutral",
                      help="market neutral (False)",
                      default=False)

    parser.add_option('-u', '--url', dest="url",
                      help=f'url ({st.config["common"]["upload_url"]})',
                      default=st.config["common"]["upload_url"])

    parser.add_option('-c', '--cache-ef', dest="to_cache",
                      help=f'calculate and cache efficient object only for later use into the parameter filename')

    parser.add_option('-o', '--load-ef', dest="reuse_cache",
                      help=f'reuse cached ef object from the parameter filename')

    (options, args) = parser.parse_args()

    print(f'options:{options}')

    if options.to_cache:
        mu, S = calculate_mu_S(options)
        pickle.dump({'mu': mu, 'S': S}, open(f'{options.to_cache}.ser', "wb"))
        ret_val = "serialised and saved"
    elif options.reuse_cache:
        d = pickle.load(open(f'{options.reuse_cache}.ser', "rb"))
        ret_val = calculate_ef(d['mu'], d['S'], options)
    else:
        ret_val = eff_front(options)

    print(f'eff_front:\n{json.dumps(ret_val, indent=4, sort_keys=True)}')


expected_returns_calc_func = {
    "mean": expected_returns.mean_historical_return,
    "exp": expected_returns.ema_historical_return
}


portfolio2return_func = {
    "sharpe": ("max_sharpe", lambda options: dict(risk_free_rate=options.risk_free)),
    "return": ("efficient_return", lambda options: dict(target_return=options.target_return,
                                                        market_neutral=options.market_neutral)),
    "volatility": ("efficient_risk",
                   lambda options: dict(target_risk=options.target_volatility, risk_free_rate=options.risk_free))
}


def eff_front(options):
    mu, S = calculate_mu_S(options)
    return calculate_ef(mu, S, options)


def calculate_ef(mu, S, options):
    # Optimise for maximal Sharpe ratio
    now = datetime.now()
    ef = EfficientFrontier(mu, S, weight_bounds=(options.lower_weight_bound, options.higher_weight_bound))
    print(f'3. EfficientFrontier():         {(datetime.now() - now).microseconds}')
    now = datetime.now()
    calc_func = portfolio2return_func[options.portfolio2return][0]
    args = portfolio2return_func[options.portfolio2return][1](options)
    raw_weights = getattr(ef, calc_func)(**args)
    print(f'4. {calc_func}({args}):     {(datetime.now() - now).microseconds}')
    now = datetime.now()
    cleaned_weights = ef.clean_weights()
    cleaned_0weights = {key: val for key, val in cleaned_weights.items() if val != 0}

    cleaned_weights_sorted_list = sorted(cleaned_0weights.items(), key=lambda x: x[1], reverse=True)
    print(f'type(cleaned_weights_sorted) = {type(cleaned_weights_sorted_list)}')
    print(f'{cleaned_weights_sorted_list}')

    print(f'5. ef.clean_weights():          {(datetime.now() - now).microseconds}')
    now = datetime.now()
    (mu_, sigma, sharpe) = ef.portfolio_performance(verbose=False, risk_free_rate=options.risk_free)
    print(f'6. ef.portfolio_performance:    {(datetime.now() - now).microseconds}')
    ret_val = {'return': mu_, 'volatility': sigma, 'sharpe': sharpe, 'weights': cleaned_weights_sorted_list}
    return ret_val


def calculate_mu_S(options):
    now = datetime.now()
    # Read in price data
    df = pd.read_csv(options.url, parse_dates=True, index_col="date")
    print(f'0. read_csv:                    {(datetime.now() - now).microseconds}')
    now = datetime.now()
    # Calculate expected returns and sample covariance
    mu = expected_returns_calc_func[options.expected_returns_calc](df)
    print(f'1. expected_returns_calc_func:  {(datetime.now() - now).microseconds}')
    now = datetime.now()
    S = risk_models.sample_cov(df)
    print(f'2. risk_models.sample_cov(df):  {(datetime.now() - now).microseconds}')
    return mu, S


def eff_front_thread(options):
    def thread_func(options_, uid_):
        taskDict[uid_] = (False, '')         #not completed yet but started
        jsonStr = eff_front(options_)
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
