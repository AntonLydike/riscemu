from riscemu import RunConfig
from riscemu.types import InstructionMemorySection, SimpleInstruction, Program

if __name__ == '__main__':
    from .CPU import UserModeCPU
    from .instructions import InstructionSetDict
    from .debug import launch_debug_session

    cpu = UserModeCPU(list(InstructionSetDict.values()), RunConfig(verbosity=4))

    program = Program('interactive session', base=0x100)
    context = program.context
    program.add_section(InstructionMemorySection([
        SimpleInstruction('ebreak', (), context, 0x100),
        SimpleInstruction('addi', ('a0', 'zero', '0'), context, 0x104),
        SimpleInstruction('addi', ('a7', 'zero', '93'), context, 0x108),
        SimpleInstruction('scall', (), context, 0x10C),
    ], '.text', context, program.name, 0x100))

    cpu.load_program(program)

    cpu.setup_stack()

    cpu.launch(program)
