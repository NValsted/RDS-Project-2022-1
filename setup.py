from src.database_models import RedditPostTable
from src.database import DBFactory


def setup():
    db = DBFactory()()
    db.drop_tables()
    db.create_tables()


if __name__ == "__main__":
    setup()
