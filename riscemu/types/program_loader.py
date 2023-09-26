import os
from abc import abstractmethod, ABC
from typing import Union, Iterator, List, ClassVar
from io import IOBase

from . import T_ParserOpts, Program


class ProgramLoader(ABC):
    """
    A program loader is always specific to a given source file. It is a place to store
    all state concerning the parsing and loading of that specific source file, including
    options.
    """

    is_binary: ClassVar[bool]

    def __init__(self, source_name: str, source: IOBase, options: T_ParserOpts):
        self.source_name = source_name
        self.source = source
        self.options = options
        self.filename = os.path.split(self.source_name)[-1]
        self.__post_init__()

    def __post_init__(self):
        pass

    @classmethod
    @abstractmethod
    def can_parse(cls, source_name: str) -> float:
        """
        Return confidence that the file located at source_path
        should be parsed and loaded by this loader
        :param source_name: the name of the input
        :return: the confidence that this file belongs to this parser in [0,1]
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls, argv: List[str]) -> [List[str], T_ParserOpts]:
        """
        parse command line args into an options dictionary

        :param argv: the command line args list
        :return: all remaining command line args and the parser options object
        """
        pass

    @classmethod
    def instantiate(
        cls, source_name: str, source: IOBase, options: T_ParserOpts
    ) -> "ProgramLoader":
        """
        Instantiate a loader for the given source file with the required arguments

        :param source_name: the path to the source file
        :param source: IO Object representing the source
        :param options: the parsed options (guaranteed to come from this classes get_options method).
        :return: An instance of a ProgramLoader for the specified source
        """
        return cls(source_name, source, options)

    @abstractmethod
    def parse(self) -> Union[Program, Iterator[Program]]:
        """

        :return:
        """
        pass
