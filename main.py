from src import RedditBot
from src.utils import safe_call, get_logger


def main():
    logger = get_logger()

    bot = RedditBot()
    treatment, control = safe_call(
        func=lambda: bot.group_posts(bot.get_batch_of_posts())
    )
    bot.add_posts_to_db(treatment)
    bot.add_posts_to_db(control)
    
    logger.info("Successfully added posts to database")


if __name__ == "__main__":
    main()
