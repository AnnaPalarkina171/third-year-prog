from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import sys

from .config import Config
from .log import get_logger

Base = declarative_base()
logger = get_logger(__name__)


def new_engine():
    try:
        config = Config()
    except ValueError as exc:
        logger.exception(f'Could not connect to db {exc}')
        # sys.exit(1)
        return None

    try:
        engine = create_engine(config.dsn)
        engine.execute("SELECT 1; ")
    except Exception as exc:
        logger.exception(f'Could not read config: {exc}')
        # sys.exit(1)
        return None
    return engine


def init_db():
    engine = new_engine()
    if engine is None:
        sys.exit(1)
    Base.metadata.create_all(engine)


class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(JSONB, nullable=False)
    cv_results = Column(JSONB, nullable=False)


if __name__ == '__main__':
    logger.info('Init db')
    init_db()

