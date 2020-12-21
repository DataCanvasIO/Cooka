from sqlalchemy import create_engine, Column
from sqlalchemy.orm import sessionmaker
import contextlib
from cooka.common import consts
engine = create_engine(f'sqlite:///{consts.PATH_DATABASE}', echo=False, echo_pool=False, logging_name="cooka-web")  # echo for showing sql


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(engine)


@contextlib.contextmanager
def open_session():
    global engine
    Session = sessionmaker(engine)
    session = Session()
    # session.query()
    yield session

    if session is not None:
        session.commit()
        session.close()

