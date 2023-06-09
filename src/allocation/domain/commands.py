from dataclasses import dataclass
from typing import Optional
from datetime import date

class Command:
    pass

@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int

@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date]

@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    qty: int