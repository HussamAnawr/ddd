from datetime import date
from unittest import mock
import pytest

from allocation.adapters import repository
from allocation.domain import events
from allocation.service_layer import handlers, messagebus, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class TestAddBatch:

    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(events.BatchedCreated("b1", "CRUNCHY_ARMCHAIR", 100, None), uow)
        assert uow.products.get("CRUNCHY_ARMCHAIR") is not None
        assert uow.committed


class TestAllocate:

    def test_returns_allocations(self):
        uow = FakeUnitOfWork()
        messagebus.handle(events.BatchedCreated("batch1", "COMPLICATED_LAMP", 100, None), uow)
        [result] = messagebus.handle(
            events.AllocationRequired("o1", "COMPLICATED_LAMP", 10), uow
        )
        assert result == "batch1"


class TestChangeBatchQuantity:

    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            events.BatchedCreated("batch1", "ADORABLE-SETTEE", 100, None), uow
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        messagebus.handle(events.BatchQuantityChanged(ref="batch1", qty=50), uow)

        assert batch.available_quantity == 50

    def test_reallocations_if_necessary(self):
        uow = FakeUnitOfWork()
        event_history =[
            events.BatchedCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchedCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history: 
            messagebus.handle(e, uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(events.BatchQuantityChanged("batch1", 25), uow)
        assert batch1.available_quantity == 5
        assert batch2.available_quantity == 30