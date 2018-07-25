import pandas_datareader as pdr
from pandas_datareader.tiingo import TiingoDailyReader, TiingoQuoteReader
import requests

class TiingoExt(TiingoDailyReader):
    """
    Historical daily data from Tiingo on equities, ETFs and mutual funds
    """
    def __init__(self, symbols, start=None, end=None, retry_count=3, pause=0.1,
                 timeout=30, session=None, freq=None, api_key=None, extheaders={}):
        super(TiingoExt, self).__init__(symbols, start=start, end=end, retry_count=retry_count,
                                        pause=pause, timeout=timeout, session=session, freq=freq, api_key=api_key)
        self.extheaders = extheaders

    def _read_one_data(self, url, params):
        """ read one data from specified URL """
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Token ' + self.api_key}
        headers.update(self.extheaders)
        # print 'headers={}'.format(headers)
        print 'url={}'.format(url)
        except_to_throw = None
        for i in range(self.retry_count):
            try:
                out = self._get_response(url, params=params, headers=headers).json()
                return self._read_lines(out)
            except  requests.exceptions.ConnectionError, e:
                print 'Exception {}'.format(e)
                except_to_throw = e

        print 'Symbol {} skipped due to exception: {}'.format(except_to_throw)
        return None

    # raise except_to_throw

    def read(self):
        df_orig = super(TiingoExt, self).read()
        df_orig = df_orig.reset_index()
        df_orig.to_csv('downloads/df_orig_tiingo.csv')
        column_names = ['symbol','date','adjClose','adjHigh','adjLow','adjOpen','adjVolume','close','divCash','high','low','open','splitFactor','volume']
        df_orig.columns = column_names
        df_result = df_orig[['symbol', 'date', 'adjClose']]
        df_result.columns = ['symbol', 'date', 'close']
        df_result.to_csv('downloads/df_tiingo_converted.csv')
        return df_result

class TiingoPandas:
    """
    Historical daily data from Tiingo
    """
    def __init__(self, symbols, start=None, end=None, retry_count=3, pause=0.1,
                 timeout=30, session=None, freq=None, api_key=None, extheaders={}):
        self.symbols = symbols
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
        df_orig = pdr.get_data_tiingo(self.symbols, api_key=self.api_key)
        df_orig.to_csv('downloads/df_orig_tiingo.csv')
        exit(0)
        column_names = ['Symbol', 'Date', 'Price', 'Open', 'High', 'Low', 'Vol']
        df_orig.columns = column_names
        df_result = df_orig[['Symbol', 'Date', 'Price']]
        df_result.columns = ['symbol', 'date', 'close']
        df_result.to_csv('downloads/df_converter.csv')
        return df_result
        return df
