import pandas as pd
import sys
import urllib2
import requests
import io
import ssl
import csv

column_names = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']

class FormatConverter():
    """
    converts file "upload" format into "upload1"
    Useful for files downloaded in one format to be processed with the  latest systems.
    """
    def __init__(self, start_date, file_name = 'data.csv'):
        self.start_date = start_date
        self.column_names = column_names
        self.file_name = file_name

    def read(self):
        df_orig = pd.read_csv(self.file_name, delimiter=',')
        df_orig.columns = column_names
        df_result = df_orig[['Ticker', 'Date', 'Close']]
        df_result.columns = ['symbol', 'date', 'close']
        df_result.to_csv('downloads/df_converter.csv')
        return df_result
