from dataclasses import dataclass, replace
from constants import *
from utils import *

# Instruction ##################################################################

OP_REG = gen_id()
OP_REGMEM = gen_id()
OP_REGMEM_REG = gen_id()
OP_REGMEM_ATREG = gen_id()
OP_REGMEM_ATREGPLUSDISP8 = gen_id()
OP_REGMEM_ATREGPLUSDISP32 = gen_id()
OP_REGMEM_ATSIB = gen_id()
OP_REGMEM_ATSIBPLUSDISP8 = gen_id()
OP_REGMEM_ATSIBPLUSDISP32 = gen_id()
OP_REGMEM_ATDISP32 = gen_id()
OP_REGMEM_ATRIPPLUSDISP32 = gen_id()
OP_MOFFSET = gen_id()
OP_SPECREG = gen_id()
OP_SPECSEGREG = gen_id()
OP_SEGREG = gen_id()
OP_IMM = gen_id()

operand_kind_specified_regmems = set((
    OP_REGMEM_REG,
    OP_REGMEM_ATREG,
    OP_REGMEM_ATREGPLUSDISP8,
    OP_REGMEM_ATREGPLUSDISP32,
    OP_REGMEM_ATSIB,
    OP_REGMEM_ATSIBPLUSDISP8,
    OP_REGMEM_ATSIBPLUSDISP32,
    OP_REGMEM_ATDISP32,
    OP_REGMEM_ATRIPPLUSDISP32,
))

operand_kind = operand_kind_specified_regmems | set((
    OP_REG,
    OP_REGMEM,
    OP_MOFFSET,
    OP_SPECREG,
    OP_SPECSEGREG,
    OP_SEGREG,
    OP_IMM,
))

class Instruction_Operand:
    def __init__(self, kind, contents, size, signed = None, mem_size = None):
        assert(kind in operand_kind)
        self.kind = kind
        # The operand contents in the mnemonic.
        self.contents = contents
        # Size of the operand (size of the destination if the operand is a pointer).
        self.size = size
        # Only for OP_IMM: is the immediate signed.
        self.signed = signed
        # Only for OP_REGMEM: separated size of the memory destination.
        self.mem_size = mem_size if mem_size != None else size

    def dup_specialized_modrm(self, new_kind):
        assert(isinstance(self, Instruction_Operand))
        assert(new_kind in operand_kind_specified_regmems)
        return Instruction_Operand(new_kind, self.contents, self.size, self.signed, self.mem_size)

    def stringify(self, native_size = 0):
        if self.kind in (OP_REG, OP_REGMEM_REG,):
            return 'reg%d' % (self.size,)
        elif self.kind == OP_REGMEM:
            if self.size == self.mem_size:
                return 'reg/mem%d' % (self.size,)
            else:
                return 'reg%d/mem%d' % (self.size, self.mem_size,)
        elif self.kind == OP_REGMEM_ATREG:
            return '%s[reg%d]' % (size_to_word(self.mem_size), native_size)
        elif self.kind == OP_REGMEM_ATREGPLUSDISP8:
            return '%s[reg%d + disp8]' % (size_to_word(self.mem_size), native_size,)
        elif self.kind == OP_REGMEM_ATREGPLUSDISP32:
            return '%s[reg%d + disp32]' % (size_to_word(self.mem_size), native_size,)
        elif self.kind == OP_REGMEM_ATDISP32:
            return '%s[disp32]' % (size_to_word(self.mem_size),)
        elif self.kind == OP_REGMEM_ATRIPPLUSDISP32:
            return '%s[rIP + disp32]' % (size_to_word(self.mem_size),)
        elif self.kind == OP_REGMEM_ATSIB:
            return '%s[reg%d + reg%d * scale]' % (size_to_word(self.mem_size), native_size, native_size,)
        elif self.kind == OP_REGMEM_ATSIBPLUSDISP8:
            return '%s[reg%d + reg%d * scale + disp8]' % (size_to_word(self.mem_size), native_size, native_size,)
        elif self.kind == OP_REGMEM_ATSIBPLUSDISP32:
            return '%s[reg%d + reg%d * scale + disp32]' % (size_to_word(self.mem_size), native_size, native_size,)
        elif self.kind == OP_MOFFSET:
            return '%s[disp%d]' % (size_to_word(self.size), native_size)
        elif self.kind == OP_IMM:
            return 'imm%d' % (self.size,)
        elif self.kind in (OP_SPECREG, OP_SPECSEGREG,):
            return self.contents.lower()
        elif self.kind == OP_SEGREG:
            return 'segreg'
        else:
            raise Exception('Unknown operand kind: %s' % (self.kind,))

    def __str__(self):
        return self.stringify()

@dataclass
class Instruction_OpcodeInfo:
    opcodes: tuple
    opcode_plus_reg: bool = False
    modrm: bool = False
    modrm_mod: int = None
    modrm_reg: int = None
    modrm_rm: int = None
    sib: bool = False
    sib_scale: int = None
    sib_index: int = None
    sib_base: int = None
    disp_size: int = None
    imm_size: int = None
    prefix_operand_size_override: bool = False
    prefix_rex: bool = False
    prefix_rex_w: bool = False

    def dup_specialize_modrm(self, mod = None, rm = None, sib = False, disp = None):
        assert(self.modrm == True)
        assert(self.modrm_mod == None)
        assert(self.modrm_rm == None)
        assert(self.sib == False)
        assert(self.disp_size == None)
        return replace(
            self,
            modrm_mod = mod,
            modrm_rm = rm,
            sib = sib,
            disp_size = disp,
        )

    def dup_add_prefixes(self, operand_size_override, rex_w):
        return replace(
            self,
            prefix_operand_size_override = operand_size_override,
            prefix_rex_w = rex_w,
            prefix_rex = any((rex_w,)),
        )

    def __str__(self):
        result = ''
        if self.prefix_operand_size_override:
            result += '66 '
        if self.prefix_rex:
            result += 'REX(%d) ' % (
                1 if self.prefix_rex_w else 0,
            )
        result += ' '.join(self.opcodes)
        result += '+r' if self.opcode_plus_reg else ''
        if self.modrm:
            result += ' ModRM(%s, %s, %s)' % (
                str(self.modrm_mod),
                str(self.modrm_reg) if self.modrm_reg != None else 'reg',
                str(self.modrm_rm) if self.modrm_rm != None else 'rm_reg',
            )
            result += ' SIB(sib_scale, sib_index, sib_base)' if self.sib else ''
        result += ' disp%d' % (self.disp_size,) if self.disp_size != None else ''
        result += ' imm%d' % (self.imm_size,) if self.imm_size != None else ''
        return result

@dataclass
class Instruction:
    name: str
    operands: tuple
    opcode_info: Instruction_OpcodeInfo
    archs: tuple
    op_size: int

    def dup(self, operands = None, opcode_info = None, archs = None):
        return Instruction(
            self.name,
            self.operands if operands == None else operands,
            self.opcode_info if opcode_info == None else opcode_info,
            self.archs if archs == None else archs,
            self.op_size,
        )

    def __str__(self):
        result = self.name.lower()
        result += ' ' if len(self.operands) != 0 else ''
        result += ', '.join([str(operand) for operand in self.operands])
        result += ' # '
        result += str(self.opcode_info)
        return result


