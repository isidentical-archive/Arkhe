import os
import pytest

from io import StringIO
from arkhe.controller import Arkhe, RegisterNotFound, Registers
from arkhe.debugger import ADB
from arkhe.utils import create_instr, divide_sequence
from arkhe.vm import INSTR_TERM, Operation, TypeTable, MemoryFault

def test_utils_divideseq():
    data = [1, 2, 3, 0, 1, 2, 0, 1, 0, 1, 2, 3, 4, 5, 0]
    assert divide_sequence(data) == [[1, 2, 3], [1, 2], [1], [1, 2, 3, 4, 5]]


def test_utils_create_instr():
    assert create_instr("load", 0, 1, 244) == [
        Operation.LOAD.value,
        0,
        1,
        244,
        INSTR_TERM,
    ]


def test_register():
    registers = Registers(32)
    assert registers[0] == 0


def test_register_key_imm():
    registers = Registers(16)
    with pytest.raises(RegisterNotFound):
        registers[32] = 3


def test_register_set():
    registers = Registers(16)
    registers[5] = 15
    assert registers[5] == 15


def test_vm_load():
    code = create_instr("load", 0, 0, 100)
    vm = Arkhe(code)
    vm.eval()
    assert vm.registers[0] == 100


def test_vm_load_multiple():
    code = [*create_instr("load", 0, 3, 232), *create_instr("load", 1, 1, 244)]

    vm = Arkhe(code)
    vm.eval()
    assert vm.registers[0] == 1000 and vm.registers[1] == 500


def test_vm_math():
    code = [
        *create_instr("load", 0, 3, 232),
        *create_instr("load", 1, 1, 244),
        *create_instr("add", 0, 1, 2),
        *create_instr("sub", 2, 1, 3),
        *create_instr("mul", 1, 2, 4),
        *create_instr("truediv", 2, 3, 5),
    ]

    vm = Arkhe(code)
    vm.eval()
    assert (
        vm.registers[0] == 1000
        and vm.registers[1] == 500
        and vm.registers[2] == 1500
        and vm.registers[3] == 1000
        and vm.registers[4] == 750_000
        and vm.registers[5] == 1.5
    )


def test_vm_jmp():
    code = create_instr("jmp", 0)
    vm = Arkhe(code)
    vm.registers[0] = 0
    vm.exc_instr()
    assert vm.counter == 0


def test_vm_jmpf():
    code = [*create_instr("jmpf", 0), *create_instr("nop")]

    vm = Arkhe(code)
    vm.registers[0] = 4
    vm.exc_instr()  # counter at 3
    assert vm.counter == 7


def test_vm_jmpb():
    code = [*create_instr("jmpb", 0), *create_instr("nop")]

    vm = Arkhe(code)
    vm.registers[0] = 3
    vm.exc_instr()  # counter at 3
    assert vm.counter == 0


def test_vm_comp_eq():
    code = [*create_instr("eq", 0, 1), *create_instr("eq", 1, 2)]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert not vm._eqflag


def test_vm_comp_ne():
    code = [*create_instr("ne", 0, 1), *create_instr("ne", 1, 2)]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert not vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert vm._eqflag


def test_vm_comp_gt():
    code = [
        *create_instr("gt", 0, 1),
        *create_instr("gt", 1, 2),
        *create_instr("gt", 1, 3),
    ]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert not vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert not vm._eqflag
    vm.registers[3] = 4
    vm.exc_instr()
    assert vm._eqflag


def test_vm_comp_lt():
    code = [
        *create_instr("lt", 0, 1),
        *create_instr("lt", 1, 2),
        *create_instr("lt", 1, 3),
    ]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert not vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert vm._eqflag
    vm.registers[3] = 4
    vm.exc_instr()
    assert not vm._eqflag


def test_vm_comp_ge():
    code = [
        *create_instr("ge", 0, 1),
        *create_instr("ge", 1, 2),
        *create_instr("ge", 1, 3),
    ]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert not vm._eqflag
    vm.registers[3] = 4
    vm.exc_instr()
    assert vm._eqflag


def test_vm_comp_le():
    code = [
        *create_instr("le", 0, 1),
        *create_instr("le", 1, 2),
        *create_instr("le", 1, 3),
    ]
    vm = Arkhe(code)
    vm.registers[0] = 5
    vm.registers[1] = 5
    vm.exc_instr()
    assert vm._eqflag
    vm.registers[2] = 10
    vm.exc_instr()
    assert vm._eqflag
    vm.registers[3] = 4
    vm.exc_instr()
    assert not vm._eqflag


