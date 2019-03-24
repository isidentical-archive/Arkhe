# Arkhe
Experimental Universal Virtual Machine (`pip install arkhe`) (`python -m arkhe`)
## Demo
[![asciicast](https://asciinema.org/a/ILB4AeuGsPpVspaCKnIziayiJ.svg)](https://asciinema.org/a/ILB4AeuGsPpVspaCKnIziayiJ)

## Usage
### Type
Check out `arkhe.vm.TypeTable`
### Load
```
LOAD REGISTER OPERANDS+ TYPE?
```
Type is optional and int by default. 
#### Integer Loading
Takes 2 operands, maximum 2^16
```
(operand1 << 8) | operand2
```
#### String Loading
Takes n operands as hex. 
### Math
```
{OPERATION} R1 R2 TARGET
```
=
```
TARGET_REG = R1 {OPERATION} R2
```

- ADD
- SUB
- MUL
- TRUEDIV

Mapped from python's `operator` module. 
### JUMP
#### Absolute Jump
```
JMP R1
```
Set counter to given register's value
#### Relative Jump
```
JMP{F/B} R1
```
F for forward, B for backward. Increment or decrement counter's value by R1's value
### Comparison
#### Basic
```
{OPERATION} R1 R2
```
Sets `_eqflag` of `Arkhe` instance to the result of given operation. Mapped directly from `operators` library

- EQ
- NE
- LT
- GT
- GE
- LE
#### Jump
```
JEQ R1
JNQ R1
```
JEQ: Set counter to R1's value if `_eqflag` is True
JNQ: Set counter to R1's value if `_eqflag` is False
### Memory
```
ALLOC R1
DEALLOC R1 0/1
```
ALLOC: Allocates memory amount of R1
DEALLOC: Deallocates memory amount of R1 from Head (1) or Tail (0)
### NOP / HLT
NOP does nothing, HLT raises `arkhe.vm.HLT` exception.
