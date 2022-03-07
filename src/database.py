from dataclasses import dataclass
from typing import Optional, TypeVar, List, Type
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import Table
from sqlmodel import create_engine, SQLModel, Session

ModelType = TypeVar("ModelType", bound=SQLModel)


@dataclass
class Database:
    engine: Engine

    @contextmanager
    def session(self):
        with Session(self.engine) as session:
            yield session

    def create_tables(self, tables: Optional[List[Table]] = None) -> None:
        SQLModel.metadata.create_all(self.engine, tables=tables)

    def drop_tables(self, tables: Optional[List[Table]] = None) -> None:
        SQLModel.metadata.drop_all(self.engine, tables=tables)

    def add(self, instances: List[ModelType]) -> None:
        with self.session() as session:
            session.add_all(instances)
            session.commit()

    def get(self, model: Type[ModelType], id: int) -> Optional[ModelType]:
        with Session(self.engine) as session:
            matches = session.query(model).filter(model.id == id).all()
            if len(matches) > 1:
                raise ValueError(
                    f"Multiple matches for {id=} in {model.__name__}:\n{matches}"
                )
            elif len(matches) == 0:
                return None
            return matches[0]


@dataclass
class DBFactory:
    engine_url: str = "sqlite:///database.db"

    def __call__(self, *args, **kwargs) -> Database:
        engine = create_engine(url=self.engine_url, **kwargs)
        return Database(engine=engine, **kwargs)
