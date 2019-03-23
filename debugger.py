from arkhe import Arkhe
from functools import partial

b16 = partial(int, base=16)
class ADB:
    def __init__(self):
        self.vm = Arkhe([])
        self.history = []
        
    def run(self, ps1 = ">>> "):
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
            else:
                commands = command.split(" ")
                try:
                    commands = map(b16, commands)
                except ValueError:
                    print(f"Given commands couldn't converted to base-10 from base-16.")
                self.vm.code.extend(commands)
                self.vm.exc_instr()
                
            self.history.append(command)
            command = input(ps1).strip()
        
if __name__ == '__main__':
    adb = ADB()
    adb.run()
