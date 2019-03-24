import ast
import sys
from contextlib import redirect_stdout
from functools import partial
from itertools import chain

from arkhe.controller import Arkhe
from arkhe.lang.compiler import ParseError, Parser
from arkhe.utils import divide_sequence
from arkhe.vm import INSTR_TERM, Instr


class Text:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    UNDERLINE = "\033[4m"

    def __class_getitem__(cls, item):
        def wrapper(text, start, end=cls.ENDC, p=True):
            if p:
                print(f"{start}{text}{end}")
            else:
                return f"{start}{text}{end}"
        
        if item.endswith('_p'):
            p = False
            item = item.replace('_p', '')
        else:
            p = True
            
        if hasattr(cls, item.upper()):
            return partial(wrapper, start=getattr(cls, item.upper()), p=p)
        else:
            raise AttributeError()


class ADB:
    def __init__(self, stdout=sys.stdout):
        self.vm = Arkhe()
        self.parse = Parser()
        self.stdout = stdout
        self.evaled = 0

    def run(self, ps1=">>> "):
        Text["header"]("ADB session started")

        command = input(ps1).strip()
        while command != "q":
            self.run_cmd(command)
            command = input(ps1).strip()

    def run_cmd(self, command, stdout=None):
        with redirect_stdout(stdout or self.stdout):
            if command == "code":
                codesets = divide_sequence(self.vm.code, INSTR_TERM)
                for n, codeset in enumerate(codesets, 1):
                    codeset = Instr(codeset.pop(0), codeset)
                    if n < self.evaled:
                        Text["green"](f"{n}th instr (executed) -> {codeset}")
                    elif n == self.evaled:
                        Text["underline"](f"Last executed instr  -> {codeset}")
                    else:
                        Text["blue"](f"{n}th instr (pending)  -> {codeset}")
            elif command == "regs":
                allrs = set(self.vm.registers.items())
                useds = set(filter(lambda i: i[1], allrs))
                frees = allrs - useds

                print("Register states:")
                Text["blue"](f"\tTotal: {len(allrs)}")
                Text["warn"](f"\tUseds: {str(len(useds)).zfill(len(f'{len(allrs)}'))}")
                Text["green"](f"\tFrees: {len(frees)}")
                for reg, val in useds:
                    print(f"r{reg} = {val}")

            elif command.startswith("r") and command[1:].isnumeric():
                reg = command[1:]
                print(f"r{reg} = {self.vm.registers[int(reg)]}")

            elif command == "mem":
                total = len(self.vm.memory)
                nonzero = len([0 for chunk in self.vm.memory if chunk])
                zero = total - nonzero
                Text["blue"](f"Allocated memory: {total}")
                Text["warn"](f"Non-zero  memory: {nonzero}")
                Text["green"](f"Free      memory: {zero}")

            elif command == "counter":
                Text["green"](f"Counter: {self.vm.counter}")
            
            elif command == "symtable":
                for key, value in self.vm.symtable.items():
                    print(f"{Text['green_p'](key)}: {Text['blue_p'](value)}")
            
            elif "=" in command and command.startswith("sym"):
                target, value = [item.strip() for item in command.replace("sym ", "").split("=")]
                value = ast.literal_eval(value)
                self.vm.symtable[target] = value

            elif "=" in command and command.startswith("r"):
                target, value = [item.strip() for item in command.replace("r", "").split("=")]
                value = ast.literal_eval(value)
                self.vm.registers[target] = value
            
            elif command == "reset":
                self.vm = Arkhe()  # or reset counter, code, eqflag, memory, registers
                self.evaled = 0
            
            elif command.startswith("eval ") and command[5:].isnumeric():
                for _ in range(int(command[5:])):
                    self.vm.exc_instr()

                self.evaled += int(command[5:])
            else:
                try:
                    if ";" in command:
                        self.vm.code.extend(
                            chain.from_iterable(
                                self.parse(command) for command in command.split("; ")
                            )
                        )
                    else:
                        commands = self.parse(command)
                        self.vm.code.extend(commands)
                except ParseError as exc:
                    Text["fail"]("Last instruction couldn't parsed!")


if __name__ == "__main__":
    adb = ADB()
    adb.run()
