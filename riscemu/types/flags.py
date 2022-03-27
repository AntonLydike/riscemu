from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryFlags:
    read_only: bool
    executable: bool

    def __repr__(self):
        return "r{}{}".format(
            '-' if self.read_only else 'w',
            'x' if self.executable else '-'
        )
