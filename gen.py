from dataclasses import dataclass

# Constants ####################################################################

ARCH_I386 = 'i386'
ARCH_AMD64 = 'amd64'

ARCHS_I386 = (ARCH_I386,)
ARCHS_AMD64 = (ARCH_AMD64,)
ARCHS_ALL = (ARCH_I386, ARCH_AMD64,)

imms = {
    'imm8u': 8,
    'imm16u': 16,
    'imm32u': 32,
    'imm64u': 64,
    'imm8s': 8,
    'imm16s': 16,
    'imm32s': 32,
    'imm64s': 64,
}

imms_without_signs = ('imm8', 'imm16', 'imm32', 'imm64')

regs = {
    'reg8': 8,
    'reg16': 16,
    'reg32': 32,
    'reg64': 64,
}

moffsets = {
    'moffset8': 8,
    'moffset16': 16,
    'moffset32': 32,
    'moffset64': 64,
}

regmems = {
    'reg/mem8': (8, 8),
    'reg/mem16': (16, 16),
    'reg/mem32': (32, 32),
    'reg/mem64': (64, 64),
    'reg32/mem16': (32, 16),
    'reg64/mem16': (64, 16),
}

slashes = {
    '/r': None,
    '/0': 0,
    '/1': 1,
    '/2': 2,
    '/3': 3,
    '/4': 4,
    '/5': 5,
    '/6': 6,
    '/7': 7,
}

is_ = {
    'ib': 8,
    'iw': 16,
    'id': 32,
    'iq': 64,
}

plusrs = {
    '+rb': 8,
    '+rw': 16,
    '+rd': 32,
    '+rq': 64,
}

specifiedregs = {
    'AL': 8,
    'AX': 16,
    'EAX': 32,
    'RAX': 64,
}

specifiedsegregs = {
    'DS': 16,
    'ES': 16,
    'FS': 16,
    'GS': 16,
    'SS': 16,
}

# Utils ########################################################################

def get_native_size(arch):
    if arch == ARCH_I386:
        return 32
    elif arch == ARCH_AMD64:
        return 64
    else:
        raise Exception('Error: Unknown architecture: %s' % (arch,))

def is_str(obj):
    return isinstance(obj, str)

def is_hex_byte(x):
    assert(is_str(x))
    hexdigits = '0123456789abcdefABCDEF'
    return len(x) == 2 and all(c in hexdigits for c in x)

def size_to_word(size):
    if size == 8:
        return 'byte'
    elif size == 16:
        return 'word'
    elif size == 32:
        return 'dword'
    elif size == 64:
        return 'qword'
    else:
        raise Exception('Unknown size: %d' % (size,))

def gen_id():
    if not hasattr(gen_id, 'next'):
        gen_id.next = 0
    gen_id.next += 1
    return gen_id.next

# Instruction ##################################################################

@dataclass
class Entry:
    mnemonic: str
    opcode: str
    archs: tuple
    op_size: int

