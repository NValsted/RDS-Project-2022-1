# RDS-Project-2022-1

## Introduction

Randomized control trail (RCT) investigating the impact on a post's popularity by giving an initial boost with a single upvote / like

## Table of Contents
- [RDS-Project-2022-1](#rds-project-2022-1)
  * [Introduction](#introduction)
  * [Table of Contents](#table-of-contents)
- [Setup](#setup)
  * [Virtual environment](#virtual-environment)
    + [Installing with Poetry](#installing-with-poetry)
    + [Installing with pip](#installing-with-pip)
    + [Setup with Docker](#setup-with-docker)
  * [Environment variables](#environment-variables)
- [How to run the experiment](#how-to-run-the-experiment)

# Setup
## Virtual environment
### Installing with Poetry
[Poetry](https://github.com/python-poetry/poetry) is recommended for installating and setting up the project. If poetry is installed, run:

```bash
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry install
```

Scripts can then be run with `poetry run python ${filename}` or alternatively by entering a poetry shell with `poetry shell`, from which scripts can simply be run with `python ${filename}`. 

### Installing with pip
A `requirements.txt` file is provided for convenience. Activate your preferred virtual environment and type the following command to install all dependencies:

```bash
pip install -r requirements.txt	
```

### Setup with Docker
Alternatively, you can use [Docker](https://www.docker.com/) to run the project. To do so, first build the Docker image with the following command from the root of this repository:
```bash
docker build . -t rct/main:latest
```
or simply
```bash
make build-image
```

Then run the Docker image with the following command:
```bash
docker run rct/main:latest
```

## Environment variables
To authenticate the bot and the bot's API, you need to set the following environment variables with their appropriate values:
```bash
export CLIENT_ID=
export CLIENT_SECRET=
export USERNAME=
export PASSWORD=
export USER_AGENT=
```

# How to run the experiment
There are two main entry points to the experiment:
- `python setup.py` - which sets up the database file and creates appropriate tables
- `python main.py` - which fetches posts, groups them, and stores them in the database
