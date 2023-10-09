import struct
from ctypes import c_float, c_double
from typing import Union, Any, ClassVar, Type
from abc import ABC

bytes_t = bytes


class BaseFloat(ABC):
    __slots__ = ("_val",)

    _type: ClassVar[Type[Union[c_float, c_double]]]
    _struct_fmt_str: ClassVar[str]

    _val: Union[c_float, c_double]

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
        return struct.pack("<" + self._struct_fmt_str, self.value)

    @classmethod
    def from_bytes(cls, val: Union[bytes_t, bytearray]):
        return cls(val)

    def __init__(
        self, val: Union[float, c_float, "BaseFloat", bytes_t, bytearray, int] = 0
    ):
        if isinstance(val, (float, int)):
            self._val = self._type(val)
        elif isinstance(val, (c_float, c_double)):
            self._val = self._type(val.value)
        elif isinstance(val, (bytes, bytearray)):
            self._val = self._type(struct.unpack("<" + self._struct_fmt_str, val)[0])
        elif isinstance(val, self.__class__):
            self._val = val._val
        else:
            raise ValueError(
                "Unsupported value passed to {}: {} ({})".format(
                    self.__class__.__name__,
                    repr(val),
                    type(val),
                )
            )

    def __add__(self, other: Union["BaseFloat", float]):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value + other)

    def __sub__(self, other: Union["BaseFloat", float]):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value - other)

    def __mul__(self, other: Union["BaseFloat", float]):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value * other)

    def __truediv__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value / other)

    def __floordiv__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value // other)

    def __mod__(self, other: Union["BaseFloat", float]):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.__class__(self.value % other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (float, int)):
            return self.value == other
        elif isinstance(other, BaseFloat):
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

    def __hash__(self):
        return hash(self.value)

    def __gt__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.value > other

    def __lt__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.value < other

    def __le__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.value <= other

    def __ge__(self, other: Any):
        if isinstance(other, BaseFloat):
            other = other.value
        return self.value >= other

    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return self.value

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

    @classmethod
    def bitcast(cls, f: "BaseFloat") -> "BaseFloat":
        """
        bitcast the struct up or down to another type.
        Fills upper bits with zero.

        Use Float64.bitcast(Float32(...)) to bitcast a f32 to f64
        """
        if isinstance(f, cls):
            return f
        return cls.from_bytes(
            (b"\x00\x00\x00\x00\x00\x00\x00\x00" + f.bytes)[
                -struct.calcsize(cls._struct_fmt_str) :
            ]
        )

    @classmethod
    def flen_to_cls(cls, bits: int) -> Type["BaseFloat"]:
        if bits == 32:
            return Float32
        if bits == 64:
            return Float64
        raise ValueError(f"Unsupported flen: {bits}")

    def __format__(self, spec: str):
        if spec[-2:] == "32":
            return Float32.bitcast(self).__format__(spec[:-2])
        if spec[-2:] == "64":
            return Float64.bitcast(self).__format__(spec[:-2])
        return format(self.value, spec)


class Float32(BaseFloat):
    _type = c_float
    _struct_fmt_str = "f"


class Float64(BaseFloat):
    _type = c_double
    _struct_fmt_str = "d"
