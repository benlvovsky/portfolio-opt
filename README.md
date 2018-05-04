##To build image from markowitzpy directory run:
`docker build -t img_markowitz .`
##or use '-no-cache' option to build from scratch
`docker build --no-cache -t img_markowitz .`

##normally first run the whole docker compose (see project Docker in dockerdm)
from dockerdm folder: `./lcompose.sh up`

##to run container iteractive into bash
`docker run -it img_markowitz:latest bash`
##access to bash on running markowitz-cont container:
`docker exec -it markowitz-cont bash`

#Running downloader:
1. Manually fix dates in markowitz.py in main()
2. run docker
3. run main like `./markowitz.py`

#downloading webrequest request sample
`http://localhost:5000/download?from=01/01/2010&to=17/04/2018&downloadFileName=data.csv&symbols=CBA.AX,WBC.AX,BHP.AX,ANZ.AX,NAB.AX,CSL.AX,WES.AX,TLS.AX,WOW.AX,MQG.AX,RIO.AX,TCL.AX,WPL.AX,SCG.AX,WFD.AX,IAG.AX,AMP.AX,BXB.AX,QBE.AX`
`http://localhost:5000/download?from=01/01/2010&to=17/04/2018&downloadFileName=data.csv&symbols=QQQ,VCSH,VCIT,DVY,PFF,EMB,MBB,CSJ,SHY,SCZ,VXUS,IBB,ACWI,IXUS,BNDX,SHV,IEF,CIU,TLT,IEI,SAGE,VNQI,AAXJ,IJT,VMBS,VTIP,PFPT,IUSG,ACWX,IUSV,OLLI,GWPH,MCHI,LGND,ARRY,LOXO,IMMU,TQQQ,FOLD,FV,VCLT,CSA,IGF,QTEC,AERI,NGHC,EUFN,SUPN,DGRW,APPN,IUSB,CALD,XLRN,VGSH,TTD,PRFZ,PDP,ESPR,VGIT,OSTK,XT,VONG,CRED,TBPH,SOXX,FEX,MDB,RDUS,ONEQ,FTSM,MB,XIV,APPF,SKYY,PAHC,PKW,FTSL,FIVN,ZGNX,VONV,VTWO,ISTB,HYLS,FTXO,INDY,FSCT,RVNC,AMRN,FTA,CMCT,XNCR,NMIH,CRSP,XENT,KBWB,BOLD,FLXN,VWOB,OMER,WVE,LMBS,APTI,CHUBA,CIFS,PID,IFV,PEY,CHUBK,RTRX,TRUP,EGRX,NYNY,IGOV,GDEN,SCMP,INSY,TDIV,PHO,ALDR,MZOR,BNFT,EVBG,RPD,FDT,ADMS,VONE,ANIP,USMC,LNTH,MDIV,BLDP,NTLA,RYTM,AIA,ACIU,VIGI,FNX,PDBC,AAOI,FEP,FTC,VYMI,DOVA,TPIC,AKBA,CARB,FFWM,OFLX,VNDA,TLND,FRPT,GDS,VBTX,HEWG,STAA,SLQD,CLXT,ATRC,VRAY,IFGL,FTCS,CNCE,ENTL,TRNC,EEMA,BBH,MBUU,LMAT,VGLT,GPP,IOVA,GLYC,QCRH,ANCX,FYX,CHRS,QQEW,PRTK,TCMD,USAT,TRHC,VUSE,URGN,WINA,ABTX,FRBK,RFDI,LOOP,RILY,FMBH,PNQI,RDNT,SNLN,HMTV,AKAO,PSCT,SQQQ,BLBD,BIB,FEM`
