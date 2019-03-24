import itertools
from collections import UserDict, UserList

from arkhe.vm import VM, ArkheException, Instr, Operation


class RegisterNotFound(ArkheException):
    pass


class Registers(UserDict):
    def __init__(self, amount=32):
        self.data = dict(zip(range(amount), itertools.repeat(0, amount)))

    def __setitem__(self, register, value):
        if self.get(register) is None:
            raise RegisterNotFound(f"{register}")
        return super().__setitem__(register, value)


class Memory(UserList):
    def alloc(self, amount):
        self.data.extend(itertools.repeat(0, amount))


class Arkhe:
    def __init__(self, code):
        self.code = code

        self.registers = Registers(32)
        self.counter = 0
        self.memory = Memory()
        self._eqflag = False

        self.machine = VM(self)

    def eval(self):
        eta = len(self.code)
        while self.counter < eta:
            self.exc_instr()

    def exc_instr(self):
        return self.machine.dispatch(self.next_instr())

    def next_instr(self):
        operation = Operation(self.code[self.counter])
        operands = self.code[self.counter + 1 : self.counter + 4]
        self.counter += 4
        return Instr(operation, operands)

    def __repr__(self):
        return f"Arkhe at {self.counter}"
