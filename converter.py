import pandas as pd
import sys
import urllib2
import requests
import io
import ssl
import csv

column_names = ['Symbol', 'Date', 'Price', 'Open', 'High', 'Low', 'Vol']

class FormatConverter():
    base_url = 'https://www.marketindex.com.au/sites/default/files/historical-data/{}.csv'

    """
    converts file "upload" format into "upload1"
    Useful for files downloaded in one format to be processed with the  latest systems.
    """
    def __init__(self, start_date, file_name = 'data.csv'):
        self.start_date = start_date
        self.column_names = column_names
        self.file_name = file_name

    def read(self):
        # df_orig = pd.read_csv(self.file_name, delimiter=';', quoting=csv.QUOTE_NONE, parse_dates = [1])
        df_orig = pd.read_csv(self.file_name, delimiter=';')#, parse_dates = [1])
        df_orig.columns = column_names
        df_result = df_orig[['Symbol', 'Date', 'Price']]
        df_result.columns = ['symbol', 'date', 'close']
        df_result.to_csv('downloads/df_converter.csv')
        # print 'df_result.dtypes={}'.format(df_result.dtypes)
        # reversed = df_result.reindex(index=df_result.index[::-1])
        # reversed.to_csv('downloads/df_converter_reversed.csv')
        # sys.exit()
        return df_result
