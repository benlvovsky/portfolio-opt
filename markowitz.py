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
import findata as fd
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
marketDataASX= 'BHP,ANZ,CBA,WBC,NAB,CSL,WES,TLS,WOW,MQG,RIO,TCL,WPL,SCG,WFD,IAG,AMP,BXB,QBE'
asxTop20StrGoogle = 'ASX:CBA,ASX:WBC,ASX:BHP,ASX:ANZ,ASX:NAB,ASX:CSL,ASX:WES,ASX:TLS,ASX:WOW,ASX:MQG,ASX:RIO,ASX:TCL,ASX:WPL,ASX:SCG,ASX:WFD,ASX:IAG,ASX:AMP,ASX:BXB,ASX:QBE'
smallGlobalStr = 'AAPL,GOOGL,GOOG'

def main():
    # sharpeAndCml('upload', 0.03, "")
    start = dt.datetime(2013, 2, 1) #yyyy,mm,dd
    end = dt.datetime(2017, 12, 01)
    print 'will run downloadInstruments'
    # downloadInstruments('yahoo', asxTop20Str, start, end, 'dataAllcolsTop200.csv')
    # downloadInstruments('morningstar', 'AAPL,GOOGL', 'Close', start, end, 'dataAllcolsTop200.csv')
    # fd.FinDownloader('marketdata').downloadInstruments(marketDataASX, start, end)
    source = st.config['downloader']['activesource']
    fd.FinDownloader(source).downloadInstruments("", start, end)


# def getEfficientFrontierPortfolios(port, evols):
#     portfolios = list()
#     for v in evols:
#         port.optimize('Return', constraint=v, constraint_type='Exact')
#         portfolios.append(copy.copy(port))
#
#     return portfolios


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



if __name__ == "__main__":
    main()
