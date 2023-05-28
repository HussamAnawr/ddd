import abc
from allocation.adapters import repository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from allocation import config

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(config.get_postgres_uri()))

class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __exit__(self, *args):
        self.rollback()
    
    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory = DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
    
    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super.__enter__()
    
    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()