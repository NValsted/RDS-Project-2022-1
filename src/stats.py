from datetime import timedelta, datetime
from enum import Enum

import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px

from src.database import DBFactory
from src.database_models import RedditPostTable


class TargetAttributeEnum(Enum):
    SCORE = "score"
    COMMENTS = "num_comments"


def get_distplot(data, attribute: TargetAttributeEnum = TargetAttributeEnum.SCORE):
    hist_data = [
        data[data["group"] == "CONTROL"][attribute.value],
        data[data["group"] == "TREATMENT"][attribute.value]
    ]
    return ff.create_distplot(
        hist_data,
        group_labels=["CONTROL", "TREATMENT"],
    )


def get_scatter(data, attribute: TargetAttributeEnum = TargetAttributeEnum.SCORE):
    return px.scatter(data, x="date", y=attribute.value, color="group", opacity=0.25)


def generate_figures():
    df = pd.read_sql_table(RedditPostTable.__tablename__, DBFactory.engine_url)
    df = df[df["creation_date"] >= (datetime.now() - timedelta(days=8))]

    distplot = get_distplot(df)
    scatter = get_scatter(df)
    
    return distplot, scatter
