from src.database_models import RedditPostTable, RedditPostLogPointTable  # NOQA : F401
from src.database import DBFactory


def setup():
    db = DBFactory()()
    db.drop_tables()
    db.create_tables()


if __name__ == "__main__":
    setup()
