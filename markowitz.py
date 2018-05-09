#!/usr/bin/env python

import traceback
import matplotlib
import requests
matplotlib.use('Agg')
#matplotlib.use('qt5agg')
#matplotlib.use('qt4agg')
#import PyQt4
# import matplotlib.pyplot as plt
# import json
# from dx import *
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
# from scipy import interpolate
# import sympy

sns.set()

taskDict = {}

asxTop20 = ['CBA.AX','WBC.AX','BHP.AX','ANZ.AX','NAB.AX','CSL.AX','WES.AX','TLS.AX','WOW.AX',\
            'MQG.AX','RIO.AX','TCL.AX','WPL.AX','SCG.AX',\
#             'SUN.AX',\
            'WFD.AX','IAG.AX','AMP.AX','BXB.AX','QBE.AX']
original = ['AAPL', 'GOOG', 'MSFT', 'FB']
globalTop100Str = 'DDD,MMM,WBAI,WUBA,EGHT,AHC,AIR,AAN,ABB,ABT,ABBV,ANF,GCH,ACP,JEQ,SGF,ABM,AKR,ACN,ACCO,ATV,ATU,AYI,ADX,PEO,AGRO,ATGE,AAP,WMS,ASX,AAV,AVK,AGC,LCM,ACM,ANW,AED,AEG,AEH,AER,AJRD,AET,AMG,AFL,MITT,AGCO,A,AEM,ADC,AGU,AL,APD,AYR,AKS,ALG,AGI,ALK,AIN,ALB,AA,ALEX,ALX,ARE,AQN,Y,ATI,ALLE,AGN,ALE,AKP,ADS,AFB,AOI,AWF,AB,LNT,CBH,NCV,NCZ,ACV,NIE,NFJ,ALSN,ALL'
globalTop200Str = 'AAPL,GOOGL,GOOG,MSFT,AMZN,FB,INTC,CSCO,CMCSA,PEP,AMGN,NVDA,TXN,AVGO,GILD,QCOM,KHC,PYPL,PCLN,ADBE,NFLX,CHTR,CELG,COST,SBUX,WBA,BIIB,BIDU,FOX,AABA,MDLZ,QQQ,AMAT,AMOV,TSLA,TMUS,MU,ADP,CSX,CME,MAR,ATVI,FOXA,ISRG,ESRX,REGN,CTSH,EBAY,INTU,JD,NXPI,VRTX,MNST,EQIX,EA,ADI,ILMN,LRCX,ROST,LBTYA,LBTYB,AMTD,LBTYK,ALXN,FISV,PCAR,NTES,DLTR,TROW,AAL,PAYX,WDC,IBKR,XEL,ADSK,SIRI,MYL,DISH,CERN,NTRS,WDAY,HBANO,VCSH,ORLY,FITB,MCHP,CTRP,INCY,PFG,WLTW,SBAC,EXPE,VCIT,ALGN,SWKS,INFO,DVY,SYMC,PFF,CHKP,XLNX,CTAS,KLAC,WYNN,LBRDK,LBRDA,BMRN,HBAN,VRSK,FAST,XRAY,NTAP,MXIM,ULTA,VOD,MELI,IDXX,CA,CBOE,VIA,ETFC,CTXS,ALNY,LSXMK,TTWO,SNPS,NDAQ,ASML,ANSS,LKQ,JBHT,FANG,NCLH,IPGP,SIVB,CHRW,SPLK,STX,EMB,CDNS,HOLX,CINF,MBB,SHPG,TEAM,ACGL,EXPD,CSJ,HAS,SEIC,MRVL,HSIC,GRMN,SHY,SNI,AKAM,AMD,YNDX,CSGP,ODFL,CGNX,CDW,VRSN,IAC,QVCA,RYAAY,STLD,SCZ,LULU,TRMB,VXUS,QVCB,VIAB,IBB,ZION,CPRT,NWS,FLEX,CDK,ON,NWSA,DOX,TSCO,EXEL,IEP,OTEX,DISCB,NKTR,AGNCB,JKHY,ACWI,EWBC,CZR,MTCH,QRVO,ABMD,NDSN,ALKS,DISCA,IXUS,OLED,SSNC,FFIV,JAZZ,BLUE,SGEN,DISCK,Z,ZG,BNDX,CG,SHV,FWONK,GT,SINA,FTNT,GLPI,IEF,SBNY,CIU,AGNC,MIDD,MKTX,PPC,WB,UHAL,COHR,HDS,NBIX,FSLR,COMM,QGEN'
asxTop20StrYahoo = 'CBA.AX,WBC.AX,BHP.AX,ANZ.AX,NAB.AX,CSL.AX,WES.AX,TLS.AX,WOW.AX,MQG.AX,RIO.AX,TCL.AX,WPL.AX,SCG.AX,WFD.AX,IAG.AX,AMP.AX,BXB.AX,QBE.AX'
asxTop20StrGoogle = 'ASX:CBA,ASX:WBC,ASX:BHP,ASX:ANZ,ASX:NAB,ASX:CSL,ASX:WES,ASX:TLS,ASX:WOW,ASX:MQG,ASX:RIO,ASX:TCL,ASX:WPL,ASX:SCG,ASX:WFD,ASX:IAG,ASX:AMP,ASX:BXB,ASX:QBE'
smallGlobalStr = 'AAPL,GOOGL,GOOG'

