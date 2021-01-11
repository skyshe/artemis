FROM python:3.9-alpine

LABEL maintainer="Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>"
ARG module=autostarter

# directories
RUN mkdir -p /etc/artemis/ && \
    mkdir -p /var/log/artemis && \
    mkdir -p /etc/service/$module && \
    mkdir -p /opt/$module && \
    mkdir -p /etc/run_once

WORKDIR /opt/$module

# deps
RUN apk add --no-cache postgresql-client postgresql-dev redis \
  curl git libffi-dev cmake libssh build-base runit bash python3-dev

COPY requirements.txt ./requirements.txt
RUN pip --no-cache-dir install -r requirements.txt --ignore-installed

COPY . .
COPY run /etc/service/$module/run
COPY dev /etc/run_once/dev

CMD ["./boot.sh"]
