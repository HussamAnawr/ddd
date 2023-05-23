import model
import abc 

class  AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError
    
    def get(self, reference) -> model.Batch:
        raise NotImplementedError