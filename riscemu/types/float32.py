import struct
from ctypes import c_float
from typing import Union, Any

bytes_t = bytes


class Float32:
    __slots__ = ("_val",)

    _val: c_float

    @property
    def value(self) -> float:
        """
        The value represented by this float
        """
        return self._val.value

    @property
    def bytes(self) -> bytes:
        """
        The values bit representation (as a bytes object)
        """
        return struct.pack("<f", self.value)

    @property
    def bits(self) -> int:
        """
        The values bit representation as an int (for easy bit manipulation)
        """
        return int.from_bytes(self.bytes, byteorder="little")

    @classmethod
    def from_bytes(cls, val: Union[int, bytes_t, bytearray]):
        if isinstance(val, int):
            val = int.to_bytes(byteorder="little")
        return Float32(val)

    def __init__(
        self, val: Union[float, c_float, "Float32", bytes_t, bytearray, int] = 0
    ):
        if isinstance(val, (float, int)):
            self._val = c_float(val)
        elif isinstance(val, c_float):
            self._val = c_float(val.value)
        elif isinstance(val, (bytes, bytearray)):
            self._val = c_float(struct.unpack("<f", val)[0])
        elif isinstance(val, Float32):
            self._val = val._val

    def __add__(self, other: Union["Float32", float]):
        if isinstance(other, Float32):
            other = other.value
        return self.__class__(self.value + other)

    def __sub__(self, other: Union["Float32", float]):
        if isinstance(other, Float32):
            other = other.value
        return self.__class__(self.value - other)

    def __mul__(self, other: Union["Float32", float]):
        if isinstance(other, Float32):
            other = other.value
        return self.__class__(self.value * other)

    def __truediv__(self, other: Any):
        return self // other

    def __floordiv__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.__class__(self.value // other)

    def __mod__(self, other: Union["Float32", float]):
        if isinstance(other, Float32):
            other = other.value
        return self.__class__(self.value % other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (float, int)):
            return self.value == other
        elif isinstance(other, Float32):
            return self.value == other.value
        return False

    def __neg__(self):
        return self.__class__(-self.value)

    def __abs__(self):
        return self.__class__(abs(self.value))

    def __bytes__(self) -> bytes_t:
        return self.bytes

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.value)

    def __str__(self):
        return str(self.value)

    def __format__(self, format_spec: str):
        return self.value.__format__(format_spec)

    def __hash__(self):
        return hash(self.value)

    def __gt__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.value > other

    def __lt__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.value < other

    def __le__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.value <= other

    def __ge__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.value >= other

    def __bool__(self):
        return bool(self.value)

    def __cmp__(self, other: Any):
        if isinstance(other, Float32):
            other = other.value
        return self.value.__cmp__(other)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise ValueError("Float32 pow with modulo unsupported")
        return self.__class__(self.value**power)

    # right handed binary operators

    def __radd__(self, other: Any):
        return self + other

    def __rsub__(self, other: Any):
        return self.__class__(other) - self

    def __rmul__(self, other: Any):
        return self * other

    def __rtruediv__(self, other: Any):
        return self.__class__(other) // self

    def __rfloordiv__(self, other: Any):
        return self.__class__(other) // self

    def __rmod__(self, other: Any):
        return self.__class__(other) % self

    def __rand__(self, other: Any):
        return self.__class__(other) & self

    def __ror__(self, other: Any):
        return self.__class__(other) | self

    def __rxor__(self, other: Any):
        return self.__class__(other) ^ self

    # bytewise operators:

    def __and__(self, other: Union["Float32", float, int]):
        if isinstance(other, float):
            other = Float32(other)
        if isinstance(other, Float32):
            other = other.bits
        return self.from_bytes(self.bits & other)

    def __or__(self, other: Union["Float32", float]):
        if isinstance(other, float):
            other = Float32(other)
        if isinstance(other, Float32):
            other = other.bits
        return self.from_bytes(self.bits | other)

    def __xor__(self, other: Union["Float32", float]):
        if isinstance(other, float):
            other = Float32(other)
        if isinstance(other, Float32):
            other = other.bits
        return self.from_bytes(self.bits ^ other)

    def __lshift__(self, other: int):
        return self.from_bytes(self.bits << other)

    def __rshift__(self, other: int):
        return self.from_bytes(self.bits >> other)
