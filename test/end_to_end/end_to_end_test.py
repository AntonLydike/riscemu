import contextlib
import os
from abc import abstractmethod
from tempfile import NamedTemporaryFile
from typing import Optional, Union, Tuple
from unittest import TestCase

from riscemu import CPU, UserModeCPU, InstructionSetDict, RunConfig
from riscemu.types import Program


class EndToEndTest(TestCase):

    def __init__(self, cpu: Optional[CPU] = None):
        super().__init__()
        if cpu is None:
            cpu = UserModeCPU(InstructionSetDict.values(), RunConfig())
        self.cpu = cpu

    @abstractmethod
    def get_source(self) -> Tuple[str, Union[bytes, str, bytearray]]:
        """
        This method returns the source code of the program
        :return:
        """
        pass

    def test_run_program(self):
        """
        Runs the program and verifies output
        :return:
        """
        with self.with_source_file() as names:
            fname, orig_name = names
            loader = self.cpu.get_best_loader_for(fname)
            self.program = loader.instantiate(fname, loader.get_options([])).parse()
            self._change_program_file_name(self.program, orig_name)
            self.cpu.load_program(self.program)
            self.after_program_load(self.program)
            if isinstance(self.cpu, UserModeCPU):
                self.cpu.setup_stack()
            try:
                self.cpu.launch(self.program)
            except Exception as ex:
                if self.is_exception_expected(ex):
                    pass
                raise ex

    @contextlib.contextmanager
    def with_source_file(self):
        name, content = self.get_source()
        if isinstance(content, str):
            f = NamedTemporaryFile('w', suffix=name, delete=False)
        else:
            f = NamedTemporaryFile('wb', suffix=name, delete=False)
        f.write(content)
        f.flush()
        f.close()
        try:
            yield f.name, name
        finally:
            os.unlink(f.name)

    def after_program_load(self, program):
        pass

    def is_exception_expected(self, ex: Exception) -> bool:
        return False

    def _change_program_file_name(self, program: Program, new_name: str):
        program.name = new_name
        for sec in program.sections:
            sec.owner = new_name
