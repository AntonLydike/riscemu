from typing import Union
from ctypes import c_int32, c_uint32


class Int32:
    _type = c_int32
    __slots__ = ('_val',)

    def __init__(self, val: Union[int, c_int32, c_uint32, 'Int32', bytes, bytearray] = 0):
        if isinstance(val, (bytes, bytearray)):
            self._val = self.__class__._type(int.from_bytes(val, 'little', signed=True))
        elif isinstance(val, self.__class__._type):
            self._val = val
        elif isinstance(val, (c_uint32, c_int32, Int32)):
            self._val = self.__class__._type(val.value)
        elif isinstance(val, int):
            self._val = self.__class__._type(val)
        else:
            raise RuntimeError(
                "Unknonw {} input type: {} ({})".format(self.__class__.__name__, type(val), val)
            )

    def __add__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value

        return self.__class__(self._val.value + other)

    def __sub__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value - other)

    def __mul__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value * other)

    def __truediv__(self, other):
        return self // other

    def __floordiv__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self.value // other)

    def __mod__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value % other)

    def __and__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value & other)

    def __or__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value | other)

    def __xor__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self._val.value ^ other)

    def __lshift__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self.value << other)

    def __rshift__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.__class__(self.value >> other)

    def __eq__(self, other: Union['Int32', int]):
        if isinstance(other, Int32):
            other = other.value
        return self.value == other

    def __neg__(self):
        return self.__class__(-self._val.value)

    def __abs__(self):
        return self.__class__(abs(self.value))

    def __bytes__(self):
        return self.to_bytes(4)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __str__(self):
        return str(self.value)

    def __format__(self, format_spec):
        return self.value.__format__(format_spec)

    def __hash__(self):
        return hash(self.value)

    def __gt__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.value > other

    def __lt__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.value < other

    def __le__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.value <= other

    def __ge__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.value >= other

    def __bool__(self):
        return bool(self.value)

    def __cmp__(self, other):
        if isinstance(other, Int32):
            other = other.value
        return self.value.__cmp__(other)

    # right handed binary operators

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self.__class__(other) - self

    def __rmul__(self, other):
        return self * other

    def __rtruediv__(self, other):
        return self.__class__(other) // self

    def __rfloordiv__(self, other):
        return self.__class__(other) // self

    def __rmod__(self, other):
        return self.__class__(other) % self

    def __rand__(self, other):
        return self.__class__(other) & self

    def __ror__(self, other):
        return self.__class__(other) | self

    def __rxor__(self, other):
        return self.__class__(other) ^ self

    @property
    def value(self):
        return self._val.value

    def unsigned(self) -> 'UInt32':
        return UInt32(self)

    def to_bytes(self, bytes: int = 4) -> bytearray:
        return bytearray(self.unsigned_value.to_bytes(bytes, 'little'))

    def signed(self) -> 'Int32':
        if self.__class__ == Int32:
            return self
        return Int32(self)

    @property
    def unsigned_value(self):
        return c_uint32(self.value).value

    def shift_right_logical(self, ammount: Union['Int32', int]):
        if isinstance(ammount, Int32):
            ammount = ammount.value
        return self.__class__((self.value % 0x100000000) >> ammount)

    def __int__(self):
        return self.value

    def __hex__(self):
        return hex(self.value)


class UInt32(Int32):
    _type = c_uint32

    def unsigned(self) -> 'UInt32':
        return self

    @property
    def unsigned_value(self):
        return self._val.value

    def shift_right_logical(self, ammount: Union['Int32', int]):
        return self >> ammount
