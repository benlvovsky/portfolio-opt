##To build image from markowitzpy directory run:
`docker build -t img_markowitz .`
##or use '-no-cache' option to build from scratch
`docker build --no-cache -t img_markowitz .`
##to run container iteractive into bash
`docker run -it img_markowitz:latest bash`
