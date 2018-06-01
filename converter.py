import pandas as pd
import sys
import urllib2
import requests
import io
import ssl

column_names = ['Symbol', 'Date', 'Price', 'Open', 'High', 'Low', 'Vol']

class FormatConverter():
    base_url = 'https://www.marketindex.com.au/sites/default/files/historical-data/{}.csv'

    """
    converts file "upload" format into "upload1"
    Useful for files downloaded in one format to be processed with the  latest systems.
    """
    def __init__(self, file_name = 'data.csv'):
        self.column_names = column_names
        self.file_name = file_name
        # self.symbols_array = ""
        # self.start=start
        # self.end=end
        # self.retry_count=retry_count
        # self.pause=pause
        # self.timeout=timeout
        # self.session=session
        # self.freq=freq
        # self.api_key=api_key
        # self.extheaders = extheaders

    def read(self):
        df_orig = pd.read_csv(self.file_name, delimiter=';')
        df_orig.columns = column_names
        df_result = df_orig[['Symbol', 'Date', 'Price']]
        df_result.columns = ['symbol', 'date', 'close']
        df_result.to_csv('downloads/df_converter.csv')
        # sys.exit()
        return df_result
