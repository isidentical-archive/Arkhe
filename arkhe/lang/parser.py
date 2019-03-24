import textwrap

# from pathlib import Path
from lark import Lark

# GRAMMAR = Path(__file__).parent / "grammar.lark"
GRAMMAR = textwrap.dedent(
    """
start: instr+
instr: OP OPERAND+

OPERAND: HEXDIGIT~2..4

%import common.HEXDIGIT
%import common.CNAME -> OP
%import common.WS
%ignore WS
"""
)


def get_parser():
    # with open(GRAMMAR) as f:
    #    grammar = f.read()

    return Lark(GRAMMAR)
