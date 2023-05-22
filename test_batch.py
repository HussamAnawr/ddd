from model import Batch, OrderLine
from datetime import date

def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch('batch-001', sku=sku, qty=batch_qty, eta=date.today()),
        OrderLine("order-123", sku=sku, qty=line_qty)
    )

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", 20, date.today())
    line = OrderLine('order-ref', "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert not small_batch.can_allocate(large_line)

def test_can_allocate_of_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_sku_do_not_match():
    batch = Batch("batch-001", "SMALL-TABLE", 20, date.today())
    line = OrderLine('order-ref', "LARGE-TABLE", 2)
    assert not batch.can_allocate(line)

def test_can_only_deallocate_allocated_lines():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.deallocate(line)
    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18