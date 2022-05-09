"""
SKU - Stock-keeping unit
Order: order reference, order lines
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set


class Order:
    def __init__(self, ref: str, order_lines: List[OrderLine]):
        self.ref = ref
        self.order_lines = order_lines

    def add_order_line(self, order_line: OrderLine):
        self.order_lines.append(order_line)


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int):
        self.reference = ref
        self.sku = sku
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.qty >= line.qty and self.sku == line.sku
