#!/usr/bin/env python

import traceback
import matplotlib
matplotlib.use('Agg')
#matplotlib.use('qt5agg')
#matplotlib.use('qt4agg')
#import PyQt4
# import matplotlib.pyplot as plt
# import json
# from dx import *
import datetime as dt
import dx
import seaborn as sns;
import copy
import settings as st
import meanvarianceportfolio as mvp
import pandas as pd
from pandas_datareader import data as web
import os
# from scipy import interpolate
# import sympy

sns.set()

asxTop20 = ['CBA.AX','WBC.AX','BHP.AX','ANZ.AX','NAB.AX','CSL.AX','WES.AX','TLS.AX','WOW.AX',\
            'MQG.AX','RIO.AX','TCL.AX','WPL.AX','SCG.AX',\
#             'SUN.AX',\
            'WFD.AX','IAG.AX','AMP.AX','BXB.AX','QBE.AX']
original = ['AAPL', 'GOOG', 'MSFT', 'FB']
globalTop100Str = 'DDD,MMM,WBAI,WUBA,EGHT,AHC,AIR,AAN,ABB,ABT,ABBV,ANF,GCH,ACP,JEQ,SGF,ABM,AKR,ACN,ACCO,ATV,ATU,AYI,ADX,PEO,AGRO,ATGE,AAP,WMS,ASX,AAV,AVK,AGC,LCM,ACM,ANW,AED,AEG,AEH,AER,AJRD,AET,AMG,AFL,MITT,AGCO,A,AEM,ADC,AGU,AL,APD,AYR,AKS,ALG,AGI,ALK,AIN,ALB,AA,ALEX,ALX,ARE,AQN,Y,ATI,ALLE,AGN,ALE,AKP,ADS,AFB,AOI,AWF,AB,LNT,CBH,NCV,NCZ,ACV,NIE,NFJ,ALSN,ALL'
globalTop200Str = 'QQQ,VCSH,VCIT,DVY,PFF,EMB,MBB,CSJ,SHY,SCZ,VXUS,IBB,ACWI,IXUS,BNDX,SHV,IEF,CIU,TLT,IEI,SAGE,VNQI,AAXJ,IJT,VMBS,VTIP,PFPT,IUSG,ACWX,IUSV,OLLI,GWPH,MCHI,LGND,ARRY,LOXO,IMMU,TQQQ,FOLD,FV,VCLT,CSA,IGF,QTEC,AERI,NGHC,EUFN,SUPN,DGRW,APPN,IUSB,CALD,XLRN,VGSH,TTD,PRFZ,PDP,ESPR,VGIT,OSTK,XT,VONG,CRED,TBPH,SOXX,FEX,MDB,RDUS,ONEQ,FTSM,MB,XIV,APPF,SKYY,PAHC,PKW,FTSL,FIVN,ZGNX,VONV,VTWO,ISTB,HYLS,FTXO,INDY,FSCT,RVNC,AMRN,FTA,CMCT,XNCR,NMIH,CRSP,XENT,KBWB,BOLD,FLXN,VWOB,OMER,WVE,LMBS,APTI,CHUBA,CIFS,PID,IFV,PEY,CHUBK,RTRX,TRUP,EGRX,NYNY,IGOV,GDEN,SCMP,INSY,TDIV,PHO,ALDR,MZOR,BNFT,EVBG,RPD,FDT,ADMS,VONE,ANIP,USMC,LNTH,MDIV,BLDP,NTLA,RYTM,AIA,ACIU,VIGI,FNX,PDBC,AAOI,FEP,FTC,VYMI,DOVA,TPIC,AKBA,CARB,FFWM,OFLX,VNDA,TLND,FRPT,GDS,VBTX,HEWG,STAA,SLQD,CLXT,ATRC,VRAY,IFGL,FTCS,CNCE,ENTL,TRNC,EEMA,BBH,MBUU,LMAT,VGLT,GPP,IOVA,GLYC,QCRH,ANCX,FYX,CHRS,QQEW,PRTK,TCMD,USAT,TRHC,VUSE,URGN,WINA,ABTX,FRBK,RFDI,LOOP,RILY,FMBH,PNQI,RDNT,SNLN,HMTV,AKAO,PSCT,SQQQ,BLBD,BIB,FEM'

def main():
    # sharpeAndCml('upload', 0.03, "")
    start = dt.datetime(2010, 1, 1)
    end = dt.datetime(2017, 12, 31)
    print 'will run downloadInstruments'
    downloadInstruments('yahoo', globalTop200Str, start, end)
    print 'done'

def getEfficientFrontierPortfolios(port, evols):
    portfolios = list()
    for v in evols:
        port.optimize('Return', constraint=v, constraint_type='Exact')
        portfolios.append(copy.copy(port))
    
    return portfolios

def sharpeAndCml(source, riskFree, symbols):
    ma = dx.market_environment('ma', dt.date(2010, 1, 1))
    ma.add_list('symbols', symbols)
    ma.add_constant('source', source)
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

def downloadInstruments(source, symbols, start_date, final_date):
    dataDf = web.DataReader(symbols.split(','), source, start_date, final_date)['Adj Close']
    downloadDir = 'downloads'
    if not os.path.exists(downloadDir):
        os.makedirs(downloadDir)
    # dataDf.to_csv(downloadDir + '/downloadedInstruments1.csv')
    dataDf.index.names = ['date']
    newDf = dataDf.sort_index()
    # newDf.to_csv(downloadDir + '/downlWithEmpty.csv')
    newDf.dropna(axis=1, inplace=True)
    newDf.to_csv(downloadDir + '/dataAllcolsTop200.csv')

if __name__ == "__main__":
    main()
