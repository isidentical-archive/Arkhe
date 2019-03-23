from lark import Lark
from pathlib import Path

GRAMMAR = Path(__file__).parent / "grammar.lark" 

def get_parser():
    with open(GRAMMAR) as f:
        grammar = f.read()
    
    return Lark(grammar)
