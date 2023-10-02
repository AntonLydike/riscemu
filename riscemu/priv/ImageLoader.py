"""
Loads a memory image with debug information into memory
"""

import os.path
from io import IOBase
from typing import List, Iterable

from .ElfLoader import ElfMemorySection
from .types import MemoryImageDebugInfos
from ..assembler import INSTRUCTION_SECTION_NAMES
from ..colors import FMT_NONE, FMT_PARSE
from ..core import MemoryFlags, ProgramLoader, Program, T_ParserOpts


class MemoryImageLoader(ProgramLoader):
    is_binary = True

    @classmethod
    def can_parse(cls, source_name: str) -> float:
        if source_name.split(".")[-1] == "img":
            return 1
        return 0

    @classmethod
    def get_options(cls, argv: List[str]) -> [List[str], T_ParserOpts]:
        return argv, {}

    def parse(self) -> Iterable[Program]:
        if "debug" not in self.options:
            yield self.parse_no_debug()
            return

        with open(self.options.get("debug"), "r") as debug_file:
            debug_info = MemoryImageDebugInfos.load(debug_file.read())

        with self.source as source_file:
            data: bytearray = bytearray(source_file.read())

        for name, sections in debug_info.sections.items():
            program = Program(name)

            for sec_name, (start, size) in sections.items():
                if program.base is None:
                    program.base = start

                # in_code_sec = get_section_base_name(sec_name) in INSTRUCTION_SECTION_NAMES
                program.add_section(
                    ElfMemorySection(
                        data[start : start + size],
                        sec_name,
                        program.context,
                        name,
                        start,
                        MemoryFlags(False, True),
                    )
                )

            program.context.labels.update(debug_info.symbols.get(name, dict()))
            program.global_labels.update(debug_info.globals.get(name, set()))

            yield program

    def parse_no_debug(self) -> Program:
        print(
            FMT_PARSE
            + "[MemoryImageLoader] Warning: loading memory image without debug information!"
            + FMT_NONE
        )

        with self.source as source_file:
            data: bytes = source_file.read()

        p = Program(self.filename)
        p.add_section(
            ElfMemorySection(
                bytearray(data), ".text", p.context, p.name, 0, MemoryFlags(False, True)
            )
        )
        return p

    @classmethod
    def instantiate(
        cls, source_name: str, source: IOBase, options: T_ParserOpts
    ) -> "ProgramLoader":
        if os.path.isfile(source_name + ".dbg"):
            return MemoryImageLoader(
                source_name, source, dict(**options, debug=source_name + ".dbg")
            )
        return MemoryImageLoader(source_name, source, options)
