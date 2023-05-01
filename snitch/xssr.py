from riscemu.instructions.instruction_set import InstructionSet, Instruction

from .regs import StreamingRegs, StreamDef, StreamMode


class RV32_Xssr_pseudo(InstructionSet):
    def instruction_ssr_enable(self, ins: Instruction):
        self._stream.enabled = True

    def instruction_ssr_disable(self, ins: Instruction):
        self._stream.streams = dict()
        self._stream.enabled = False

    def instruction_ssr_setup_1d(self, ins: Instruction):
        """
        semantics:
        ssr.setup.1d rd, base_reg, len, stride, mode(flag,R/W/RW)
        (all as regs except mode)
        """
        print(ins)
        assert len(ins.args) == 5
        base, size, stride = (
            self.regs.get(ins.get_reg(i)) for i in range(1, 4)
        )
        rd_name = ins.get_reg(0)
        mode = ins.args[4]
        assert mode == 'R'

        self._stream.streams[rd_name] = StreamDef(
            base, size, stride, StreamMode.READ, 1
        )

        print("Created stream def: {}".format(self._stream.streams[rd_name]))

    @property
    def _stream(self) -> StreamingRegs:
        return self.cpu.regs  #type: ignore