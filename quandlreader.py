import sys
import quandl

class Quandl():
    """
    Historical daily data from Quandle
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
        quandl.ApiConfig.api_key = api_key
        self.extheaders = extheaders

    def read(self):
        # print quandl.get('ASX/IBV2019', start_date='2018-05-16', end_date='2018-05-16')
        print '-----------------------------'
        print quandl.get('ASX/IBV2019', start_date=self.start, end_date=self.end)
        sys.exit()
