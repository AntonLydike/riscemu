import argparse
import sys
from dataclasses import dataclass
from io import IOBase, RawIOBase, TextIOBase
from typing import Type, Dict, List, Optional, Union
import importlib_resources

from . import __version__, __copyright__
from .core import CPU, ProgramLoader, Program, UserModeCPU
from .instructions import InstructionSet, InstructionSetDict
from .config import RunConfig
from .helpers import FMT_GRAY, FMT_NONE
from .parser import AssemblyFileLoader
from .instructions.float_base import FloatArithBase


@dataclass
class RiscemuSource:
    name: str
    stream: Union[TextIOBase, RawIOBase]

    def get_score_for(self, loader: ProgramLoader) -> float:
        if loader.is_binary:
            if isinstance(self.stream, TextIOBase):
                return 0
        elif isinstance(self.stream, RawIOBase):
            return 0
        return loader.can_parse(self.name)


class RiscemuMain:
    """
    This represents the riscemu API exposed to other programs for better
    interoperability.
    """

    available_ins_sets: Dict[str, Type[InstructionSet]]
    available_file_loaders: List[Type[ProgramLoader]]

    cfg: Optional[RunConfig]
    cpu: Optional[CPU]

    input_files: List[Union[str, RiscemuSource]]
    selected_ins_sets: List[Type[InstructionSet]]

    def __init__(self, cfg: Optional[RunConfig] = None):
        self.available_ins_sets = dict()
        self.selected_ins_sets = []
        self.available_file_loaders = []
        self.cfg: Optional[RunConfig] = cfg
        self.cpu: Optional[CPU] = None
        self.input_files = []
        self.selected_ins_sets = []

    def instantiate_cpu(self):
        self.cpu = UserModeCPU(self.selected_ins_sets, self.cfg)
        self.configure_cpu()

    def configure_cpu(self):
        assert self.cfg is not None
        if isinstance(self.cpu, UserModeCPU) and self.cfg.stack_size != 0:
            self.cpu.setup_stack(self.cfg.stack_size)

    def register_all_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "files",
            metavar="file.asm",
            type=str,
            nargs="+",
            help="The assembly files to load, the last one will be run",
        )

        parser.add_argument(
            "--options",
            "-o",
            action=OptionStringAction,
            keys=(
                "disable_debug",
                "no_syscall_symbols",
                "fail_on_ex",
                "add_accept_imm",
                "unlimited_regs",
                "libc",
                "ignore_exit_code",
            ),
            help="""Toggle options. Available options are:
        disable_debug:        Disable ebreak instructions
        no_syscall_symbols:   Don't add symbols for SCALL_EXIT and others
        fail_on_ex:           If set, exceptions won't trigger the debugger
        add_accept_imm:       Accept "add rd, rs, imm" instruction (instead of addi)
        unlimited_regs:       Allow an unlimited number of registers
        libc:                 Load a libc-like runtime (for malloc, etc.)
        ignore_exit_code:     Don't exit with the programs exit code.""",
        )

        parser.add_argument(
            "--syscall-opts",
            "-so",
            action=OptionStringAction,
            keys=("fs_access", "disable_input"),
        )

        parser.add_argument(
            "--instruction-sets",
            "-is",
            action=OptionStringAction,
            help="Instruction sets to load, available are: {}. All are enabled by default".format(
                ", ".join(self.available_ins_sets)
            ),
            keys={k: True for k in self.available_ins_sets},
            omit_empty=True,
        )

        parser.add_argument(
            "--stack_size",
            type=int,
            help="Stack size of loaded programs, defaults to 8MB",
            nargs="?",
        )

        parser.add_argument(
            "--flen",
            type=int,
            help="hardware FLEN, either 32 or 64. Defaults to 64",
            nargs="?",
            default=64,
        )

        parser.add_argument(
            "-v",
            "--verbose",
            help="Verbosity level (can be used multiple times)",
            action="count",
            default=0,
        )

        parser.add_argument(
            "--interactive",
            help="Launch the interactive debugger instantly instead of loading any "
            "programs",
            action="store_true",
        )

        parser.add_argument(
            "--ignore-exit-code",
            help="Ignore exit code of the program and always return 0 if the program ran to completion.",
            action="store_true",
            default=False,
        )

    def register_all_isas(self):
        self.available_ins_sets.update(InstructionSetDict)

    def register_all_program_loaders(self):
        self.available_file_loaders.append(AssemblyFileLoader)

    def parse_argv(self, argv: List[str]):
        parser = argparse.ArgumentParser(
            description="RISC-V Userspace emulator",
            prog="riscemu",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        if "--version" in argv:
            print(
                "riscemu version {}\n{}\n\nAvailable ISA: {}".format(
                    __version__, __copyright__, ", ".join(self.available_ins_sets)
                )
            )
            sys.exit()

        self.register_all_arguments(parser)

        # parse argv
        args = parser.parse_args(argv)

        # add ins
        if not hasattr(args, "ins"):
            setattr(args, "ins", {k: True for k in self.available_ins_sets})

        if args.flen not in (32, 64):
            raise ValueError("Cannot have flen other than 32 or 64!")

        # create RunConfig
        self.cfg = self.create_config(args)

        # set input files
        self.input_files.extend(args.files)

        # get selected ins sets
        self.selected_ins_sets.extend(
            self.available_ins_sets[name]
            for name, selected in args.ins.items()
            if selected
        )

        # remove floating point isas if they do not meet the flen requirements
        for isa in tuple(self.selected_ins_sets):
            if issubclass(isa, FloatArithBase) and isa.flen > args.flen:
                self.selected_ins_sets.remove(isa)

        # if "use_libc" is given, attach libc to path
        if self.cfg.use_libc:
            self.add_libc_to_input_files()

    def add_libc_to_input_files(self):
        """
        This adds the provided riscemu libc to the programs runtime.
        """
        for file in importlib_resources.files("riscemu.libc").iterdir():
            if file.name.lower().endswith(".s"):
                source = RiscemuSource(file.name, file.open("r"))
                self.input_files.append(source)

    def create_config(self, args: argparse.Namespace) -> RunConfig:
        # create a RunConfig from the cli args
        cfg_dict = dict(
            stack_size=args.stack_size,
            debug_instruction=not args.options["disable_debug"],
            include_scall_symbols=not args.options["no_syscall_symbols"],
            debug_on_exception=not args.options["fail_on_ex"],
            add_accept_imm=args.options["add_accept_imm"],
            unlimited_registers=args.options["unlimited_regs"],
            scall_fs=args.syscall_opts["fs_access"],
            scall_input=not args.syscall_opts["disable_input"],
            verbosity=args.verbose,
            use_libc=args.options["libc"],
            ignore_exit_code=args.options["ignore_exit_code"],
            flen=args.flen,
        )
        for k, v in dict(cfg_dict).items():
            if v is None:
                del cfg_dict[k]

        return RunConfig(**cfg_dict)

    def load_programs(self):
        for path in self.input_files:
            max_bid = -1
            bidder = None
            # get best-fit loader:
            for loader in self.available_file_loaders:
                if isinstance(path, RiscemuSource):
                    score = path.get_score_for(loader)
                else:
                    score = loader.can_parse(path)

                if score > max_bid:
                    max_bid = score
                    bidder = loader
            if max_bid <= 0:
                raise RuntimeError(
                    f"Cannot load {path}! No loader for this file type available."
                )
            if isinstance(path, RiscemuSource):
                stream = path.stream
                source_name = path.name
            elif path == "-":
                stream: IOBase = sys.stdin
                source_name = "<stdin>"
            else:
                source_name = path
                stream: IOBase = open(path, "rb" if bidder.is_binary else "r")

            programs = bidder.instantiate(source_name, stream, {}).parse()
            if isinstance(programs, Program):
                programs = [programs]
            for p in programs:
                self.cpu.mmu.load_program(p)
            if self.cfg.verbosity > 2:
                print(
                    FMT_GRAY
                    + "[Startup] Loaded {} with loader {}".format(
                        source_name, bidder.__name__
                    )
                    + FMT_NONE
                )

    def run_from_cli(self, argv: List[str]):
        # register everything
        self.register_all_isas()
        self.register_all_program_loaders()

        # parse argv and set up cpu
        self.parse_argv(argv)
        self.instantiate_cpu()
        self.load_programs()

        if self.cfg.verbosity > 3:
            print(
                FMT_GRAY
                + "[Startup] Startup complete, the following sections were loaded"
            )
            for sec in self.cpu.mmu.sections:
                print("          {}".format(sec.debug_str()))
            print(FMT_NONE)
        # run the program
        self.cpu.launch(self.cfg.verbosity > 1)

    def run(self):
        """
        This assumes that these values were set externally:

         - available_file_loaders: A list of available file loaders.
           Can be set using .register_all_program_loaders()
         - cfg: The RunConfig object. Can be directly assigned to the attribute
         - input_files: A list of assembly files to load.
         - selected_ins_sets: A list of instruction sets the CPU should support.
        """
        assert self.cfg is not None, "self.cfg must be set before calling run()"
        assert self.selected_ins_sets, "self.selected_ins_sets cannot be empty"
        assert self.input_files, "self.input_files cannot be empty"

        if self.cfg.use_libc:
            self.add_libc_to_input_files()

        self.instantiate_cpu()
        self.load_programs()

        # run the program
        self.cpu.launch(self.cfg.verbosity > 1)


class OptionStringAction(argparse.Action):
    def __init__(self, option_strings, dest, keys=None, omit_empty=False, **kwargs):
        if keys is None:
            raise ValueError('must define "keys" argument')
        if isinstance(keys, dict):
            keys_d = keys
        elif isinstance(keys, (list, tuple)):
            keys_d = {}
            for k in keys:
                if isinstance(k, tuple):
                    k, v = k
                else:
                    v = False
                keys_d[k] = v
        else:
            keys_d = dict()
        super().__init__(option_strings, dest, default=keys_d, **kwargs)
        self.keys = keys_d
        self.omit_empty = omit_empty

    def __call__(self, parser, namespace, values, option_string=None):
        d = {}
        if not self.omit_empty:
            d.update(self.keys)
        for x in values.split(","):
            if x in self.keys:
                d[x] = True
            else:
                raise ValueError("Invalid parameter supplied: " + x)
        setattr(namespace, self.dest, d)
