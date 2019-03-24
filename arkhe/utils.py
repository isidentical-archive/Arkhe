from copy import copy
from typing import List, Sequence

from arkhe.vm import INSTR_TERM, Operation


def divide_sequence(sequence: Sequence[int], terminator: int = 0) -> List[List[int]]:
    result, tmp = [], []
    for item in sequence:
        if item != terminator:
            tmp.append(item)

        else:
            result.append(copy(tmp))
            tmp.clear()

    return result


def create_instr(op, *operands):
    return [getattr(Operation, op.upper()).value, *operands, INSTR_TERM]
