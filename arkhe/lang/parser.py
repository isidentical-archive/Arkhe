from pathlib import Path

from lark import Lark

GRAMMAR = Path(__file__).parent / "grammar.lark"


def get_parser():
    with open(GRAMMAR) as f:
        grammar = f.read()

    return Lark(grammar)
