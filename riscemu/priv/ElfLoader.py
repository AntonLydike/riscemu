from ..Executable import Executable, MemorySection, MemoryFlags

# This requires pyelftools package!

class ElfExecutable(Executable):
    def __init__(self, name):
        from elftools.elf.elffile import ELFFile

        with open(f)
