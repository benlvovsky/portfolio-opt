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
