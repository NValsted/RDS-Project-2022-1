from src import RedditBot
from src.utils import safe_call


def main():
    bot = RedditBot()

    # Update old Posts
    posts = bot.get_stored_posts()
    ids = {post.id for post in posts}

    posts = bot.get_posts(ids)
    bot.add_log_points(posts)

    # New posts
    treatment, control = safe_call(
        func=lambda: bot.group_posts(bot.get_batch_of_posts())
    )
    bot.add_posts_to_db(treatment)
    bot.add_posts_to_db(control)


if __name__ == "__main__":
    main()