def test_vm_jeq():
    code = [*create_instr("jeq", 0)]
    vm = Arkhe(code)
    vm.registers[0] = 0
    vm._eqflag = True
    vm.exc_instr()
    assert vm.counter == 0
    vm._eqflag = False
    vm.exc_instr()
    assert vm.counter == 3


def test_vm_jne():
    code = [*create_instr("jne", 0)]
    vm = Arkhe(code)
    vm.registers[0] = 0
    vm._eqflag = False
    vm.exc_instr()
    assert vm.counter == 0
    vm._eqflag = True
    vm.exc_instr()
    assert vm.counter == 3

def test_vm_jfe():
    code = [*create_instr("jfe", 0)]
    vm = Arkhe(code)
    vm.registers[0] = 20
    vm._eqflag = True
    vm.exc_instr()
    assert vm.counter == 23


def test_vm_jfn():
    code = [*create_instr("jfn", 0)]
    vm = Arkhe(code)
    vm.registers[0] = 20
    vm._eqflag = False
    vm.exc_instr()
    assert vm.counter == 23
    
def test_vm_mem_alloc():
    code = create_instr("alloc", 0)
    vm = Arkhe(code)
    vm.registers[0] = 16
    vm.exc_instr()
    assert len(vm.memory) == 16
    vm.counter = 0
    vm.exc_instr()
    assert len(vm.memory) == 32


def test_vm_mem_dealloc():
    code = create_instr("dealloc", 0, 0)
    vm = Arkhe(code)
    vm.registers[0] = 16
    vm.memory.alloc(36)
    vm.exc_instr()
    assert len(vm.memory) == 20

def test_vm_mem_insert():
    code = create_instr("insert", 0, 1)
    vm = Arkhe(code)
    vm.registers[0] = 16
    vm.registers[1] = "hello"
    with pytest.raises(MemoryFault):
        vm.exc_instr()
    vm.memory.alloc(100)
    vm.counter = 0
    vm.exc_instr()
    assert vm.memory[16] == "hello"
    
def test_vm_mem_read():
    code = create_instr("read", 0, 1)
    vm = Arkhe(code)
    vm.registers[0] = 16
    with pytest.raises(MemoryFault):
        vm.exc_instr()
    vm.memory.alloc(100)
    vm.memory[16] = "hello"
    vm.counter = 0
    vm.exc_instr()
    assert vm.registers[1] == "hello"

def test_vm_sym_set():
    code = create_instr("symset", 0, 1)
    vm = Arkhe(code)
    vm.registers[0] = "age"
    vm.registers[1] = 15
    vm.exc_instr()
    assert vm.symtable["age"] == 15

def test_vm_sym_read():
    code = create_instr("symread", 0, 1)
    vm = Arkhe(code)
    vm.symtable["age"] = 15
    vm.registers[0] = "age"
    vm.exc_instr()
    assert vm.registers[1] == 15
    
def test_type_string():
    code = create_instr("load", 0, 104, 101, 108, 108, 111, TypeTable.STR)
    vm = Arkhe(code)
    vm.exc_instr()
    assert vm.registers[0] == "hello"
    vm.code.extend(create_instr("load", 1, 32, 119, 111, 114, 108, 100, 33, 32, TypeTable.STR))
    vm.exc_instr()
    assert vm.registers[1] == " world! "
    vm.code.extend(create_instr("add", 0, 1, 2))
    vm.exc_instr()
    assert vm.registers[2] == "hello world! "
    vm.registers[5] = 5
    vm.code.extend(create_instr("mul", 2, 5, 3))
    vm.exc_instr()
    assert vm.registers[3] == "hello world! hello world! hello world! hello world! hello world! "

def test_type_bytes():
    code = create_instr("load", 0, 104, 101, 108, 108, 111, TypeTable.BYT)
    vm = Arkhe(code)
    vm.exc_instr()
    assert vm.registers[0] == b"hello"
    
def test_ext_libc():
    code = create_instr("ccall", 0, 1)
    vm = Arkhe(code)
    vm.registers[0] = "getpid"
    vm.exc_instr()
    assert vm.registers[1] == os.getpid()

def test_debugger():
    stream = StringIO()
    adb = ADB(stream)
    adb.run_cmd("LOAD 00 00 04; LOAD 01 01 F4; MUL 00 01 02")
    adb.run_cmd("eval 2")
    assert adb.vm.counter == 10
    assert adb.vm.registers[0] == 4 and adb.vm.registers[1] == 500
    assert adb.vm.registers[2] == 0
    adb.run_cmd("eval 1")
    assert adb.vm.registers[2] == 2000
