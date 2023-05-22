from datetime import date, timedelta
from model import Batch, OrderLine, allocate, OutOfStock
import pytest


today =date.today()
tomorrow = date.today() + timedelta(days=1)
later = date.today() + timedelta(days=5)

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch =Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "RETRO-CLOCK", 100, eta=today)
    medium = Batch("normal-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    latest = Batch("slow-batch", "RETRO-CLOCK", 100, eta=later)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    earliest = Batch("speedy-batch", "RETRO-CLOCK", 100, eta=today)
    medium = Batch("normal-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    latest = Batch("slow-batch", "RETRO-CLOCK", 100, eta=later)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocation = allocate(line, [medium, earliest, latest])

    assert allocation == earliest.reference

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine('order-1', 'SMALL-FORK', 10), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order-2', 'SMALL-FORK', 10), [batch])