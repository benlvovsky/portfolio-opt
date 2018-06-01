import pandas as pd
import sys
import urllib2
import requests
import io
import ssl

class MarketData():
    base_url = 'https://www.marketindex.com.au/sites/default/files/historical-data/{}.csv'

    """
    Historical daily data from marketdata
    https://www.marketindex.com.au/sites/default/files/historical-data/CBA.csv
    """
    def __init__(self, symbols_array, start=None, end=None, retry_count=3, pause=0.1,
                 timeout=30, session=None, freq=None, api_key=None, extheaders={}):
        self.symbols_array = symbols_array
        self.start=start
        self.end=end
        self.retry_count=retry_count
        self.pause=pause
        self.timeout=timeout
        self.session=session
        self.freq=freq
        self.api_key=api_key
        self.extheaders = extheaders

    def read(self):
        dfs = []
        for symbol in self.symbols_array:
            effective_url = self.base_url.format(symbol)
            print 'symbol={}, effective_url={}'.format(symbol, effective_url)
            headers = requests.utils.default_headers()
            session = requests.Session()
            # print requests.get(effective_url, timeout=None, verify=True).content #, proxies = {'http': "172.18.0.3:3128", 'https': "172.18.0.3:3128"}).content
            s = session.get(effective_url, headers=headers, timeout=100) #, proxies = {'https': "socks5h://127.0.0.1:3128"}).content
            print s
            c=pd.read_csv(io.StringIO(s.decode('utf-8')))
            # response = urllib2.urlopen(effective_url)
            # csv = response.read()
            df = pd.read_csv(c)
            df.to_csv('downloads/marketDataDf.csv')
            sys.exit()
