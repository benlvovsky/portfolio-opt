# financials scientific libs python 2.7 build
FROM ubuntu:16.04
MAINTAINER Benjamin Lvovsky, ben@lvovsky.com

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y \
#--allow-unauthenticated \
    build-essential \
#    build-dep \
    wget \
    ca-certificates \
    gcc \
#    git \
#    libpq-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
#    python-matplotlib \
#    python-setuptools \
#    python-numpy \
#    python-scipy \
#    libatlas-dev \
    libpng-dev libjpeg8-dev libfreetype6-dev \
    curl \
    postgresql-client-9.6 postgresql-contrib-9.6 \
    vim \
    python-qt4 	    # not needed in non interactive version. TODO: remove for prod \
    && apt-get autoremove \
    && apt-get clean

#RUN pip install pip setuptools
RUN pip install --upgrade pip
RUN pip install numpy
RUN pip install scipy
RUN pip install matplotlib
# ipython jupyter pandas sympy nose
RUN pip install scikit-learn
RUN pip install cython
RUN pip install pandas
RUN pip install pandas-datareader
RUN pip install seaborn
RUN pip install Flask
RUN pip install PyYAML
RUN pip install statsmodels

#RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
#  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
#  cd ta-lib/ && \
#  ./configure --prefix=/usr && \
#  make && \
#  make install
#RUN pip install ta-lib

##################

RUN echo 'root:root' | chpasswd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN echo 'alias dev="cd /usr/src/app"' >> ~/.bashrc

#RUN sed -i -E 's/^(\s*)system\(\);/\1unix-stream("\/dev\/log");/' /etc/syslog-ng/syslog-ng.conf
#RUN echo 'SYSLOGNG_OPTS="--no-caps"' >> /etc/default/syslog-ng

RUN mkdir -p /usr/src/app
COPY ./dx /usr/src/app/dx
COPY ./dx_mean_variance_portfolio.py /usr/src/app/dx_mean_variance_portfolio.py
COPY ./markowitz.py /usr/src/app/markowitz.py
COPY ./meanvarianceportfolio.py /usr/src/app/meanvarianceportfolio.py
COPY ./webapp.py /usr/src/app/webapp.py

WORKDIR /usr/src/app

#CMD ["webapp.py"]
CMD ["bash"]
