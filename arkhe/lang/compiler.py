from functools import partial
from itertools import chain

from lark import Transformer
from lark.exceptions import ParseError

from arkhe.lang.parser import get_parser
from arkhe.vm import Operation

b16 = partial(int, base=16)


class InvalidInstrSize(Exception):
    pass


class Base10(Transformer):
    def start(self, instrs):
        return list(chain.from_iterable(instrs))

    def instr(self, tokens):
        op = getattr(Operation, tokens.pop(0).upper()).value
        operands = list(map(b16, tokens))

        if len(operands) != 3:
            raise InvalidInstrSize(f"Expected: 1+3, Got: 1+{len(operands)}")

        return [op, *operands]


class Parser:
    def __init__(self):
        self.parser = get_parser()
        self.transformer = Base10()

    def __call__(self, code):
        return self.transformer.transform(self.parser.parse(code))


if __name__ == "__main__":
    parser = get_parser()
    transformer = Base10()
    code = """
    LOAD 00 01 F4
    LOAD 01 03 E8
    ADD 00 01 02 
    """
    tree = parser.parse(code)
    print(transformer.transform(tree))
