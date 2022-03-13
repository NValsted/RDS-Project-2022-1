from datetime import timedelta, datetime
from enum import Enum

import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from pandas_profiling import ProfileReport

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


def get_df(latest_log_point: bool = False):
    posts = pd.read_sql_table(RedditPostTable.__tablename__, DBFactory.engine_url)
    log_points = pd.read_sql_table(
        RedditPostLogPointTable.__tablename__, DBFactory.engine_url
    )

    posts = posts[posts["creation_date"] >= (datetime.now() - timedelta(days=8))]
    joined = pd.merge(posts, log_points, on="id", how="left")

    if latest_log_point:
        sorted = joined.sort_values(["date"], ascending=False)
        grouped = sorted.groupby(by="id")
        latest = grouped.first()
        return latest
    else:
        if len(joined) > 10000:
            return joined[joined["score"] >= 10]
        return joined


def generate_figures():
    df = get_df()
    scatter = get_scatter(df)

    df_latest_points = get_df(latest_log_point=True)
    distplot = get_distplot(df_latest_points)

    return distplot, scatter


def profile_report():
    df = get_df(latest_log_point=True)

    report = ProfileReport(
        df, title="Reddit Post Report", explorative=True, minimal=True
    )
    return report