@dataclass
class Entry_Decomposed:
    name: str
    operands: tuple
    opcodes: tuple
    archs: tuple
    op_size: int

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

    def _dup_override(self, modrm_mod = None, modrm_rm = None, sib = None, disp_size = None,
                      prefix_operand_size_override = False, prefix_rex_w = False):
        return Instruction_OpcodeInfo(
            self.opcodes,
            opcode_plus_reg = self.opcode_plus_reg,
            modrm = self.modrm,
            modrm_mod = self.modrm_mod if modrm_mod == None else modrm_mod,
            modrm_reg = self.modrm_reg,
            modrm_rm = self.modrm_rm if modrm_rm == None else modrm_rm,
            sib = self.sib if sib == None else sib,
            sib_scale = self.sib_scale,
            sib_index = self.sib_index,
            sib_base = self.sib_base,
            disp_size = self.disp_size if disp_size == None else disp_size,
            imm_size = self.imm_size,
            prefix_operand_size_override = self.prefix_operand_size_override
                if prefix_operand_size_override == False
                else prefix_operand_size_override,
            prefix_rex = self.prefix_rex if not any((prefix_rex_w,)) else True,
            prefix_rex_w = self.prefix_rex_w if prefix_rex_w == False
                           else prefix_rex_w,
        )

    def dup_specialize_modrm(self, mod = None, rm = None, sib = False, disp = None):
        assert(self.modrm == True)
        assert(self.modrm_mod == None)
        assert(self.modrm_rm == None)
        assert(self.sib == False)
        assert(self.disp_size == None)
        return self._dup_override(
            modrm_mod = mod,
            modrm_rm = rm,
            sib = sib,
            disp_size = disp,
        )

    def dup_add_prefixes(self, operand_size_override = False, rex_w = False):
        return self._dup_override(
            prefix_operand_size_override = operand_size_override,
            prefix_rex_w = rex_w,
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

    def __str__(self):
        result = self.name.lower()
        result += ' ' if len(self.operands) != 0 else ''
        result += ', '.join([str(operand) for operand in self.operands])
        result += ' # '
        result += str(self.opcode_info)
        return result

# C Generator ##################################################################

@dataclass
class C_Parameter:
    name: str
    type_: str

    def __str__(self):
        return '%s %s' % (self.type_, self.name,)

def generate_c_from_instr(instr):
    def instr_c_name(instr):
        suffix = ''
        for operand in instr.operands:
            suffix += '_'
            if operand.kind in operand_kind_specified_regmems:
                suffix += ('rm%d' % (operand.size,) if operand.size == operand.mem_size
                           else 'r%dm%d' % (operand.size, operand.mem_size,))
            if operand.kind == OP_REG:
                suffix += 'reg%d' % (operand.size,)
            elif operand.kind == OP_REGMEM_REG:
                suffix += 'reg%d' % (operand.size,)
            elif operand.kind == OP_REGMEM_ATREG:
                suffix += 'mem%datreg%d' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATREGPLUSDISP8:
                suffix += 'mem%datreg%dplusdisp8' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATREGPLUSDISP32:
                suffix += 'mem%datreg%dplusdisp32' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIB:
                suffix += 'mem%datbasereg%dindexreg%dscale' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIBPLUSDISP8:
                suffix += 'mem%datbasereg%dindexreg%dscaleplusdisp8' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIBPLUSDISP32:
                suffix += 'mem%datbasereg%dindexreg%dscaleplusdisp32' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATDISP32:
                suffix += 'mem%datdisp32' % (operand.mem_size,)
            elif operand.kind == OP_REGMEM_ATRIPPLUSDISP32:
                suffix += 'mem%datripplusdisp32' % (operand.mem_size,)
            elif operand.kind == OP_MOFFSET:
                suffix += 'moffset%d' % (operand.size,)
            elif operand.kind == OP_SPECREG:
                suffix += operand.contents.lower()
            elif operand.kind == OP_SPECSEGREG:
                suffix += operand.contents.lower()
            elif operand.kind == OP_SEGREG:
                suffix += 'segreg'
            elif operand.kind == OP_IMM:
                suffix += 'imm%d' % (operand.size,)
            else:
                raise Exception('Unsupported operand: %s' % (str(operand),))
        return 'x86gen_%s_%s%s' % (instr.archs[0], instr.name.lower(), suffix,)

    def instr_c_parameters(instr):
        lambdas = {
            OP_REG: lambda operand, arch: (
                C_Parameter('reg', 'enum X86Gen_Reg%d' % (operand.size,)),
            ),
            OP_REGMEM_REG: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (operand.size,)),
            ),
            OP_REGMEM_ATREG: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
            ),
            OP_REGMEM_ATREGPLUSDISP8: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('disp', 'int8_t',),
            ),
            OP_REGMEM_ATREGPLUSDISP32: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('disp', 'int32_t',),
            ),
            OP_REGMEM_ATSIB: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
            ),
            OP_REGMEM_ATSIBPLUSDISP8: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
                C_Parameter('disp', 'int8_t'),
            ),
            OP_REGMEM_ATSIBPLUSDISP32: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
                C_Parameter('disp', 'int32_t'),
            ),
            OP_REGMEM_ATRIPPLUSDISP32: lambda operand, arch: (
                C_Parameter('disp', 'int32_t'),
            ),
            OP_REGMEM_ATDISP32: lambda operand, arch: (
                C_Parameter('disp', 'uint32_t'),
            ),
            OP_MOFFSET: lambda operand, arch: (
                C_Parameter('disp', 'uint%d_t' % (get_native_size(arch),)),
            ),
            OP_SPECREG: lambda operand, arch: tuple(),
            OP_SPECSEGREG: lambda operand, arch: tuple(),
            OP_SEGREG: lambda operand, arch: (
                C_Parameter('reg', 'enum X86Gen_SegReg'),
            ),
            OP_IMM: lambda operand, arch: (
                C_Parameter('imm', '%sint%d_t' % (
                    '' if operand.signed else 'u',
                    operand.size,
                )),
            ),
        }
        result = tuple([C_Parameter('output', 'X86Gen_Output')])
        for operand in instr.operands:
            if operand.kind in lambdas:
                result += lambdas[operand.kind](operand, instr.archs[0])
            else:
                raise Exception('Unsupported operand: %s' % (str(operand),))
        return result

    def instr_c_output(instr):
        result = []
        oi = instr.opcode_info
        if oi.prefix_operand_size_override:
            result.append('X86GEN_PREFIX_OPERAND_SIZE_OVERRIDE')
        if oi.prefix_rex_w:
            result.append('X86GEN_PREFIX_REX_W')
        for opcode_byte in oi.opcodes:
            result.append('0x%s' % (opcode_byte,))
        if oi.opcode_plus_reg:
            result[-1] += ' + reg'
        if oi.modrm:
            assert(oi.modrm_mod != None)
            result.append('X86GEN_MOD_RM(%s, %s, %s)' % (
                'X86GEN_B%s' % (format(oi.modrm_mod, '02b'),),
                'X86GEN_B%s' % (format(oi.modrm_reg, '03b'),)
                    if oi.modrm_reg != None else 'reg',
                'X86GEN_B%s' % (format(oi.modrm_rm, '03b'),)
                    if oi.modrm_rm != None else 'rm_reg',
            ))
            if oi.sib:
                result.append('X86GEN_SIB(%s, %s, %s)' % (
                    'X86GEN_B%s' % (format(oi.sib_scale, '02b'),)
                        if oi.sib_scale != None else 'sib_scale',
                    'X86GEN_B%s' % (format(oi.sib_index, '03b'),)
                        if oi.sib_index != None else 'sib_index',
                    'X86GEN_B%s' % (format(oi.sib_base, '03b'),)
                        if oi.sib_base!= None else 'sib_base',
                ))
        if oi.disp_size != None:
            if oi.disp_size != 8:
                result.append('X86GEN_EXPAND_%d(disp)' % (oi.disp_size,))
            else:
                result.append('disp')
        if oi.imm_size != None:
            if oi.imm_size != 8:
                result.append('X86GEN_EXPAND_%d(imm)' % (oi.imm_size,))
            else:
                result.append('imm')
        return tuple(result)

    def instr_mnemonic(instr):
        result = instr.name.lower()
        result += ' ' if len(instr.operands) != 0 else ''
        result += ', '.join([operand.stringify(get_native_size(instr.archs[0])) for operand in instr.operands])
        return result

    def instr_notes(instr):
        result = []
        result.append(instr_mnemonic(instr))
        for operand in instr.operands:
            if operand.kind == OP_REGMEM_ATREG:
                result.append('@warning rm_reg can\'t be rSP or rBP.')
            elif operand.kind in (OP_REGMEM_ATREGPLUSDISP8, OP_REGMEM_ATREGPLUSDISP32,):
                result.append('@warning rm_reg can\'t be rSP.')
        return tuple(result)

    def build_c_function(name, parameters, notes, c_output):
        return (
            '/* %s */\n' +
            'static void %s(\n' +
            '  %s\n'
            ') {\n' +
            '  const uint8_t buf[] = {\n' +
            '    %s\n' +
            '  };\n' +
            '  X86Gen_Output_Write(output, sizeof(buf), buf);\n' +
            '}\n'
        ) % (
            '\n * '.join(notes),
            name,
            ',\n  '.join([str(parameter) for parameter in parameters]),
            ',\n    '.join(c_output)
        )

    def instr_original_mnemonic(instr):
        result = instr.name.lower()
        result += ' ' if len(instr.operands) != 0 else ''
        result += ', '.join([(
            operand.contents if 'imm' not in operand.contents
            else operand.contents[:-1]).lower() # There's a signity in the end.
                for operand in instr.operands])
        return result

    name = instr_c_name(instr)
    parameters = instr_c_parameters(instr)
    c_output = instr_c_output(instr)
    notes = instr_notes(instr)
    c_function = build_c_function(name, parameters, notes, c_output)
    original_mnemonic = instr_original_mnemonic(instr)
    return original_mnemonic, c_function