def main():
    # sharpeAndCml('upload', 0.03, "")
    start = dt.datetime(2008, 1, 1) #yyyy,mm,dd
    end = dt.datetime(2018, 04, 30)
    print 'will run downloadInstruments'
    # downloadInstruments('yahoo', asxTop20Str, start, end, 'dataAllcolsTop200.csv')
    # downloadInstruments('morningstar', 'AAPL,GOOGL', 'Close', start, end, 'dataAllcolsTop200.csv')
    downloadInstruments(smallGlobalStr, start, end)


def getEfficientFrontierPortfolios(port, evols):
    portfolios = list()
    for v in evols:
        port.optimize('Return', constraint=v, constraint_type='Exact')
        portfolios.append(copy.copy(port))

    return portfolios


def findSource(source):
    if 'upload_type' in st.config["common"]:
        uploadType = st.config["common"]["upload_type"]
    else:
        uploadType = ''

    print 'upload_type = "{}"'.format(uploadType)

    if source == 'upload' and uploadType != 'allcolumns':
        retVal = 'upload'
    elif source == 'upload' and uploadType == 'allcolumns':
        retVal = 'upload1'
    else:
        retVal = source

    return retVal

def sharpeAndCml(source, riskFree, symbols):
    ma = dx.market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', symbols)
    ma.add_constant('source', findSource(source))
    # ma.add_constant('final date', dt.date(2014, 3, 1))
    ma.add_constant('final date', dt.datetime.now())

    retVal = '{\n'
    retVal += '"EfficientPortfolios":'
    try:
        port = mvp.MeanVariancePortfolio(source + '_stocks', ma)
        effFrontier = port.get_efficient_frontier_bl(st.config["efficient_frontier"]["points_number"])

        retVal += effFrontier.toJson()
        retVal += ',\n'

        try:
            cpl = port.get_capital_market_line_bl_1(effFrontier.vols, effFrontier.rets, riskless_asset=riskFree)
            retVal += '"CML":' + cpl.toJson()
        except Exception, e:
            retVal += '"CML": {{"error":"{}"}}'.format(str(e))
            traceback.print_exc()

    except Exception, e:
        retVal += '{{"error":"{}"}}'.format(str(e))
        traceback.print_exc()

    retVal += "\n}"

    print retVal
    return retVal


def sharpeAndCmlAsync(sourceName, riskFree, placeHolderOnly):
    uid = uuid.uuid4()
    t = Thread(target=threadFunc, args=(sourceName, riskFree, uid))
    t.start()
    return '{{"response":{{"uid":"{}","success":true}}}}'.format(str(uid))


def threadFunc(sourceName, riskFree, uid):
    taskDict[uid] = (False, '') #not completed yet but started
    jsonStr = sharpeAndCml(sourceName, riskFree, [])
    taskDict[uid] = (True, jsonStr) #completed and result is there


def getAsyncTaskStatus(uid):
    task = taskDict.get(uuid.UUID(uid), None)
    return '{{"response":{{"taskexists":{}, "taskcompleted":{}}}}}'.\
        format(str(task is not None).lower(), str(task[0]).lower())


def getAsyncTaskResult(uid):
    task = taskDict.get(uuid.UUID(uid), None)
    if task is None:
        return '{"response":{"taskexists":false, "taskcompleted":false}}'
    else:
        if task[0]:
            taskDict.pop(uuid.UUID(uid))
            return task[1]
        else:
            return '{"response":{"taskexists":true, "taskcompleted":false}}'


