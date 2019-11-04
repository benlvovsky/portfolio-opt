FROM python:3
MAINTAINER Benjamin Lvovsky, ben@lvovsky.com
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get upgrade -y 
RUN apt-get install -y \
    libssl-dev \
    libffi-dev \
    libpng-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
	git \
    wget \
    curl \
    vim \
    python-qt4 	    # not needed in non interactive version. TODO: remove for prod \
	libxml2-dev \
	libxslt-dev \
	python-dev \
	zlib1g-dev

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN mkdir -p /usr/src/app
COPY . .

CMD ["python", "./webapp.py"]
