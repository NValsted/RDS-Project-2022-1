from enum import Enum
from datetime import datetime

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import SQLModel, Field


class GroupEnum(str, Enum):
    CONTROL = "CONTROL"
    TREATMENT = "TREATMENT"


class RedditPost(SQLModel):
    id: str = Field(primary_key=True, index=True)
    group: GroupEnum = Field(sa_column=Column(SAEnum(GroupEnum)))
    subreddit: str = Field()
    title: str = Field()
    score: int = Field()
    num_comments: int = Field()
    date: datetime = Field(description="Date at which stats were collected")


class RedditPostTable(RedditPost, table=True):
    __tablename__ = "RedditPost"
