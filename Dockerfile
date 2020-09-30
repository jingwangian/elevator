FROM python:3.8.2-slim-buster

LABEL maintainer "Ian Wang <jingwangian@gmail.com>"


USER root

ARG BTC_USER="btc"
ARG BTC_UID="500"
ARG BTC_GID="500"

RUN groupadd -g ${BTC_GID} btc
RUN useradd -d /opt/btc -g btc -u $BTC_UID -m $BTC_USER

# Setup app volumes
VOLUME /opt/btc
WORKDIR /opt/btc

# Install requirements + build/test tools
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 --no-cache install -r /tmp/requirements.txt

COPY --chown=${BTC_UID}:${BTC_GID} src /opt/btc

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

USER ${BTC_USER}
