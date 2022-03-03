# RDS-Project-2022-1

Randomized control trail (RCT) investigating the impact on a post's popularity by giving an initial boost with a single upvote / like

# Setup
## Installing with Poetry
[Poetry](https://github.com/python-poetry/poetry) is recommended for installating and setting up the project. If poetry is installed, run:

```bash
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry install
```

Scripts can then be run with `poetry run python ${filename}` or alternatively by entering a poetry shell with `poetry shell`, from which scripts can simply be run with `python ${filename}`. 

## Installing with pip
A `requirements.txt` file is provided for convenience. Activate your preferred virtual environment and type the following command to install all dependencies:

```bash
pip install -r requirements.txt	
```

# How to run experiment
There are two main entry points to the experiment:
- `python setup.py` - which sets up the database file and creates appropriate tables
- `python main.py` - which fetches posts, groups them, and stores them in the database

Furthermore, a jupyter notebook is provided, which contains these entry points - `RoDS-Reddit-bot.ipynb`
