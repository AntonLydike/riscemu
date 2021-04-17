from dataclasses import dataclass

@dataclass()
class RunConfig:
    color = True
    preffered_stack_size = None
    debug_instruction = True

