"""
'Product Allocation'

"Domain-Driven Design is an approach to software development that centers the development on programming a domain model that has a rich understanding of the processes and rules of a domain."

Model: 
- A customer place orders for items (identified by thier SKU). 
- An order contains multiple order lines, each of which has a SKU and a quantity.
- Purchasing department order batches of stock, which will have a reference ID, a SKU and a qunatity.
- Order lines are allocated to batches, which will then allow the system to send stock to the customer.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set


class Order:
    def __init__(self, ref: str, order_lines: List[OrderLine]):
        self.ref = ref
        self.order_lines = order_lines

    def add_order_line(self, order_line: OrderLine):
        self.order_lines.append(order_line)


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str  # Stock-keeping unit
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.available_quantity >= line.qty and self.sku == line.sku


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")


class OutOfStock(Exception):
    pass
