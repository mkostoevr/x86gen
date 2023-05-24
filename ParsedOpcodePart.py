from utils import *
from OpcodeComponent import *

def is_opcode_part(obj):
    return isinstance(obj, ParsedOpcodePart)

class ParsedOpcodePart:
    def __eq__(self, other):
        return False

    def is_raw(self):
        return False

class ParsedOpcodePart_Byte(ParsedOpcodePart):
    def __init__(self, value):
        assert(is_int(value))
        assert(value >= 0 and value <= 255)
        self.value = value

    def __str__(self):
        return '%02x' % (self.value,)

    def is_raw(self):
        return True

class ParsedOpcodePart_ModRm(ParsedOpcodePart):
    def __init__(self):
        pass

    def __str__(self):
        return '/r'

    def __eq__(self, other):
        if is_str(other) and other == '/r':
            return True
        super().__eq__(other)

class ParsedOpcodePart_ModRmN(ParsedOpcodePart):
    def __init__(self, n):
        assert(n >= 0 and n <= 7)
        self.n = n

    def __str__(self):
        return '/%d' % (self.n,)

class ParsedOpcodeParts:
    def __init__(self, opcodes):
        assert(is_tuple(opcodes))
        for opcode in opcodes:
            assert(is_opcode_part(opcode))
        self.opcodes = opcodes

    def __str__(self):
        return ' '.join([str(opcode) for opcode in self.opcodes])

    def raw_part(self):
        result = []
        for opcode in self.opcodes:
            if opcode.is_raw():
                result.append(opcode.value)
            else:
                break
        return tuple(result)

    def modrm_sib_disp(self):
        if '/r' in self.opcodes:
            return OpcodeComponent_ModRmSibDisp_Abstract()
        else:
            return OpcodeComponent_ModRmSibDisp_Unexisting()
