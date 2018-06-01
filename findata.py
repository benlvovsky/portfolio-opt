import datetime as dt
import time
import dx
import seaborn as sns;
import copy
import settings as st
import meanvarianceportfolio as mvp
import pandas as pd
# from pandas_datareader import data as web
import pandas_datareader.data as web
import os
from threading import Thread
import uuid
import TiingoExt
import requests
import quandlreader as qr
import marketdata as md
import converter as cv

class FinDownloader():
    """
    Historical daily data downloader
    """
    def __init__(self, source, retry_count=3, pause=0.1,
                 timeout=30):
        self.source         = source
        self.retry_count    = retry_count
        self.pause          = pause
        self.timeout        = timeout
        self.datasource     = st.config['downloader']['datasource']
        self.symbolColumn   = st.config['downloader']['symbolColumn']
        self.dateColumn     = st.config['downloader']['dateColumn']
        self.priceColumn    = st.config['downloader']['priceColumn']
        self.directory      = st.config['downloader']['directory']
        self.access_key     = st.config['downloader']['access_key']
        self.inputfilename  = st.config['downloader']['inputfilename']

    def downloadInstruments(self, symbols, start_date, final_date):

        millis = int(round(time.time() * 1000))
        downloadFileName = '{}.csv'.format(str(millis))

        symbolsArray= symbols.split(',')
        print 'datasource ={}'.format(self.datasource)
        print 'symbolName ={}'.format(self.symbolColumn)
        print 'dateColumn ={}'.format(self.dateColumn)
        print 'priceColumn={}'.format(self.priceColumn)
        print 'symbols.split={}'.format(symbolsArray)
        print 'source={}, start_date={}, final_date={}, downloadFileName={}'.format(self.datasource, start_date, final_date,
                                                                                    downloadFileName)

        session = requests.session()
        session.headers = requests.utils.default_headers()
        session.headers['Accept'] = 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        session.headers['Accept-Encoding'] = 'gzip, deflate, br'
        session.headers['Accept-Language'] = 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7'
        session.headers['Cache-Control'] = 'max-age=0'
        session.headers['Connection'] = 'keep-alive'
        session.headers['Upgrade-Insecure-Requests'] = '1'
        session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
        session.headers['Content-Type'] = 'application/json'
        session.headers['Authorization'] = 'Token {}'.format(self.access_key)
        print 'using headers v.6'
        # url = "https://api.tiingo.com/tiingo/daily/{}/prices?startDate=2012-1-1&endDate=2016-1-1&token={}".\
        #     format(symbolsArray[0], access_key)
        # print 'url={}'.format(url)
        # # readJsonDf = pd.read_json("https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate=2012-1-1&endDate=2016-1-1&token={}", symbolsArray[0], access_key)
        # # requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/googl/prices?startDate=2012-1-1&endDate=2016-1-1", headers=session.headers)
        # requestResponse = requests.get(url, headers=session.headers)
        # readJsonDf = pd.read_json(requestResponse.json())
        # print requestResponse.json()
        # readJsonDf.to_csv(directory + '/readJsonDf.csv')
        # return

        # allColumnsOrigDf = web.DataReader(symbolsArray, datasource, start_date, final_date, access_key=access_key,
        #                                   session=session, retry_count=10, pause=0.3)

        downloaders = {
            "marketdata": md.MarketData(symbolsArray, start_date, final_date, session=session),
            "converter": cv.FormatConverter(self.inputfilename)
            # "tiingo": TiingoExt.TiingoExt(symbolsArray, start_date, final_date, api_key=self.access_key,
            #                                               retry_count=10, pause=0.3, extheaders=session.headers),
            # "quandl": qr.Quandl(symbolsArray, start_date, final_date, api_key=self.access_key,
            #                      retry_count=10, pause=0.3, extheaders=session.headers)
        }

        # allColumnsOrigDf = TiingoExt.TiingoExt(symbolsArray, start_date, final_date, api_key=access_key,
        #                                        retry_count=10, pause=0.3, extheaders=session.headers).read()
        print downloaders
        allColumnsOrigDf = downloaders[self.source].read()
        allColumnsNoIndexDf = allColumnsOrigDf.reset_index()

        print 'Columns list from DataReader: {}'.format(allColumnsNoIndexDf.columns.values)
        print 'Index from DataReader: {}'.format(allColumnsNoIndexDf.index)
        if self.priceColumn in allColumnsNoIndexDf:
            dataDf = allColumnsNoIndexDf[[self.symbolColumn, self.dateColumn, self.priceColumn]]
        else:
            print 'Column {} doesn''t exist. Using [''Symbol'', ''Date'', ''Close'']'.format(self.priceColumn)
            dataDf = allColumnsNoIndexDf[['Symbol', 'Date', 'Close']]
        # dataDf.to_csv(downloadDir + '/downloadedInstrumentsOnlyOnePriceColRaw.csv')
        newDf = self.pivot(dataDf)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # allColumnsNoIndexDf.to_csv(downloadDir + '/downloadedInstrumentsNoIndexAllCols.csv')
        earliest_date = start_date + dt.timedelta(days=7)
        cols_to_exclude =  newDf.loc[:earliest_date].isnull().all()
        cols_to_keep    = ~cols_to_exclude
        print 'Earliest date to compare: {}'.format(str(earliest_date))
        print 'Columns to keep: {}'.format(str(cols_to_keep))
        print 'Columns excluded: {}'.format(str(cols_to_exclude))
        newDf = newDf.loc[:, cols_to_keep]
        newDf.dropna(axis=1, inplace=True)

        newDf.to_csv(self.directory + '/' + downloadFileName)
        print 'download instruments done'
        return self.directory + '/' + downloadFileName

    def pivot(self, dataDf):
        symbolsArray = dataDf[self.symbolColumn].unique()
        print 'symbols in data: {}'.format(symbolsArray)
        dfRet = pd.DataFrame()
        for i, sym in enumerate(symbolsArray):
            newSymData = dataDf.loc[dataDf[self.symbolColumn] == sym][[self.dateColumn, self.priceColumn]]
            earliest_date = pd.to_datetime(newSymData['date']).min()
            print 'sym={}, earliest date={}'.format(sym, earliest_date)
            # dataDf.to_csv('downloads/newSymData.csv')
            newSymData.columns = [self.dateColumn, sym]
            if i < 1:
                dfRet = newSymData.copy()
            else:
                dfRet = pd.merge(dfRet, newSymData, on=self.dateColumn, how='outer')

        reversed = dfRet.set_index(self.dateColumn)
        reversed.index.names = ['date']
        # reversed = reversed.reindex(index=reversed.index[::-1])
        data = reversed
        data.columns = symbolsArray
        return data
