from datetime import datetime, timedelta
from model import Batch, OrderLine, OutOfStock, allocate
import pytest

# ===========================
# Fixtures and helper funcs
# ===========================

today = datetime.today()
tomorrow = datetime.today() + timedelta(days=1)
later = datetime.today() + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, today),
        OrderLine("order-123", sku, line_qty),
    )


# ===========================
# Tests
# ===========================


def test_allocating_a_batch_reduces_the_available_qty():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("SMALL-TABLE", 200, 10)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("SMALL-TABLE", 10, 200)
    assert not small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 20)
    assert batch.can_allocate(line)


def test_cannot_allocate_the_same_line_twice():
    batch, line = make_batch_and_line("SMALL-TABLE", 100, 10)
    batch.allocate(line)
    batch.allocate(line)  # Second allocation should have no affect
    assert batch.available_quantity == 90


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("ref123", "SMALL-TABLE", 20, today)
    line = OrderLine("order123", "LARGE-TABLE", 10)
    assert batch.can_allocate(line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-TABLE", 10, today)
    allocate(OrderLine("order1", "SMALL-TABLE", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-TABLE"):
        allocate(OrderLine("order2", "SMALL-TABLE", 1), [batch])
