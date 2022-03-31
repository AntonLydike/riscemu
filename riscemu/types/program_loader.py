import os
from abc import abstractmethod, ABC
from typing import Union, Iterator, List

from . import T_ParserOpts, Program


class ProgramLoader(ABC):
    """
    A program loader is always specific to a given source file. It is a place to store all state
    concerning the parsing and loading of that specific source file, including options.
    """

    def __init__(self, source_path: str, options: T_ParserOpts):
        self.source_path = source_path
        self.options = options
        self.filename = os.path.split(self.source_path)[-1]

    @classmethod
    @abstractmethod
    def can_parse(cls, source_path: str) -> float:
        """
        Return confidence that the file located at source_path
        should be parsed and loaded by this loader
        :param source_path: the path of the source file
        :return: the confidence that this file belongs to this parser
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls, argv: list[str]) -> [List[str], T_ParserOpts]:
        """
        parse command line args into an options dictionary

        :param argv: the command line args list
        :return: all remaining command line args and the parser options object
        """
        pass

    @classmethod
    def instantiate(cls, source_path: str, options: T_ParserOpts) -> 'ProgramLoader':
        """
        Instantiate a loader for the given source file with the required arguments

        :param source_path: the path to the source file
        :param options: the parsed options (guaranteed to come from this classes get_options method.
        :return: An instance of a ProgramLoader for the spcified source
        """
        return cls(source_path, options)

    @abstractmethod
    def parse(self) -> Union[Program, Iterator[Program]]:
        """

        :return:
        """
        pass
