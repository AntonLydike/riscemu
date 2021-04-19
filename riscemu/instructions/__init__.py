from .InstructionSet import InstructionSet
from .RV32M import RV32M
from .RV32I import RV32I

InstructionSetDict = {
    v.__name__: v for v in [RV32I, RV32M]
}
