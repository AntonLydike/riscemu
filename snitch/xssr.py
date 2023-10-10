from riscemu.instructions.instruction_set import InstructionSet, Instruction

from .regs import StreamingRegs, StreamDef, StreamMode


class Xssr_pseudo(InstructionSet):
    def instruction_ssr_enable(self, ins: Instruction):
        self._stream.enabled = True

    def instruction_ssr_disable(self, ins: Instruction):
        self._stream.enabled = False

    def instruction_ssr_configure(self, ins: Instruction):
        dm = ins.get_imm(0).abs_value.value
        bound = ins.get_imm(1).abs_value.value
        stride = ins.get_imm(2).abs_value.value

        self._stream.dm_by_id[dm].bound = bound
        self._stream.dm_by_id[dm].stride = stride

    def instruction_ssr_read(self, ins: Instruction):
        base_pointer = ins.get_reg(0)
        dm = ins.get_imm(1).abs_value.value
        dim = ins.get_imm(2).abs_value.value

        self._stream.dm_by_id[dm].base = self.regs.get(base_pointer).value
        self._stream.dm_by_id[dm].dim = dim
        self._stream.dm_by_id[dm].mode = StreamMode.READ

    def instruction_ssr_write(self, ins: Instruction):
        base_pointer = ins.get_reg(0)
        dm = ins.get_imm(1).abs_value.value
        dim = ins.get_imm(2).abs_value.value

        self._stream.dm_by_id[dm].base = self.regs.get(base_pointer).value
        self._stream.dm_by_id[dm].dim = dim
        self._stream.dm_by_id[dm].mode = StreamMode.WRITE

    @property
    def _stream(self) -> StreamingRegs:
        return self.cpu.regs  # type: ignore
