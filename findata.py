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
import numpy as np


class FinDownloader():
    """
    Historical daily data downloader
    """

    def __init__(self, source, retry_count=3, pause=0.1,
                 timeout=30):
        self.source = source
        self.retry_count = retry_count
        self.pause = pause
        self.timeout = timeout
        self.datasource = st.config['downloader']['datasource']
        self.symbolColumn = st.config['downloader']['symbolColumn']
        self.dateColumn = st.config['downloader']['dateColumn']
        self.priceColumn = st.config['downloader']['priceColumn']
        self.directory = st.config['downloader']['directory']
        self.access_key = st.config['downloader']['access_key']
        self.inputfilename = st.config['downloader']['inputfilename']

    def downloadInstruments(self, symbols, start_date, final_date):

        millis = int(round(time.time() * 1000))
        downloadFileName = '{}.csv'.format(str(millis))

        symbolsArray = symbols.split(',')
        print 'datasource ={}'.format(self.datasource)
        print 'symbolName ={}'.format(self.symbolColumn)
        print 'dateColumn ={}'.format(self.dateColumn)
        print 'priceColumn={}'.format(self.priceColumn)
        print 'symbols.split={}'.format(symbolsArray)
        print 'source={}, start_date={}, final_date={}, downloadFileName={}'.format(self.datasource, start_date,
                                                                                    final_date,
                                                                                    downloadFileName)

        session = requests.session()
        session.headers = requests.utils.default_headers()
        session.headers[
            'Accept'] = 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        session.headers['Accept-Encoding'] = 'gzip, deflate, br'
        session.headers['Accept-Language'] = 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7'
        session.headers['Cache-Control'] = 'max-age=0'
        session.headers['Connection'] = 'keep-alive'
        session.headers['Upgrade-Insecure-Requests'] = '1'
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
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
            "converter": cv.FormatConverter(start_date, self.inputfilename)
            # "tiingo": TiingoExt.TiingoExt(symbolsArray, start_date, final_date, api_key=self.access_key,
            #                                               retry_count=10, pause=0.3, extheaders=session.headers),
            # "quandl": qr.Quandl(symbolsArray, start_date, final_date, api_key=self.access_key,
            #                      retry_count=10, pause=0.3, extheaders=session.headers)
        }

        # allColumnsOrigDf = TiingoExt.TiingoExt(symbolsArray, start_date, final_date, api_key=access_key,
        #                                        retry_count=10, pause=0.3, extheaders=session.headers).read()
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
        newDf = self.pivot(dataDf, start_date, final_date)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        earliest_date = start_date + dt.timedelta(days=7)
        newDf = newDf[newDf.index >= earliest_date]
        newDf.to_csv('downloads/reduced.csv')
        existing_earliest_date = newDf.index.min()
        # existing_earliest_date = newDf.loc(newDf.index >= earliest_date).index.min()
        print 'earliest_date = {}, existing_earliest_date = {}'.format(earliest_date, existing_earliest_date)
        cols_to_exclude = newDf.loc[:existing_earliest_date].isnull().all()
        cols_to_keep = ~cols_to_exclude
        print 'Earliest date to compare: {}'.format(str(existing_earliest_date))
        print 'Columns to keep: {}'.format(str(cols_to_keep))
        print 'Columns excluded: {}'.format(str(cols_to_exclude))
        newDf = newDf.loc[:, cols_to_keep]
        newDf.to_csv(self.directory + '/before_dropna_' + downloadFileName)
        newDf.dropna(axis=0, inplace=True)
        newDf.dropna(axis=1, inplace=True)
        newDf.to_csv(self.directory + '/' + downloadFileName)
        print 'download instruments done'
        return self.directory + '/' + downloadFileName


    def pivot(self, dataDf, start_date, final_date):
        symbolsArray = dataDf[self.symbolColumn].unique()
        # print 'symbols in data: {}'.format(symbolsArray)
        df_list=[]
        dfRet = pd.DataFrame()
        for i, sym in enumerate(symbolsArray):
            newSymData = dataDf.loc[dataDf[self.symbolColumn] == sym][[self.dateColumn, self.priceColumn]]
            earliest_date = pd.to_datetime(newSymData[self.dateColumn]).min()
            if start_date >= earliest_date:
                print '{}.\tAdding sym=\'{}\': required {:%Y-%m-%d} >= earliest {:%Y-%m-%d}' \
                    .format(i, sym, start_date, earliest_date)
                # dataDf.to_csv('downloads/newSymData.csv')
                newSymData[self.dateColumn] = pd.to_datetime(newSymData[self.dateColumn])
                # newSymData[self.priceColumn] = newSymData[self.priceColumn].astype(np.float64)
                newSymData = newSymData.set_index(self.dateColumn)
                newSymData = newSymData[pd.to_datetime(newSymData.index) >= start_date]
                newSymData.dropna(axis=(0, 1), inplace=True)
                newSymData.drop_duplicates(inplace=True)
                if newSymData.empty:
                    print '\t\tSkipped as empty'
                elif len(newSymData.index) < 200:
                    print '\t\tSkipped as too short'
                elif final_date - dt.timedelta(days=7) >= newSymData.index.max():
                    print '\t\tSkipped as latest date {} is too far back'.format(newSymData.index.max())
                else:
                    newSymData.index.names = [self.dateColumn]
                    newSymData.columns = [sym]
                    newSymData.sort_index(inplace=True)
                    newSymData.to_csv('downloads/{}.csv'.format(sym))
                    df_list.append(newSymData)
            else:
                print '{}.\tSkipped. sym=\'{}\': required {:%Y-%m-%d} < earliest {:%Y-%m-%d}' \
                    .format(i, sym, start_date, earliest_date)

        dfRet = pd.concat(df_list, axis=1, join='outer')
        dfRet.to_csv('downloads/df_before_dropna_tresh.csv')
        # dfRet.replace('', np.nan, inplace=True)
        thresh = len(dfRet) * .2
        dfRet = dfRet.dropna(thresh=thresh, axis=1)
        dfRet.to_csv('downloads/df_after_dropna_tresh.csv')
        dfRet.fillna(method='bfill', inplace=True)
        dfRet.sort_index(inplace=True)
        dfRet.index.names = ['date']
        dfRet.to_csv('downloads/df_ret.csv')
        return dfRet
