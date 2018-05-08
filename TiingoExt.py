import requests
from pandas_datareader.tiingo import TiingoDailyReader, TiingoQuoteReader


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
        print 'headers={}'.format(headers)
        except_to_throw = None
        for i in range(self.retry_count):
            try:
                out = self._get_response(url, params=params, headers=headers).json()
                return self._read_lines(out)
            except  requests.exceptions.ConnectionError, e:
                print 'Exception {}'.format(e)
                except_to_throw = e
                pass

        raise except_to_throw
