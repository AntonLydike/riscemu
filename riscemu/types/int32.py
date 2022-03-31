from typing import Union
from ctypes import c_int32, c_uint32


class Int32:
    """
    This class implements 32bit signed integers (see :class:`UInt32` for unsigned integers)

    It implements basically all mathematical dunder magic methods (__add__, __sub__, etc.)

    You can use it just like you would any other integer, just be careful when passing it
    to functions which actually expect an integer and not a Int32.
    """
    _type = c_int32
    __slots__ = ('_val',)

    def __init__(self, val: Union[int, c_int32, c_uint32, 'Int32', bytes, bytearray] = 0):
        if isinstance(val, (bytes, bytearray)):
            signed = len(val) == 4 and self._type == c_int32
            self._val = self.__class__._type(int.from_bytes(val, 'little', signed=signed))
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
    def value(self) -> int:
        """
        The value represented by this Integer
        :return:
        """
        return self._val.value

    def unsigned(self) -> 'UInt32':
        """
        Convert to an unsigned representation. See :class:Uint32
        :return:
        """
        return UInt32(self)

    def to_bytes(self, bytes: int = 4) -> bytearray:
        """
        Convert to a bytearray of length :param:bytes

        :param bytes: The length of the bytearray
        :return: A little-endian representation of the contained integer
        """
        return bytearray(self.unsigned_value.to_bytes(4, 'little'))[0:bytes]

    def signed(self) -> 'Int32':
        """
        Convert to a signed representation. See :class:Int32
        :return:
        """
        if self.__class__ == Int32:
            return self
        return Int32(self)

    @property
    def unsigned_value(self):
        """
        Return the value interpreted as an unsigned integer
        :return:
        """
        return c_uint32(self.value).value

    def shift_right_logical(self, ammount: Union['Int32', int]) -> 'Int32':
        """
        This function implements logical right shifts, meaning that the sign bit is shifted as well.

        This is equivalent to (self.value % 0x100000000) >> ammount

        :param ammount: Number of positions to shift
        :return: A new Int32 object representing the shifted value (keeps the signed-ness of the source)
        """
        if isinstance(ammount, Int32):
            ammount = ammount.value
        return self.__class__((self.value % 0x100000000) >> ammount)

    def __int__(self):
        return self.value

    def __hex__(self):
        return hex(self.value)

    @classmethod
    def sign_extend(cls, data: Union[bytes, bytearray, int], bits: int):
        """
        Create an instance of Int32 by sign extending :param:bits bits from :param:data
        to 32 bits

        :param data: The source data
        :param bits: The number of bits in the source data
        :return: An instance of Int32, holding the sign-extended value
        """
        if isinstance(data, (bytes, bytearray)):
            data = int.from_bytes(data, 'little')
        sign = data >> (bits - 1)
        if sign > 1:
            print("overflow in Int32.sext!")
        if sign:
            data = (data & (2 ** (bits - 1) - 1)) - 2**(bits-1)
        return cls(data)


class UInt32(Int32):
    """
    An unsigned version of :class:Int32.
    """
    _type = c_uint32

    def unsigned(self) -> 'UInt32':
        """
        Return a new instance representing the same bytes, but signed
        :return:
        """
        return self

    @property
    def unsigned_value(self) -> int:
        return self._val.value

    def shift_right_logical(self, ammount: Union['Int32', int]) -> 'UInt32':
        """
        see :meth:`Int32.shift_right_logical <Int32.shift_right_logical>`

        :param ammount: Number of positions to shift
        :return: A new Int32 object representing the shifted value (keeps the signed-ness of the source)
        """
        return self >> ammount
