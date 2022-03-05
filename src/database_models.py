from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import SQLModel, Field


class GroupEnum(str, Enum):
    CONTROL = "CONTROL"
    TREATMENT = "TREATMENT"


class RedditPost(SQLModel):
    id: str = Field(primary_key=True, index=True)
    batch_id: str = Field(
        index=True,
        description="Unique ID of the batch in which the post was added",
    )
    active: bool = Field(
        default=True, description="Indicates whether the post is reachable"
    )
    group: GroupEnum = Field(sa_column=Column(SAEnum(GroupEnum)))
    subreddit: str = Field()
    title: str = Field()
    creation_date: datetime = Field(description="Date at which post was created")


class RedditPostTable(RedditPost, table=True):
    __tablename__ = "RedditPost"


class RedditPostLogPoint(SQLModel):
    pk: Optional[int] = Field(primary_key=True, default=None, index=True)
    id: str = Field(index=True)
    score: int = Field()
    num_comments: int = Field()
    date: datetime = Field(description="Date at which stats were collected")


class RedditPostLogPointTable(RedditPostLogPoint, table=True):
    __tablename__ = "RedditPostLogPoint"
