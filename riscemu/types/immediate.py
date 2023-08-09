from abc import ABC
from enum import Enum

class ImmediateKind(Enum):
    integer = 0
    label = 1

class Immediate(ABC):
    value: int
    type: ImmediateKind

    def __init__(self, value, type):
        self.value = value
        self.type = type

    
    