def generate_c(instructions):
    emitted_mnemonics = set()
    for instr in instructions:
        original_mnemonic, c_function = generate_c_from_instr(instr)
        if original_mnemonic not in emitted_mnemonics:
            print('/*\n * %s\n */\n' % (original_mnemonic,))
            emitted_mnemonics.add(original_mnemonic)
        print(c_function)

# The rest #####################################################################

def main():
    def entry(mnemonic, opcode, archs = (ARCH_I386, ARCH_AMD64), op_size = None):
        return Entry(mnemonic, opcode, archs, op_size)

    def entry_decomposed(entry):
        def mnemonic_parts(mnemonic):
            # Commas sould be followed by a space.
            assert(mnemonic.count(',') == mnemonic.count(', '))
            # Only single spaces allowed.
            assert('  ' not in mnemonic)
            # 'MOVZX reg32, reg8' -> [ 'MOVZX reg32', 'reg8' ]
            comma_splitted = mnemonic.split(', ')
            # 'MOVZX reg32' -> [ 'MOVZX', 'reg32' ]
            name_and_possibly_first_operand = comma_splitted[0].split(' ')
            # 'MOVZX'
            name = name_and_possibly_first_operand[0]
            # [ 'reg32', 'reg8' ]
            operands = name_and_possibly_first_operand[1:] + comma_splitted[1:]
            return name, tuple(operands)

        def get_opcode_parts(opcode):
            # Only single spaces allowed.
            assert('  ' not in opcode)
            return tuple(opcode.split(' '))

        # Entry parsing result.
        name, operands = mnemonic_parts(entry.mnemonic)
        opcodes = get_opcode_parts(entry.opcode)
        archs = entry.archs
        op_size = entry.op_size
        return Entry_Decomposed(name, operands, opcodes, archs, op_size)

    def instruction_operands(decomposed_entry_operands):
        result = []
        for operand in decomposed_entry_operands:
            if operand in regmems:
                reg_size, mem_size = regmems[operand]
                result.append(Instruction_Operand(OP_REGMEM, operand, reg_size, mem_size = mem_size))
            elif operand in regs:
                reg_size = regs[operand]
                result.append(Instruction_Operand(OP_REG, operand, reg_size))
            elif operand in moffsets:
                target_size = moffsets[operand]
                result.append(Instruction_Operand(OP_MOFFSET, operand, target_size))
            elif operand in specifiedregs:
                specreg_size = specifiedregs[operand]
                result.append(Instruction_Operand(OP_SPECREG, operand, specreg_size))
            elif operand in specifiedsegregs:
                result.append(Instruction_Operand(OP_SPECSEGREG, operand, 0))
            elif operand in imms:
                imm_size = imms[operand]
                assert(operand[-1] in ('s', 'u'))
                signed = True if operand[-1] == 's' else False
                result.append(Instruction_Operand(OP_IMM, operand, imm_size, signed = signed))
            elif operand in imms_without_signs:
                raise Exception('Please specify the signity of the immediate' +
                                ' operand. Use \'u\' suffix to specify an' +
                                ' unsigned operand and \'s\' to specify a' +
                                ' signed one. Example: imm32s, imm8u.')
            elif operand == 'segReg':
                result.append(Instruction_Operand(OP_SEGREG, operand, 0))
            else:
                raise Exception('Unknown operand: %s' % (operand,))
        return tuple(result)

    def instruction_opcode_info(instruction_operands, decomposed_entry_opcodes):
        disp_size = None
        for operand in instruction_operands:
            if operand.kind == OP_MOFFSET:
                disp_size = 0
        opcode_bytes = []
        opcode_plus_reg = False
        modrm = False
        modrm_reg = None
        imm_size = None
        for opcode in decomposed_entry_opcodes:
            if is_hex_byte(opcode):
                assert(opcode_plus_reg == False) # +r should follow the last opcode.
                opcode_bytes.append(opcode)
            elif opcode in plusrs:
                opcode_plus_reg = True
            elif opcode in slashes:
                modrm = True
                modrm_reg = slashes[opcode]
            elif opcode in is_:
                imm_size = is_[opcode]
            else:
                raise Exception('Unknown opcode: %s' % (opcode,))
        return Instruction_OpcodeInfo(
            tuple(opcode_bytes),
            opcode_plus_reg = opcode_plus_reg,
            modrm = modrm,
            modrm_reg = modrm_reg,
            disp_size = disp_size,
            imm_size = imm_size
        )

    def instruction_variations_modrm(name, generic_operands, generic_opcode_info, archs, op_size):
        def specialized_operands(new_modrm_operand_kind):
            # The stuff here is not cached for the sake of readability.
            # Find the index of the generic ModRM operand.
            for i in range(len(generic_operands)):
                if generic_operands[i].kind == OP_REGMEM:
                    modrm_i = i
                    break
            else:
                raise Exception('This can only be called with operand list containig ModRM operand.')
            # Get the generic ModRM operand.
            generic_modrm_operand = generic_operands[modrm_i]
            # Get all the previous and next generic operands.
            prev_operands = generic_operands[:modrm_i]
            next_operands = generic_operands[modrm_i + 1:]
            # Specialize the generic modrm operand.
            specialized_modrm_operand = generic_modrm_operand.dup_specialized_modrm(new_modrm_operand_kind)
            # Put it back where it was in the operand list and return it.
            return tuple(prev_operands + (specialized_modrm_operand,) + next_operands)

        def specialized_opcode_info(mod = None, rm = None, sib = False, disp = None):
            return generic_opcode_info.dup_specialize_modrm(mod = mod, rm = rm, sib = sib, disp = disp)

        def variant(archs, operand_kind, mod = None, rm = None, sib = False, disp = None):
            return (
                archs,
                specialized_operands(operand_kind),
                specialized_opcode_info(mod, rm, sib, disp),
            )

        result = []
        # If it's not a ModRM instruction - just return it.
        if not generic_opcode_info.modrm:
            return (Instruction(name, generic_operands, generic_opcode_info, archs, op_size),)
        # If it is - split the instruction into several with different forms of ModRM.
        # First, split operands.
        variants = (
            # reg32
            variant(ARCHS_ALL,   OP_REGMEM_REG,             mod = 0b11),
            # [reg32]
            variant(ARCHS_ALL,   OP_REGMEM_ATREG,           mod = 0b00),
            # [disp32]
            variant(ARCHS_I386,  OP_REGMEM_ATDISP32,        mod = 0b00, rm = 0b101, disp = 32),
            # [rip + disp32]
            variant(ARCHS_AMD64, OP_REGMEM_ATRIPPLUSDISP32, mod = 0b00, rm = 0b101, disp = 32),
            # [reg32 + disp8]
            variant(ARCHS_ALL,   OP_REGMEM_ATREGPLUSDISP8,  mod = 0b01, disp = 8),
            # [reg32 + disp32]
            variant(ARCHS_ALL,   OP_REGMEM_ATREGPLUSDISP32, mod = 0b10, disp = 32),
            # [base + index * scale]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIB,           mod = 0b00, rm = 0b100, sib = True),
            # [base + index * scale + disp8]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIBPLUSDISP8,  mod = 0b01, rm = 0b100, sib = True, disp = 8),
            # [base + index * scale + disp32]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIBPLUSDISP32, mod = 0b10, rm = 0b100, sib = True, disp = 32),
        )
        for variant in variants:
            v_archs = variant[0]
            v_operands = variant[1]
            v_opcode_info = variant[2]
            for arch in archs:
                if arch in v_archs:
                    result.append(Instruction(name, v_operands, v_opcode_info, (arch,), op_size))
        return tuple(result)

    def instruction_variations_arch(name, operands, opcode_info, archs, op_size):
        result = []
        for arch in archs:
            operand_size_override = True if arch in (ARCH_AMD64, ARCH_I386,) and op_size == 16 else False
            rex_w = True if op_size == 64 else False
            assert((rex_w and arch == ARCH_AMD64) or (not rex_w))
            new_opcode_info = opcode_info.dup_add_prefixes(operand_size_override = operand_size_override, rex_w = rex_w)
            result.append(Instruction(name, operands, new_opcode_info, (arch,), op_size))
        return tuple(result)

    def instruction_find_op_size(instr):
        if instr.op_size != None:
            return
        op_size = 0
        for operand in instr.operands:
            if operand.size > op_size:
                op_size = operand.size
        instr.op_size = op_size

    def instruction_update_opcode_info_sizes(instr):
        assert(len(instr.archs) == 1)
        if instr.opcode_info.disp_size == 0:
            instr.opcode_info.disp_size = get_native_size(instr.archs[0])

    entries = (
        # AAA
        entry('AAA', '37', (ARCH_I386,)),
        # AAD
        entry('AAD', 'D5 0A', (ARCH_I386,)),
        # AAM
        entry('AAM', 'D4 0A', (ARCH_I386,)),
        # AAS
        entry('AAS', '3F', (ARCH_I386,)),
        # ADD
        entry('ADD AL, imm8u', '04 ib'),
        entry('ADD AX, imm16u', '05 iw'),
        entry('ADD EAX, imm32u', '05 id'),
        entry('ADD RAX, imm32s', '05 id', (ARCH_AMD64,)),
        entry('ADD reg/mem8, imm8u', '80 /0 ib'),
        entry('ADD reg/mem16, imm16u', '81 /0 iw'),
        entry('ADD reg/mem32, imm32u', '81 /0 id'),
        entry('ADD reg/mem64, imm32s', '81 /0 id', (ARCH_AMD64,)),
        entry('ADD reg/mem16, imm8s', '83 /0 ib'),
        entry('ADD reg/mem32, imm8s', '83 /0 ib'),
        entry('ADD reg/mem64, imm8s', '83 /0 ib', (ARCH_AMD64,)),
        entry('ADD reg/mem8, reg8', '00 /r'),
        entry('ADD reg/mem16, reg16', '01 /r'),
        entry('ADD reg/mem32, reg32', '01 /r'),
        entry('ADD reg/mem64, reg64', '01 /r', (ARCH_AMD64,)),
        entry('ADD reg8, reg/mem8', '02 /r'),
        entry('ADD reg16, reg/mem16', '03 /r'),
        entry('ADD reg32, reg/mem32', '03 /r'),
        entry('ADD reg64, reg/mem64', '03 /r', (ARCH_AMD64,)),
        # DAA
        entry('DAA', '27', (ARCH_I386,)),
        # DAS
        entry('DAS', '2F', (ARCH_I386,)),
        # MOV
        entry('MOV reg/mem8, reg8', '88 /r'),
        entry('MOV reg/mem16, reg16', '89 /r'),
        entry('MOV reg/mem32, reg32', '89 /r'),
        entry('MOV reg/mem64, reg64', '89 /r', (ARCH_AMD64,)),
        entry('MOV reg8, reg/mem8', '8A /r'),
        entry('MOV reg16, reg/mem16', '8B /r'),
        entry('MOV reg32, reg/mem32', '8B /r'),
        entry('MOV reg64, reg/mem64', '8B /r', (ARCH_AMD64,)),
        entry('MOV reg/mem16, segReg', '8C /r'),
        entry('MOV reg32/mem16, segReg', '8C /r'),
        entry('MOV reg64/mem16, segReg', '8C /r', (ARCH_AMD64,)),
        entry('MOV segReg, reg/mem16', '8E /r', op_size = 0),
        entry('MOV AL, moffset8', 'A0'),
        entry('MOV AX, moffset16', 'A1'),
        entry('MOV EAX, moffset32', 'A1'),
        entry('MOV RAX, moffset64', 'A1', (ARCH_AMD64,)),
        entry('MOV moffset8, AL', 'A2'),
        entry('MOV moffset16, AX', 'A3'),
        entry('MOV moffset32, EAX', 'A3'),
        entry('MOV moffset64, RAX', 'A3', (ARCH_AMD64,)),
        entry('MOV reg8, imm8u', 'B0 +rb ib'),
        entry('MOV reg16, imm16u', 'B8 +rw iw'),
        entry('MOV reg32, imm32u', 'B8 +rd id'),
        entry('MOV reg64, imm64u', 'B8 +rq iq', (ARCH_AMD64,)),
        entry('MOV reg/mem8, imm8u', 'C6 /0 ib'),
        entry('MOV reg/mem16, imm16u', 'C7 /0 iw'),
        entry('MOV reg/mem32, imm32u', 'C7 /0 id'),
        entry('MOV reg/mem64, imm32s', 'C7 /0 id', (ARCH_AMD64,)),
        # POP
        entry('POP reg/mem16', '8F /0'),
        entry('POP reg/mem32', '8F /0', (ARCH_I386,)),
        entry('POP reg/mem64', '8F /0', (ARCH_AMD64,), 0),
        entry('POP reg16', '58 +rw'),
        entry('POP reg32', '58 +rd', (ARCH_I386,)),
        entry('POP reg64', '58 +rq', (ARCH_AMD64,), 0),
        entry('POP DS', '1F', (ARCH_I386,)),
        entry('POP ES', '07', (ARCH_I386,)),
        entry('POP SS', '17', (ARCH_I386,)),
        entry('POP FS', '0F A1'),
        entry('POP GS', '0F A9'),
        # POPA
        entry('POPA', '61', (ARCH_I386,), 16),
        entry('POPAD', '61', (ARCH_I386,), 32),
        # RET
        entry('RET', 'C3'),
        entry('RET imm16u', 'C2 iw', op_size = 0),
    )

    instructions = tuple()
    for entry in entries:
        decomposed = entry_decomposed(entry)
        name = decomposed.name
        archs = decomposed.archs
        op_size = decomposed.op_size
        operands = instruction_operands(decomposed.operands)
        opcode_info = instruction_opcode_info(operands, decomposed.opcodes)
        instruction = Instruction(name, operands, opcode_info, archs, op_size)
        instructions += (instruction,)

    def perform_pass(instructions, the_pass):
        result = tuple()
        for instr in instructions:
            name = instr.name
            operands = instr.operands
            opcode_info = instr.opcode_info
            archs = instr.archs
            op_size = instr.op_size
            variations = the_pass(name, operands, opcode_info, archs, op_size)
            result += variations
        return result

    for instr in instructions:
        instruction_find_op_size(instr)

    instructions = perform_pass(instructions, instruction_variations_arch)
    instructions = perform_pass(instructions, instruction_variations_modrm)

    # Now we know the native size of e. g. pointers.
    for instr in instructions:
        instruction_update_opcode_info_sizes(instr)

    generate_c(instructions)

if __name__ == '__main__':
    main()
