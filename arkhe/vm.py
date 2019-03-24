"""
Reserveds:
0xFF{o} family reserved for VM
0xFE{o} family reserved for no action & hlt instrs
0xFD{o} family reserved for loading const types
"""
import operator
from contextlib import suppress
from dataclasses import dataclass
from enum import IntEnum
from typing import List

INSTR_TERM = 0xFFF


class ArkheException(Exception):
    pass


class HLT(ArkheException):
    def __init__(self):
        super().__init__("Program stopped!")


class InsufficientOperands(ArkheException):
    pass


class MemoryFault(ArkheException):
    pass

class UnknownSymbol(ArkheException):
    pass

class TypeTable(IntEnum):
    INT = 0xFD0
    STR = 0xFD1
    
    

class Operation(IntEnum):
    LOAD = 0
    ADD = 1
    SUB = 2
    MUL = 3
    TRUEDIV = 4
    JMP = 5
    JMPF = 6
    JMPB = 7
    EQ = 8
    NE = 9
    GT = 10
    LT = 11
    GE = 12
    LE = 13
    JEQ = 14
    JNE = 15
    ALLOC = 16
    DEALLOC = 17
    INSERT = 18
    READ = 19
    SYMSET = 20
    SYMREAD = 21
    NOP = 0xFEE
    HLT = 0xFEF

    def __repr__(self):
        return self.name.capitalize().ljust(7)


@dataclass
class Instr:
    operation: Operation
    operands: List[int]

    def __post_init__(self):
        self.op = 0
        if not isinstance(self.operation, Operation):
            self.operation = Operation(self.operation)

    def get_8(self):
        try:
            res = self.operands[self.op]
        except IndexError:
            raise InsufficientOperands()

        self.op += 1
        return res

    def get_16(self):
        return (self.get_8() << 8) | self.get_8()

    def __hash__(self):
        """unsafe_hash parameter has different functionality"""
        return hash(id(self))


class VM:
    instrset = {}

    def __init__(self, arkhe):
        self.arkhe = arkhe

    @classmethod
    def instr(cls, instr):
        def wrapper(f):
            cls.instrset[instr] = f
            return f

        return wrapper

    def dispatch(self, instr):
        return self.instrset.get(instr.operation)(self.arkhe, instr)


@VM.instr(Operation.LOAD)
def load(vm, instr):
    target = instr.get_8()
    try:
        typed = TypeTable(instr.operands[-1])
    except ValueError:
        typed = TypeTable.INT
    
    if typed is TypeTable.INT:
        value = instr.get_16()
    elif typed is TypeTable.STR:
        value = "".join(map(chr, instr.operands[1:-1]))

    vm.registers[target] = value


@VM.instr(Operation.ADD)
@VM.instr(Operation.SUB)
@VM.instr(Operation.MUL)
@VM.instr(Operation.TRUEDIV)
def math(vm, instr):
    operand1 = vm.registers[instr.get_8()]
    operand2 = vm.registers[instr.get_8()]
    vm.registers[instr.get_8()] = getattr(operator, instr.operation.name.lower())(
        operand1, operand2
    )


@VM.instr(Operation.EQ)
@VM.instr(Operation.NE)
@VM.instr(Operation.LE)
@VM.instr(Operation.GE)
@VM.instr(Operation.GT)
@VM.instr(Operation.LT)
def comparison(vm, instr):
    operand1 = vm.registers[instr.get_8()]
    operand2 = vm.registers[instr.get_8()]
    vm._eqflag = getattr(operator, instr.operation.name.lower())(operand1, operand2)


@VM.instr(Operation.JMP)
def jmp(vm, instr):
    vm.counter = vm.registers[instr.get_8()]


@VM.instr(Operation.JMPF)
def jmp_forward(vm, instr):
    value = vm.registers[instr.get_8()]
    vm.counter += value


@VM.instr(Operation.JMPB)
def jmp_backward(vm, instr):
    value = vm.registers[instr.get_8()]
    vm.counter -= value


@VM.instr(Operation.JEQ)
def jmp_ifeq(vm, instr):
    value = vm.registers[instr.get_8()]
    if vm._eqflag:
        vm.counter = value


@VM.instr(Operation.JNE)
def jmp_ifne(vm, instr):
    value = vm.registers[instr.get_8()]
    if not vm._eqflag:
        vm.counter = value


@VM.instr(Operation.ALLOC)
def mem_alloc(vm, instr):
    value = vm.registers[instr.get_8()]
    vm.memory.alloc(value)


@VM.instr(Operation.DEALLOC)
def mem_dealloc(vm, instr):
    head = instr.get_8()
    vm.memory.dealloc(vm.registers[instr.get_8()], head=head)


@VM.instr(Operation.INSERT)
def mem_insert(vm, instr):
    position = vm.registers[instr.get_8()]
    value = vm.registers[instr.get_8()]
    try:
        vm.memory[position] = value
    except IndexError:
        raise MemoryFault("Insert operation to not owned area!")


@VM.instr(Operation.READ)
def mem_read(vm, instr):
    position = vm.registers[instr.get_8()]
    try:
        vm.registers[instr.get_8()] = vm.memory[position]
    except IndexError:
        raise MemoryFault("Read operation to not owned area!")

@VM.instr(Operation.SYMSET)
def sym_set(vm, instr):
    name = vm.registers[instr.get_8()]
    value = vm.registers[instr.get_8()]
    vm.symtable[name] = value

@VM.instr(Operation.SYMREAD)
def sym_read(vm, instr):
    name = vm.registers[instr.get_8()]
    try:
        vm.registers[instr.get_8()] = vm.symtable[name]
    except KeyError:
        raise UnknownSymbol(f"{name}")
        
@VM.instr(Operation.NOP)
def nop(vm, instr):
    pass


@VM.instr(Operation.HLT)
def hlt(vm, instr):
    raise HLT()
