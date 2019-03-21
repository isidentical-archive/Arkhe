from dataclasses import dataclass
from typing import Any, Sequence
from operations import MACHINE, Operation, InvalidOpcode
    
@dataclass
class Register:
    value: Any

    @classmethod
    def start(cls, amount):
        return [Register(0) for _ in range(amount)]
    
class Instr:
    def __init__(self, opcode, *operands):
        try:
            self.opcode = Operation(opcode)
        except ValueError as exc:
            raise InvalidOpcode(f"The {opcode} doesnt match with any operation in Operation table") from exc
        
        self.operands = operands
        
class Arkhe:
    def __init__(
        self, 
        code: Sequence[int], 
        total_regs: int = 32, 
        counter_start: int = 0
    ):
        self.registers = Register.start(total_regs)
        self.counter = counter_start
        self.code = code            
    
    def eval(self):
        code_length = len(self.code)
        while self.counter < code_length:
            self.dispatch(self.next_instr())
            
    def next_instr(self):
        instr = Instr(*self.code[self.counter:self.counter+4])
        self.counter += 4
        return instr
    
    def dispatch(self, instr: Instr):
        return MACHINE.get(instr.opcode)(self, instr)
        
arkhe = Arkhe([
    0, 0, 0, 0,
    1, 0, 1, 244,
    1, 1, 1, 244,
    2, 0, 1, 2,
    3, 2, 1, 3,
    4, 1, 2, 4,
    5, 3, 2, 5, 
])
arkhe.eval()
from pprint import pprint
pprint(arkhe.registers)
