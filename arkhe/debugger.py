from arkhe.controller import Arkhe
from arkhe.lang.compiler import Parser, ParseError


class ADB:
    def __init__(self):
        self.vm = Arkhe([])
        self.parse = Parser()
        self.history = []

    def run(self, ps1=">>> "):
        print("ADB session started")

        command = input(ps1).strip()
        while command != "q":
            if command == "h":
                for n, cmd in enumerate(self.history):
                    print(f"{n} -> {cmd}")
            elif command == "c":
                for cmd in self.vm.code:
                    print(cmd)
            elif command == "r":
                allrs = set(self.vm.registers.items())
                useds = set(filter(lambda i: i[1], allrs))
                frees = allrs - useds

                print("Register states:")
                print(f"\tTotal: {len(allrs)}")
                print(f"\tUseds: {len(useds)}")
                print(f"\tFree: {len(frees)}")
                for reg, val in useds:
                    print(f"r{reg} = {val}")
            elif command.startswith("r") and command[1:].isnumeric():
                reg = command[1:]
                print(f"r{reg} = {self.vm.registers[int(reg)]}")
            elif command == "m":
                print(f"Allocated memory: {len(self.vm.memory)}")
            else:
                try:
                    commands = self.parse(command)
                    self.vm.code.extend(commands)
                    self.vm.exc_instr()
                except ParseError:
                    print("Last instruction couldn't parsed!")

            self.history.append(command)
            command = input(ps1).strip()


if __name__ == "__main__":
    adb = ADB()
    adb.run()