def getListAsyncTasks():
    uidsList = taskDict.keys()
    csvList = ",".join(map(str, uidsList))
    return '{{"response":{{"tasklist":"{}"}}}}'.format(csvList)


def downloadInstruments(symbols, start_date, final_date):
    millis = int(round(time.time() * 1000))
    downloadFileName = '{}.csv'.format(str(millis))

    datasource  = st.config['downloader']['datasource']
    symbolColumn= st.config['downloader']['symbolColumn']
    dateColumn  = st.config['downloader']['dateColumn']
    priceColumn = st.config['downloader']['priceColumn']
    directory   = st.config['downloader']['directory']
    access_key  = st.config['downloader']['access_key']

    symbolsArray= symbols.split(',')
    print 'datasource ={}'.format(datasource)
    print 'symbolName ={}'.format(symbolColumn)
    print 'dateColumn ={}'.format(dateColumn)
    print 'priceColumn={}'.format(priceColumn)
    print 'symbols.split={}'.format(symbolsArray)
    print 'source={}, start_date={}, final_date={}, downloadFileName={}'.format(datasource, start_date, final_date,
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
    session.headers['Authorization'] = 'Token {}'.format(access_key)
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
    allColumnsOrigDf = TiingoExt.TiingoExt(symbolsArray, start_date, final_date, api_key=access_key,
                                           retry_count=10, pause=0.3, extheaders=session.headers).read()
    allColumnsNoIndexDf = allColumnsOrigDf.reset_index()
    print 'Columns list from DataReader: {}'.format(allColumnsNoIndexDf.columns.values)
    print 'Index from DataReader: {}'.format(allColumnsNoIndexDf.index)
    if priceColumn in allColumnsNoIndexDf:
        dataDf = allColumnsNoIndexDf[[symbolColumn,dateColumn, priceColumn]]
    else:
        print 'Column {} doesn''t exist. Using [''Symbol'', ''Date'', ''Close'']'.format(priceColumn)
        dataDf = allColumnsNoIndexDf[['Symbol', 'Date', 'Close']]
    # dataDf.to_csv(downloadDir + '/downloadedInstrumentsOnlyOnePriceColRaw.csv')
    newDf = pivot(dataDf)

    if not os.path.exists(directory):
        os.makedirs(directory)

    # allColumnsNoIndexDf.to_csv(downloadDir + '/downloadedInstrumentsNoIndexAllCols.csv')
    earliest_date = start_date + dt.timedelta(days=7)
    cols_to_exclude =  newDf.loc[:earliest_date].isnull().all()
    cols_to_keep    = ~cols_to_exclude
    print 'Earliest date to compare: {}'.format(str(earliest_date))
    print 'Columns to keep: {}'.format(str(cols_to_keep))
    print 'Columns excluded: {}'.format(str(cols_to_exclude))
    newDf = newDf.loc[:, cols_to_keep]
    newDf.dropna(axis=1, inplace=True)

    newDf.to_csv(directory + '/' + downloadFileName)
    print 'download instruments done'
    return directory + '/' + downloadFileName


def pivot(dataDf):
    symbolColumn= st.config['downloader']['symbolColumn']
    dateColumn  = st.config['downloader']['dateColumn']
    priceColumn = st.config['downloader']['priceColumn']
    symbolsArray = dataDf[symbolColumn].unique()
    print 'symbols in data: {}'.format(symbolsArray)
    dfRet = pd.DataFrame()
    for i, sym in enumerate(symbolsArray):
        newSymData = dataDf.loc[dataDf[symbolColumn] == sym][[dateColumn, priceColumn]]
        earliest_date = pd.to_datetime(newSymData['date']).min()
        print 'sym={}, earliest date={}'.format(sym, earliest_date)
        # dataDf.to_csv('downloads/newSymData.csv')
        newSymData.columns = [dateColumn, sym]
        if i < 1:
            dfRet = newSymData.copy()
        else:
            dfRet = pd.merge(dfRet, newSymData, on=dateColumn, how='outer')

    reversed = dfRet.set_index(dateColumn)
    reversed.index.names = ['date']
    # reversed = reversed.reindex(index=reversed.index[::-1])
    data = reversed
    data.columns = symbolsArray
    return data

if __name__ == "__main__":
    main()
