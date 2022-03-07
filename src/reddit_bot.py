import os
import random
import traceback
from enum import Enum
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
from typing import Tuple, List, Optional, Dict
from uuid import uuid4
import json

import praw

from src.database import DBFactory
from src.database_models import RedditPostTable, RedditPostLogPointTable, GroupEnum
from src.utils import get_logger, safe_call

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")
RATELIMIT = int(os.getenv("RATELIMIT", 5))

logger = get_logger("REDDIT-BOT")


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
            post
            for post in self.reddit.subreddit(subreddit).new(limit=batch_size)
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

        batch_id = str(uuid4())

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
            post.batch_id = batch_id

        for post in control_posts:
            post.group = GroupEnum.CONTROL
            post.batch_id = batch_id

        return treatment_posts, control_posts

    @staticmethod
    def add_posts_to_db(
        posts: List[praw.models.Submission],
        backup: bool = False,
    ) -> None:

        prepared_posts = []

        def _prepare_post(post: praw.models.Submission) -> Dict:
            return dict(
                id=post.id,
                batch_id=post.batch_id,
                group=post.group,
                subreddit=str(post.subreddit),
                title=post.title,
                creation_date=post.created_utc,
            )

        for post in posts:
            prepared_post = safe_call(
                _prepare_post,
                args=[post],
                exception=Exception,
                raise_on_failure=False,
            )
            if prepared_post is not None:
                prepared_posts.append(prepared_post)

        if backup:
            today = datetime.today().date().isoformat()
            with open(f"backup/REDDITBOT_{today}_{str(uuid4())}.json", "w") as f:
                json.dump(prepared_posts, f, indent=4, default=str)

        db = DBFactory()()

        parsed_posts = [RedditPostTable(**post) for post in prepared_posts]
        db.add(parsed_posts)
        logger.info(f"Added {len(parsed_posts)} posts to the database")

        RedditBot.add_log_points(posts, backup=backup)

    @staticmethod
    def add_log_points(
        posts: List[praw.models.Submission], backup: bool = False
    ) -> None:

        prepared_posts = []
        stale_posts = []

        def _prepare_post(post: praw.models.Submission) -> Dict:
            return dict(
                id=post.id,
                score=post.score,
                num_comments=post.num_comments,
                date=datetime.now(),
            )

        for post in posts:
            prepared_post = safe_call(
                _prepare_post,
                args=[post],
                exception=Exception,
                raise_on_failure=False,
            )
            if prepared_post is not None:
                prepared_posts.append(prepared_post)
            else:
                stale_posts.append(post)

        if backup:
            today = datetime.today().date().isoformat()
            with open(f"backup/REDDITBOT_{today}_{str(uuid4())}.json", "w") as f:
                json.dump(prepared_posts, f, indent=4, default=str)

        db = DBFactory()()

        parsed_posts = [RedditPostLogPointTable(**post) for post in prepared_posts]
        db.add(parsed_posts)
        logger.info(f"Added {len(parsed_posts)} log points to database")

        for post in stale_posts:
            old_instance = db.get(RedditPostTable, id=post.id)
            if old_instance is not None:
                old_instance.active = False
                db.add([old_instance])

        logger.info(f"Marked {len(stale_posts)} stale posts")

    @staticmethod
    def get_stored_posts(max_age: int = 8) -> List[RedditPostTable]:
        db = DBFactory()()

        with db.session() as session:
            posts = (
                session.query(RedditPostTable)
                .filter(
                    RedditPostTable.creation_date
                    >= (datetime.now() - timedelta(days=max_age))
                )
                .filter(RedditPostTable.active)
                .all()
            )

            logger.info(f"Fetched {len(posts)} active posts from the database")

            return posts

    def _submission_wrapper(self, *args, **kwargs) -> Optional[praw.models.Submission]:
        try:
            return self.reddit.submission(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"{e}\n{traceback.format_exc()}\nargs: {args}\nkwargs: {kwargs}"
            )
            return None

    def get_posts(
        self, ids: List[str], threads: int = 4
    ) -> List[praw.models.Submission]:
        with ThreadPool(threads) as pool:
            posts = pool.map(self._submission_wrapper, ids)

        posts = [post for post in posts if post is not None]

        return posts
