from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONFIG не доставала, а просто строкой прописывала.

engine = create_engine(CONFIG)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
session = session_factory()


class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(JSONB, nullable=False)
    cv_results = Column(JSONB, nullable=False)


Base.metadata.create_all(engine)

# model = session.query(Model).filter_by(id=4).first()
# print(model.model['model'],'\n\n',model.cv_results['cv_results'])


session.commit()
session.close()

