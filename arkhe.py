import itertools
from collections import UserDict
from vm import VM, Operation, ArkheException

class RegisterNotFound(ArkheException):
    pass

class Registers(UserDict):
    def __init__(self, amount=32):
        self.data = dict(zip(range(amount), itertools.repeat(0, amount)))

    def __setitem__(self, register, value):
        if self.get(register) is None:
            raise RegisterNotFound(f"{register}")
        return super().__setitem__(register, value)


class Arkhe:
    def __init__(self, code):
        self.code = code

        self.registers = Registers(32)
        self.counter = 0

        self.machine = VM(self)

    def eval(self):
        eta = len(self.code)
        while self.counter < eta:
            self.exc_instr()
            
    def exc_instr(self):
        return self.machine.dispatch(self.next_instr())

    def next_instr(self):
        instr = Operation(self.code[self.counter])
        self.counter += 1
        return instr

    def get_next_8(self):
        res = self.code[self.counter]
        self.counter += 1
        return res

    def get_next_16(self):
        res = (self.code[self.counter] << 8) | self.code[self.counter + 1]
        self.counter += 2
        return res
    
    def __repr__(self):
        return f"Arkhe at {self.counter}"
