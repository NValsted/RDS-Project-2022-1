FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Install Python3.9
RUN apt update -yq && apt install software-properties-common -yq
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.9 -yq
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Other unix and build tools
RUN apt-get update -yq && apt-get install -yq \
    make \
    curl \
    gcc \
    cron \
    libpq-dev \
    build-essential \
    sqlite3 \
    python3.9-dev \
    python3.9-venv \
    python3-setuptools

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.9 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry config virtualenvs.create true
RUN poetry config virtualenvs.in-project true

# Install project
COPY . /RDS-Project-2022-1/
WORKDIR /RDS-Project-2022-1/
RUN make setup

# Setup cronjob
RUN touch /var/log/cron.log
RUN chmod 0644 cronjob.sh
RUN crontab cronjob.sh

#CMD cron && tail -f /var/log/cron.log
