from datetime import timedelta, datetime
from enum import Enum

import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px

from src.database import DBFactory
from src.database_models import RedditPostTable, RedditPostLogPointTable


class TargetAttributeEnum(Enum):
    SCORE = "score"
    COMMENTS = "num_comments"


def get_distplot(data, attribute: TargetAttributeEnum = TargetAttributeEnum.SCORE):
    hist_data = [
        data[data["group"] == "CONTROL"][attribute.value],
        data[data["group"] == "TREATMENT"][attribute.value],
    ]
    return ff.create_distplot(
        hist_data,
        group_labels=["CONTROL", "TREATMENT"],
    )


def get_scatter(data, attribute: TargetAttributeEnum = TargetAttributeEnum.SCORE):
    return px.scatter(data, x="date", y=attribute.value, color="group", opacity=0.25)


def generate_figures():
    posts = pd.read_sql_table(RedditPostTable.__tablename__, DBFactory.engine_url)
    log_points = pd.read_sql_table(
        RedditPostLogPointTable.__tablename__, DBFactory.engine_url
    )

    posts = posts[posts["creation_date"] >= (datetime.now() - timedelta(days=8))]
    joined = pd.merge(posts, log_points, on="id", how="left")

    distplot = get_distplot(joined)
    scatter = get_scatter(joined)

    return distplot, scatter
