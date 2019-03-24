import itertools
from collections import UserDict, UserList
from functools import partial

from arkhe.vm import INSTR_TERM, VM, ArkheException, Instr, Operation


class RegisterNotFound(ArkheException):
    pass


class InstrNotEnded(ArkheException):
    pass


class Registers(UserDict):
    def __init__(self, amount=32):
        self.data = dict(zip(range(amount), itertools.repeat(0, amount)))

    def __setitem__(self, register, value):
        if self.get(register) is None:
            raise RegisterNotFound(f"{register}")
        return super().__setitem__(register, value)

class Symtable(UserDict):
    pass
    
class Memory(UserList):
    def alloc(self, amount):
        self.data.extend(itertools.repeat(0, amount))

    def dealloc(self, amount, head):
        p = partial(self.data.pop, 0 if head else -1)
        for _ in range(amount):
            p()


class Arkhe:
    def __init__(self, code=None):
        self.code = code or []

        self.registers = Registers(32)
        self.memory = Memory()
        self.symtable = Symtable()
        self.machine = VM(self)
        
        self.counter = 0
        self._eqflag = False


    def eval(self):
        eta = len(self.code)
        while self.counter < eta:
            self.exc_instr()

    def exc_instr(self):
        instr = self.next_instr()
        return self.machine.dispatch(instr)

    def next_instr(self):
        operation = Operation(self.code[self.counter])
        self.counter += 1

        operands = []
        for item in self.code[self.counter :]:
            if item != INSTR_TERM:
                operands.append(item)
            else:
                break
        else:
            raise InstrNotEnded()

        self.counter += len(operands) + 1
        return Instr(operation, operands)

    def __repr__(self):
        return f"Arkhe at {self.counter}"
