from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import SQLModel, Field


class GroupEnum(str, Enum):
    CONTROL = "CONTROL"
    TREATMENT = "TREATMENT"


class RedditPost(SQLModel):
    pk: Optional[int] = Field(primary_key=True, default=None, index=True)
    id: str = Field(index=True)
    group: GroupEnum = Field(sa_column=Column(SAEnum(GroupEnum)))
    subreddit: str = Field()
    title: str = Field()
    score: int = Field()
    num_comments: int = Field()
    date: datetime = Field(description="Date at which stats were collected")
    creation_date: datetime = Field(description="Date at which post was created")


class RedditPostTable(RedditPost, table=True):
    __tablename__ = "RedditPost"
