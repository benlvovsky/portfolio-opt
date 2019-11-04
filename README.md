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

#sample CLI request
./markowitz.py
./markowitz.py -r 0.25 -l -1 -i 1 -p return -n True
./markowitz.py -l 0 -i 1 -o redis -k -5899980560828067072
