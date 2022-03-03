import os
import random
from enum import Enum
from datetime import datetime
from typing import Tuple, List
from uuid import uuid4
import json

import praw

from src.database import DBFactory
from src.database_models import RedditPostTable, GroupEnum

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")
RATELIMIT = os.getenv("RATELIMIT", 5)


class SelectionStrategyEnum(Enum):
    RANDOM = "RANDOM"
    EMBEDDINGS = "EMBEDDINGS"


class RedditBot:
    """
    Wrapper for the Reddit bot.

    It contains the following functions:
    - get_batch_of_posts: Selects a batch of posts for the experiment
    - group_posts: Groups a list of posts into treatment and control groups
    - add_posts_to_db: Adds a list of posts to the database
    """

    reddit: praw.Reddit
    url: str = "https://www.reddit.com"

    def __init__(
        self,
        client_id: str = CLIENT_ID,
        client_secret: str = CLIENT_SECRET,
        username: str = USERNAME,
        password: str = PASSWORD,
        user_agent: str = USER_AGENT,
        ratelimit: int = RATELIMIT,
    ):
        """
        Authenticates the bot and initializes the Reddit instance.
        """
        assert isinstance(client_id, str)
        assert isinstance(client_secret, str)
        assert isinstance(username, str)
        assert isinstance(password, str)
        assert isinstance(user_agent, str)
        assert isinstance(ratelimit, int)

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent,
            ratelimit=ratelimit,
        )

    def get_batch_of_posts(
        self,
        subreddit: str = "all",
        score: int = 1,
        num_comments: int = 1,
        batch_size: int = 64,
    ):
        """
        Selects a batch of posts with at most 'score' number of upvotes and
        'num_comments' number of comments in the given subreddit.
        
        NOTE: batch_size is an upper bound on the number of posts returned.
        """
        
        posts = [
            post for post in
            self.reddit.subreddit(subreddit).new(limit=batch_size)
            if post.score <= score and post.num_comments <= num_comments
        ]

        return posts

    @staticmethod
    def group_posts(
        posts: List[praw.models.Submission],
        strategy: SelectionStrategyEnum = SelectionStrategyEnum.RANDOM,
    ) -> Tuple[List[praw.models.Submission], List[praw.models.Submission]]:
        """
        Assigns posts into treatment and control groups.

        If the strategy is RANDOM, the posts are grouped randomly.
        If the strategy is EMBEDDINGS, the posts are embedded and paired up
        based on maximizing the mean cosine similarity.
        """
        
        if strategy == SelectionStrategyEnum.EMBEDDINGS:
            raise NotImplementedError
        
        else:
            random.shuffle(posts)
            if len(posts) % 2 != 0:
                posts.pop()  # Drop a random post to make the list even 
            
            middle = len(posts) // 2
            treatment_posts = posts[:middle]
            control_posts = posts[middle:]

        for post in treatment_posts:
            post.upvote()
            post.group = GroupEnum.TREATMENT

        for post in control_posts:
            post.group = GroupEnum.CONTROL

        return treatment_posts, control_posts

    @staticmethod
    def add_posts_to_db(
        posts: List[praw.models.Submission],
        backup: bool = False,
    ) -> None:

        prepared_posts = [
            dict(
                id=post.id,
                group=post.group,
                subreddit=str(post.subreddit),
                title=post.title,
                score=post.score,
                num_comments=post.num_comments,
                date=datetime.now(),
            )
            for post in posts
        ]

        if backup:
            today = datetime.today().date().isoformat()
            with open(f"backup/REDDITBOT_{today}_{str(uuid4())}.json", "w") as f:
                json.dump(prepared_posts, f, indent=4, default=str)

        db = DBFactory()()

        parsed_posts = [RedditPostTable(**post) for post in prepared_posts]
        db.add(parsed_posts)
