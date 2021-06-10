FROM python:3.8-slim AS base

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
#ARG AIRFLOW_VERSION=1.10.13
ARG PYTHON_VER=3.8
ARG AIRFLOW_VERSION=2.1.0
ARG AIRFLOW_HOME=/opt/airflow

ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VER}.txt"

ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

ENV UID=1000
ENV GID=1001

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

# Python dependencies to be installed
COPY config/base.txt ${AIRFLOW_HOME}/base.txt

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-mysql-client \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        gnupg \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && groupadd -g ${GID} airflow \
    && useradd -u ${UID} -g ${GID} -ms /bin/bash -d ${AIRFLOW_HOME} airflow \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install pyasn1 \
    && pip install -U apache-airflow[kubernetes,crypto,statsd,celery,postgres,ssh${AIRFLOW_DEPS:+,}${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} --constraint ${CONSTRAINT_URL}\
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi \
    && pip install -Ur ${AIRFLOW_HOME}/base.txt \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base


RUN adduser airflow airflow

ADD scripts/entrypoint.sh /entrypoint.sh
ADD config/requirements.txt ${AIRFLOW_HOME}/requirements.txt
RUN pip install -Ur ${AIRFLOW_HOME}/requirements.txt


RUN chmod +x /entrypoint.sh
RUN chown -R airflow:airflow ${AIRFLOW_HOME}


RUN set -ex \
    && curl -L -o azcopy.tar.gz \
    https://aka.ms/downloadazcopy-v10-linux \
    && tar -xf azcopy.tar.gz --strip-components=1 \
    && rm -f azcopy.tar.gz && cp azcopy /usr/local/bin \
    && rm azcopy \
    && chmod 777 /usr/local/bin/azcopy


EXPOSE 8080 5555 8793

USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]

FROM base as test

USER root 

ADD config/requirements.test.txt ${AIRFLOW_HOME}/requirements.test.txt
RUN pip install -Ur ${AIRFLOW_HOME}/requirements.test.txt

COPY tests/ tests/

USER 0

# FROM base as release

# COPY dags ${AIRFLOW_HOME}
