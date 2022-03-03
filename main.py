from src import RedditBot
from src.utils import safe_call, get_logger


def main():
    logger = get_logger()

    bot = RedditBot()

    # Update old Posts
    posts = bot.get_stored_posts()
    ids = {post.id: post.group for post in posts}
    logger.info(f"Fetched {len(ids)} ids from the database.")

    posts = bot.get_posts(ids.keys())
    for post in posts:
        post.group = ids[post.id]

    bot.add_posts_to_db(posts)

    # New posts
    treatment, control = safe_call(
        func=lambda: bot.group_posts(bot.get_batch_of_posts())
    )
    bot.add_posts_to_db(treatment)
    bot.add_posts_to_db(control)
    
    logger.info("Successfully added posts to database")


if __name__ == "__main__":
    main()
