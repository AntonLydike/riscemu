from collections import defaultdict
from typing import Dict, List, Optional

from .exceptions import ParseException
from ..core import T_AbsoluteAddress, T_RelativeAddress, NUMBER_SYMBOL_PATTERN


class InstructionContext:
    base_address: T_AbsoluteAddress
    """
    The address where the instruction block is placed
    """

    labels: Dict[str, T_RelativeAddress]
    """
    This dictionary maps all labels to their relative position of the instruction block
    """

    numbered_labels: Dict[str, List[T_RelativeAddress]]
    """
    This dictionary maps numbered labels (which can occur multiple times) to a list of (block-relative) addresses where
    the label was placed
    """

    global_symbol_dict: Dict[str, T_AbsoluteAddress]
    """
    A reference to the MMU's global symbol dictionary for access to global symbols
    """

    def __init__(self):
        self.labels = dict()
        self.numbered_labels = defaultdict(list)
        self.base_address = 0
        self.global_symbol_dict = dict()

    def resolve_numerical_label(
        self, symbol: str, address_at: int
    ) -> Optional[T_AbsoluteAddress]:
        direction = symbol[-1]
        values = self.numbered_labels.get(symbol[:-1], [])
        if direction == "b":
            return max(
                (addr + self.base_address for addr in values if addr < address_at),
                default=None,
            )
        else:
            return min(
                (addr + self.base_address for addr in values if addr > address_at),
                default=None,
            )

    def resolve_label(self, symbol: str) -> Optional[T_AbsoluteAddress]:
        # if it's not a local symbol, try the globals
        if symbol not in self.labels:
            return self.global_symbol_dict.get(symbol, None)
        # otherwise return the local symbol
        return self.labels.get(symbol, None)
