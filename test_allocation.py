from allocation import Batch, OrderLine

# ===========================
# Fixtures and helper funcs
# ===========================


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty),
        OrderLine("order-123", sku, line_qty),
    )

# ===========================
# Tests
# ===========================


def test_allocating_a_batch_reduces_the_available_qty():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.allocate(line)
    assert batch.qty == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("SMALL-TABLE", 200, 10)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("SMALL-TABLE", 10, 200)
    assert small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 20)
    assert batch.can_allocate(line)


def test_cannot_allocate_the_same_line_twice():
    batch, line = make_batch_and_line("SMALL-TABLE", 100, 10)
    batch.allocate(line)
    batch.allocate(line)  # Second allocation should have no affect
    assert batch.qty == 90


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("ref123", "SMALL-TABLE", 20)
    line = OrderLine("order123", "LARGE-TABLE", 10)
    assert batch.can_allocate(line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.qty == 20
