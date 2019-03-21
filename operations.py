import operator
from enum import IntEnum

class InvalidOpcode(Exception):
    pass
    
class Operation(IntEnum):
    HLT  = 0
    LOAD = 1
    ADD  = 2
    SUB  = 3
    MUL  = 4
    TRUEDIV  = 5
    
MACHINE = {}

def process(instr):
    def wrapper(f):
        MACHINE[instr] = f
        return f
    return wrapper
    
@process(Operation.HLT)
def hlt(vm, instr):
    print('HLT')
    
@process(Operation.LOAD)
def load(vm, instr):
    register = instr.operands[0]
    value = (instr.operands[1] << 8) | instr.operands[2]
    vm.registers[register].value = value

@process(Operation.ADD)
@process(Operation.SUB)
@process(Operation.MUL)
@process(Operation.TRUEDIV)
def math(vm, instr):
    r1 = vm.registers[instr.operands[0]].value
    r2 = vm.registers[instr.operands[1]].value
    vm.registers[instr.operands[2]].value = getattr(operator, instr.opcode.name.lower())(r1, r2)
    
