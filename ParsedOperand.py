from utils import *
from ParametersComponent import *

def is_parsed_operand(obj):
    return isinstance(obj, ParsedOperand)

class ParsedOperand:
    def __init__(self, size):
        assert(is_int(size))
        assert(size in (8, 16, 32, 64))
        self.size = size

class ParsedOperand_Reg(ParsedOperand):
    def __init__(self, size):
        super().__init__(size)

    def __str__(self):
        return 'reg%d' % (self.size,)

    def parameters_component(self):
        return ParametersComponent_Reg(self.size)

class ParsedOperand_Reg8(ParsedOperand_Reg):
    def __init__(self):
        super().__init__(8)

class ParsedOperand_Reg16(ParsedOperand_Reg):
    def __init__(self):
        super().__init__(16)

class ParsedOperand_Reg32(ParsedOperand_Reg):
    def __init__(self):
        super().__init__(32)

class ParsedOperand_Reg64(ParsedOperand_Reg):
    def __init__(self):
        super().__init__(64)

class ParsedOperand_RegMem(ParsedOperand):
    def __init__(self, size):
        super().__init__(size)

    def __str__(self):
        return 'reg/mem%d' % (self.size,)

    def parameters_component(self):
        return ParametersComponent_ModRm_Abstract(self.size)

class ParsedOperand_RegMem8(ParsedOperand_RegMem):
    def __init__(self):
        super().__init__(8)

class ParsedOperand_RegMem16(ParsedOperand_RegMem):
    def __init__(self):
        super().__init__(16)

class ParsedOperand_RegMem32(ParsedOperand_RegMem):
    def __init__(self):
        super().__init__(32)

class ParsedOperand_RegMem64(ParsedOperand_RegMem):
    def __init__(self):
        super().__init__(64)

class ParsedOperands:
    def __init__(self, operands):
        assert(is_tuple(operands))
        for operand in operands:
            assert(is_parsed_operand(operand))
        self.operands = operands

    def __str__(self):
        return ', '.join([str(operand) for operand in self.operands])

    def parameters_components(self):
        result = []
        for operand in self.operands:
            result.append(operand.parameters_component())
        return ParametersComponents(tuple(result))

def parsed_operand(operand):
    m = {
        'reg8': ParsedOperand_Reg8,
        'reg16': ParsedOperand_Reg16,
        'reg32': ParsedOperand_Reg32,
        'reg64': ParsedOperand_Reg64,
        'reg/mem8': ParsedOperand_RegMem8,
        'reg/mem16': ParsedOperand_RegMem16,
        'reg/mem32': ParsedOperand_RegMem32,
        'reg/mem64': ParsedOperand_RegMem64,
    }
    if operand not in m:
        print('Error: Unknown instruction operand: %s' % (operand,))
        exit(1)
    return m[operand]()
