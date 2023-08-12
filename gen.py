import sys

# Constants ####################################################################

CGEN_PREFIX = 'X86GEN'
CGEN_OUTPUT_COMPONENT_SEPARATOR = ',\n    '
CGEN_PARAMETER_SEPARATOR = ',\n  '

ARCH_I386 = 'i386'
ARCH_AMD64 = 'amd64'

arch_variants = (ARCH_I386, ARCH_AMD64)

test_values_limit = 1

gp_regs_of_size = {
    8: ('AL', 'BL', 'CL', 'DL', 'AH', 'BH', 'CH', 'DH'),
    16: ('AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'SP', 'BP'),
    32: ('EAX', 'EBX', 'ECX', 'EDX', 'ESI', 'EDI', 'ESP', 'EBP'),
    64: ('RAX', 'RBX', 'RCX', 'RDX', 'RSI', 'RDI', 'RSP', 'RBP'),
}

rm_regs_of_size = {
    8: ('AL', 'BL', 'CL', 'DL', 'AH', 'BH'),
    16: ('AX', 'BX', 'CX', 'DX', 'SI', 'DI'),
    32: ('EAX', 'EBX', 'ECX', 'EDX', 'ESI', 'EDI'),
    64: ('RAX', 'RBX', 'RCX', 'RDX', 'RSI', 'RDI'),
}

seg_regs = ('CS', 'DS', 'ES', 'FS', 'GS', 'SS')

imms = {
    'imm8': 8,
    'imm16': 16,
    'imm32': 32,
    'imm64': 64,
}

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

segregs = {
    'DS': 16,
    'ES': 16,
    'FS': 16,
    'GS': 16,
    'SS': 16,
}

B00 = 0
B01 = 1
B10 = 2
B11 = 3

B000 = 0
B001 = 1
B010 = 2
B011 = 3
B100 = 4
B101 = 5
B110 = 6
B111 = 7

# Utils ########################################################################

def get_native_size(arch):
    if arch == ARCH_I386:
        return 32
    elif arch == ARCH_AMD64:
        return 64
    else:
        raise Exception('Error: Unknown architecture: %s' % (arch,))

def is_tuple(obj):
    return isinstance(obj, tuple)

def is_int(obj):
    return isinstance(obj, int)

def is_str(obj):
    return isinstance(obj, str)

def is_hex_byte(x):
    assert(is_str(x))
    hexdigits = '0123456789abcdefABCDEF'
    return len(x) == 2 and all(c in hexdigits for c in x)

def is_byte_value(x):
    return x >= 0 and x <= 255

def is_8_to_64(x):
    return x in (8, 16, 32, 64)

def is_mem_size(x):
    return is_8_to_64(x)

def is_reg_size(x):
    return is_8_to_64(x)

def is_imm_size(x):
    return is_8_to_64(x)

def is_disp_size(x):
    return x in (8, 32)

def is_moffset_size(x):
    return x in (32, 64)

def is_native_size(x):
    return x in (32, 64)

def is_arch(x):
    return x in arch_variants

def is_int_or_none(x):
    return is_int(x) or x == None

def without_nones(collection):
    result = []
    for it in collection:
        if it != None:
            result.append(it)
    return tuple(result)

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

# CGen #########################################################################

def is_cgen_parameter(x):
    return isinstance(x, CGen_Parameter)

class CGen_Output_Component:
    pass

class CGen_Output_Component_ModRm(CGen_Output_Component):
    def __init__(self, mod, reg, rm):
        assert(is_int(mod))
        if reg != None:
            assert(is_int(reg))
            assert(reg in (0, 1, 2, 3, 4, 5, 6, 7))
        if rm != None:
            assert(is_int(rm))
            assert(rm in (0, 1, 2, 3, 4, 5, 6, 7))
        self.mod = '%s_B%s' % (CGEN_PREFIX, format(mod, '02b'),)
        self.reg = 'reg' if reg == None else '%s_B%s' % (
            CGEN_PREFIX,
            format(reg, '03b'),
        )
        self.rm = 'rm_reg' if rm == None else '%s_B%s' % (
            CGEN_PREFIX,
            format(rm, '03b'),
        )

    def emit(self):
        return '%s_MOD_RM(%s, %s, %s)' % (CGEN_PREFIX, self.mod, self.reg, self.rm,)

class CGen_Output_Component_ModRm_Reg(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B11, reg_value, None)

class CGen_Output_Component_ModRm_AtReg(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B00, reg_value, None)

class CGen_Output_Component_ModRm_AtRipPlusDisp32(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B00, reg_value, B101)

class CGen_Output_Component_ModRm_AtDisp32(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B00, reg_value, B101)

class CGen_Output_Component_ModRm_AtRegPlusDisp8(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B01, reg_value, None)

class CGen_Output_Component_ModRm_AtRegPlusDisp32(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B10, reg_value, None)

class CGen_Output_Component_ModRm_AtScaleIndexBase(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B00, reg_value, B100)

class CGen_Output_Component_ModRm_AtScaleIndexBaseDisp8(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B01, reg_value, B100)

class CGen_Output_Component_ModRm_AtScaleIndexBaseDisp32(CGen_Output_Component_ModRm):
    def __init__(self, reg_value):
        super().__init__(B10, reg_value, B100)

class CGen_Output_Component_Sib(CGen_Output_Component):
    def emit(self):
        return '%s_SIB(sib_scale, sib_index, sib_base)' % (CGEN_PREFIX,)

class CGen_Output_Component_Value(CGen_Output_Component):
    def __init__(self, name, size):
        assert(is_str(name))
        assert(is_int(size))
        assert(is_8_to_64(size))
        self.name = name
        self.size = size

    def emit(self):
        if self.size == 8:
            return '%s' % (self.name)
        elif self.size in (16, 32, 64):
            return '%s_EXPAND_%d(%s)' % (CGEN_PREFIX, self.size, self.name)
        else:
            raise Exception('Unknown size: %d' % (self.size,))

class CGen_Output_Component_Disp(CGen_Output_Component_Value):
    def __init__(self, size):
        super().__init__('disp', size)

class CGen_Output_Component_Imm(CGen_Output_Component_Value):
    def __init__(self, size):
        super().__init__('imm', size)

class CGen_Output_Component_Moffset(CGen_Output_Component_Value):
    def __init__(self, size):
        super().__init__('moffset', size)

class CGen_Output_Component_Byte(CGen_Output_Component):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        self.value = value

    def emit(self):
        return '0x%02X' % (self.value,)

class CGen_Output_Component_BytePlusReg(CGen_Output_Component):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        self.value = value

    def emit(self):
        return '0x%02X + reg' % (self.value,)

class CGen_Output_Component_Prefix_OperandSizeOverride(CGen_Output_Component):
    def emit(self):
        return '%s_PREFIX_OPERAND_SIZE_OVERRIDE' % (CGEN_PREFIX,)

class CGen_Output_Component_Prefix_RexW(CGen_Output_Component):
    def emit(self):
        return '%s_PREFIX_REX_W' % (CGEN_PREFIX,)

class CGen_Output:
    def __init__(self, components):
        self.components = components

    def emit(self):
        return CGEN_OUTPUT_COMPONENT_SEPARATOR.join(
            [component.emit() for component in self.components]
        )

def test_values_uint(size):
    assert(size <= 64)
    part = size // 4 + 2
    return (
        '0x1122334455667788'[:part],
        '0x8877665544332211'[:part],
        '0x0000000000000000'[:part],
        '0xFFFFFFFFFFFFFFFF'[:part],
    )

def test_values_int(size):
    assert(size <= 64)
    part = size // 4 + 2
    npart = part + 1
    return (
        '0x0011223344556677'[:part],
        '0x7766554433221100'[:part],
        '0x0000000000000000'[:part],
        '0x7FFFFFFFFFFFFFFF'[:part],
        '-0x0011223344556677'[:npart],
        '-0x7766554433221100'[:npart],
        '-0x0000000000000000'[:npart],
        '-0x7FFFFFFFFFFFFFFF'[:npart],
    )

class CGen_Parameter:
    pass

class CGen_Parameter_Unsigned(CGen_Parameter):
    def __init__(self, name, size):
        assert(is_int(size))
        assert(is_8_to_64(size))
        self.size = size
        self.name = name

    def emit(self):
        return 'uint%d_t %s' % (self.size, self.name,)

    def test_values(self):
        return test_values_uint(self.size)

class CGen_Parameter_Imm(CGen_Parameter_Unsigned):
    def __init__(self, size):
        super().__init__('imm', size)

class CGen_Parameter_Moffset(CGen_Parameter_Unsigned):
    def __init__(self, size):
        super().__init__('moffset', size)

class CGen_Parameter_Disp(CGen_Parameter_Unsigned):
    def __init__(self, size):
        super().__init__('disp', size)

class CGen_Parameter_SegReg(CGen_Parameter):
    def emit(self):
        return 'enum X86Gen_SegReg reg'

    def test_values(self):
        return tuple(
            [reg.lower() for reg in seg_regs]
        )

class CGen_Parameter_Reg_Generic(CGen_Parameter):
    def __init__(self, name, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        self.name = name
        self.size = size

    def emit(self):
        return 'enum X86Gen_Reg%d %s' % (self.size, self.name,)

class CGen_Parameter_Reg(CGen_Parameter_Reg_Generic):
    def __init__(self, size):
        super().__init__('reg', size)

    def test_values(self):
        assert(self.size in gp_regs_of_size)
        return tuple(
            [reg.lower() for reg in gp_regs_of_size[self.size]]
        )

class CGen_Parameter_RmReg(CGen_Parameter_Reg_Generic):
    def __init__(self, size):
        super().__init__('rm_reg', size)

    def test_values(self):
        assert(self.size in rm_regs_of_size)
        return tuple(
            [reg.lower() for reg in rm_regs_of_size[self.size]]
        )

class CGen_Parameter_Base(CGen_Parameter_Reg_Generic):
    def __init__(self, size):
        super().__init__('sib_base', size)

    def test_values(self):
        assert(self.size in rm_regs_of_size)
        return tuple(
            [reg.lower() for reg in rm_regs_of_size[self.size]]
        )

class CGen_Parameter_Index(CGen_Parameter_Reg_Generic):
    def __init__(self, size):
        super().__init__('sib_index', size)

    def test_values(self):
        assert(self.size in rm_regs_of_size)
        return tuple(
            [reg.lower() for reg in rm_regs_of_size[self.size]]
        )

class CGen_Parameter_Scale(CGen_Parameter):
    def emit(self):
        return 'enum X86Gen_Scale sib_scale'

    def test_values(self):
        return (
            'X86Gen_Scale_1',
            'X86Gen_Scale_2',
            'X86Gen_Scale_4',
            'X86Gen_Scale_8',
        )

class CGen_Parameter_Output(CGen_Parameter):
    def emit(self):
        return 'X86Gen_Output output'

class CGen_Parameters:
    def __init__(self, parameters):
        assert(is_tuple(parameters))
        for parameter in parameters:
            assert(is_cgen_parameter(parameter))
        # Each function unconditionally has the 'output' parameter.
        self.parameters = (CGen_Parameter_Output(),) + parameters

    def emit(self):
        return CGEN_PARAMETER_SEPARATOR.join(
            [parameter.emit() for parameter in self.parameters]
        )

class CGen_Function:
    def __init__(self, comment, name, parameters, output):
        self.comment = comment
        self.name = name
        self.parameters = parameters
        self.output = output

    def emit(self):
        return (
            '%s\n' +
            'static void x86gen_%s(\n' +
            '  %s\n' +
            ') {\n' +
            '  const uint8_t buf[] = {\n' +
            '    %s\n' +
            '  };\n' +
            '  X86Gen_Output_Write(output, sizeof(buf), buf);\n' +
            '}'
        ) % (self.comment, self.name, self.parameters.emit(), self.output.emit())

# Operand ######################################################################

def c_name_rm(reg_size, mem_size):
    assert(is_int(reg_size))
    assert(is_reg_size(reg_size))
    assert(is_int(mem_size))
    assert(is_mem_size(mem_size))
    if reg_size == mem_size:
        return 'rm%d' % (reg_size,)
    else:
        return 'r%dm%d' % (reg_size, mem_size,)

class Operand:
    def arch_specific(self, arch):
        return self

    def warning(self):
        return None

class Operand_Class_RegMem_Memory(Operand):
    def arch_specific(self, arch):
        # This should only be called when the operand isn't specialized yet.
        assert(self.address_size == None)
        address_size = get_native_size(arch)
        return self.__class__(self.reg_size, self.mem_size, address_size)

class Operand_SpecificRegister(Operand):
    def __init__(self, name):
        self.name = name.lower()

    def __str__(self):
        return '%s' % (self.name,)

    def c_parameters(self):
        return None

    def c_name(self):
        return self.name

class Operand_Moffset(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[addr%s]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        # This should only be called when the operand isn't specialized yet.
        assert(self.address_size == None)
        address_size = get_native_size(arch)
        return Operand_Moffset(self.mem_size, address_size)

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_Moffset(self.address_size),)

    def c_name(self):
        return 'moffset%d' % (self.mem_size,)

class Operand_Imm(Operand):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'imm%d' % (self.size,)

    def c_parameters(self):
        return (CGen_Parameter_Imm(self.size),)

    def c_name(self):
        return 'imm%d' % (self.size,)

class Operand_Reg(Operand):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'reg%d' % (self.size,)

    def c_parameters(self):
        return (CGen_Parameter_Reg(self.size),)

    def c_name(self):
        return 'reg%d' % (self.size,)

class Operand_SegReg(Operand):
    def __str__(self):
        return 'segReg'

    def c_parameters(self):
        return (CGen_Parameter_SegReg(),)

    def c_name(self):
        return 'segReg'

class Operand_RegMem_Reg(Operand):
    def __init__(self, reg_size, mem_size):
        self.reg_size = reg_size
        self.mem_size = mem_size

    def __str__(self):
        return 'reg%d' % (self.reg_size,)

    def c_parameters(self):
        return (CGen_Parameter_RmReg(self.reg_size),)

    def c_name(self):
        return '%sreg%d' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.reg_size,
        )

class Operand_RegMem_AtReg(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def warning(self):
        return 'rm_reg can\'t be rSP or rBP.'

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_RmReg(self.address_size),)

    def c_name(self):
        assert(self.address_size != None)
        return '%satreg%d' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size
        )

class Operand_RegMem_AtRipPlusDisp32(Operand):
    def __init__(self, mem_size):
        self.mem_size = mem_size
        self.address_size = get_native_size(ARCH_AMD64)

    def __str__(self):
        return '%s[rIP + disp32]' % (size_to_word(self.mem_size),)

    def c_parameters(self):
        return (CGen_Parameter_Disp(32),)

    def c_name(self):
        assert(self.address_size != None)
        return '%satripplusdisp32' % (c_name_rm(64, self.mem_size),)

class Operand_RegMem_AtDisp32(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[disp32]' % (size_to_word(self.mem_size),)

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_Disp(32),)

    def c_name(self):
        assert(self.address_size != None)
        return '%satdisp32' % (c_name_rm(self.reg_size, self.mem_size),)

class Operand_RegMem_AtRegPlusDisp8(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + disp8]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def warning(self):
        return 'rm_reg can\'t be rSP.'

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_RmReg(self.address_size),
            CGen_Parameter_Disp(8),
        )

    def c_name(self):
        assert(self.address_size != None)
        return '%satreg%dplusdisp8' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size,
        )

class Operand_RegMem_AtRegPlusDisp32(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + disp32]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def warning(self):
        return 'rm_reg can\'t be rSP.'

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_RmReg(self.address_size),
            CGen_Parameter_Disp(32),
        )

    def c_name(self):
        assert(self.address_size != None)
        return '%satreg%dplusdisp32' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size,
        )

class Operand_RegMem_AtScaleIndexBase(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_Base(self.address_size),
            CGen_Parameter_Index(self.address_size),
            CGen_Parameter_Scale(),
        )

    def c_name(self):
        assert(self.address_size != None)
        return '%satbasereg%dindexreg%dscale' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size,
            self.address_size,
        )

class Operand_RegMem_AtScaleIndexBaseDisp8(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale + disp8]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_Base(self.address_size),
            CGen_Parameter_Index(self.address_size),
            CGen_Parameter_Scale(),
            CGen_Parameter_Disp(8),
        )

    def c_name(self):
        assert(self.address_size != None)
        return '%satbasereg%dindexreg%dscaledisp8' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size,
            self.address_size,
        )

class Operand_RegMem_AtScaleIndexBaseDisp32(Operand_Class_RegMem_Memory):
    def __init__(self, reg_size, mem_size, address_size = None):
        self.reg_size = reg_size
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale + disp32]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_Base(self.address_size),
            CGen_Parameter_Index(self.address_size),
            CGen_Parameter_Scale(),
            CGen_Parameter_Disp(32),
        )

    def c_name(self):
        assert(self.address_size != None)
        return '%satbasereg%dindexreg%dscaledisp32' % (
            c_name_rm(self.reg_size, self.mem_size),
            self.address_size,
            self.address_size,
        )

class Operand_RegMem:
    def __init__(self, sizes):
        self.reg_size = sizes[0]
        self.mem_size = sizes[1]

    def __str__(self):
        return 'reg%d/mem%d' % (self.reg_size, self.mem_size)

    def modrm_split(self, arch):
        result = (
            Operand_RegMem_Reg(self.reg_size, self.mem_size),
            Operand_RegMem_AtReg(self.mem_size, self.mem_size),
        )
        if arch == ARCH_I386:
            result += (Operand_RegMem_AtDisp32(self.mem_size, self.mem_size),)
        else:
            result += (Operand_RegMem_AtRipPlusDisp32(self.mem_size),)
        result += (
            Operand_RegMem_AtRegPlusDisp8(self.mem_size, self.mem_size),
            Operand_RegMem_AtRegPlusDisp32(self.mem_size, self.mem_size),
            Operand_RegMem_AtScaleIndexBase(self.mem_size, self.mem_size),
            Operand_RegMem_AtScaleIndexBaseDisp8(self.mem_size, self.mem_size),
            Operand_RegMem_AtScaleIndexBaseDisp32(self.mem_size, self.mem_size),
        )
        return result

regmems = {
    'reg/mem8': ((8, 8), Operand_RegMem),
    'reg/mem16': ((16, 16), Operand_RegMem),
    'reg/mem32': ((32, 32), Operand_RegMem),
    'reg/mem64': ((64, 64), Operand_RegMem),
}

# Opcode #######################################################################

def is_class_opcode_modrm(x):
    return issubclass(x, Opcode_ModRm)

class Opcode:
    def arch_specific(self, arch):
        return self

class Opcode_Byte(Opcode):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        self.value = value

    def __str__(self):
        return '%02x' % (self.value,)

    def c_output_components(self):
        return (CGen_Output_Component_Byte(self.value),)

class Opcode_Moffset:
    def __init__(self, address_size = None):
        self.address_size = address_size

    def __str__(self):
        return 'moffset%s' % (
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Opcode_Moffset(addr_size)

    def c_output_components(self):
        assert(self.address_size != None)
        return (CGen_Output_Component_Moffset(self.address_size),)

class Opcode_BytePlusReg(Opcode):
    def __init__(self, value, size):
        assert(is_int(value))
        assert(is_byte_value(value))
        assert(is_reg_size(size))
        self.value = value
        self.size = size

    def __str__(self):
        return '%02x+r' % (self.value, self.size,)

    def c_output_components(self):
        return (CGen_Output_Component_BytePlusReg(self.value),)

class Opcode_ModRm_Reg(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_Reg(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (CGen_Output_Component_ModRm_Reg(self.reg_value),)

class Opcode_ModRm_AtReg(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtReg(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (CGen_Output_Component_ModRm_AtReg(self.reg_value),)

class Opcode_ModRm_AtRipPlusDisp32(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtRipPlusDisp32(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtRipPlusDisp32(self.reg_value),
            CGen_Output_Component_Disp(32),
        )

class Opcode_ModRm_AtDisp32(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtDisp32(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtDisp32(self.reg_value),
            CGen_Output_Component_Disp(32),
        )

class Opcode_ModRm_AtRegPlusDisp8(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtRegPlusDisp8(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtRegPlusDisp8(self.reg_value),
            CGen_Output_Component_Disp(8),
        )

class Opcode_ModRm_AtRegPlusDisp32(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtRegPlusDisp32(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtRegPlusDisp32(self.reg_value),
            CGen_Output_Component_Disp(32),
        )

class Opcode_ModRm_AtScaleIndexBase(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtScaleIndexBase(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtScaleIndexBase(self.reg_value),
            CGen_Output_Component_Sib(),
        )

class Opcode_ModRm_AtScaleIndexBaseDisp8(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtScaleIndexBaseDisp8(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtScaleIndexBaseDisp8(self.reg_value),
            CGen_Output_Component_Sib(),
            CGen_Output_Component_Disp(8),
        )

class Opcode_ModRm_AtScaleIndexBaseDisp32(Opcode):
    def __init__(self, reg_value):
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM_AtScaleIndexBaseDisp32(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def c_output_components(self):
        return (
            CGen_Output_Component_ModRm_AtScaleIndexBaseDisp32(self.reg_value),
            CGen_Output_Component_Sib(),
            CGen_Output_Component_Disp(32),
        )

class Opcode_ModRm:
    def __init__(self, reg_value):
        if reg_value != None:
            assert(is_int(reg_value))
            assert(reg_value in (0, 1, 2, 3, 4, 5, 6, 7))
        self.reg_value = reg_value

    def __str__(self):
        return 'ModRM(%s)' % ('default' if self.reg_value == None else str(self.reg_value))

    def modrm_split(self, arch):
        return (
            Opcode_ModRm_Reg(self.reg_value),
            Opcode_ModRm_AtReg(self.reg_value),
            Opcode_ModRm_AtDisp32(self.reg_value) if arch == ARCH_I386 else Opcode_ModRm_AtRipPlusDisp32(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp8(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp32(self.reg_value),
            Opcode_ModRm_AtScaleIndexBase(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp8(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp32(self.reg_value),
        )

class Opcode_ModRmNoReg(Opcode_ModRm):
    def __init__(self, reg_value):
        super().__init__(reg_value)

    def modrm_split(self, arch):
        return (
            Opcode_ModRm_AtReg(self.reg_value),
            Opcode_ModRm_AtDisp32(self.reg_value) if arch == ARCH_I386 else Opcode_ModRm_AtRipPlusDisp32(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp8(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp32(self.reg_value),
            Opcode_ModRm_AtScaleIndexBase(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp8(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp32(self.reg_value),
        )

class Opcode_ModRmNoMem(Opcode_ModRm):
    def __init__(self, reg_value):
        super().__init__(reg_value)

    def modrm_split(self, arch):
        return (
            Opcode_ModRm_Reg(self.reg_value),
        )

class Opcode_Imm(Opcode):
    def __init__(self, size):
        assert(is_imm_size(size))
        self.size = size

    def __str__(self):
        return 'imm%d' % (self.size,)

    def c_output_components(self):
        return (CGen_Output_Component_Imm(self.size),)

class Opcode_Prefix_OperandSizeOverride:
    def __str__(self):
        return '0x66'

    def c_output_components(self):
        return (CGen_Output_Component_Prefix_OperandSizeOverride(),)

class Opcode_Prefix_RexW:
    def __str__(self):
        return 'REX.W'

    def c_output_components(self):
        return (CGen_Output_Component_Prefix_RexW(),)

modrms = {
    '/r': (None, Opcode_ModRm),
    '/0': (0, Opcode_ModRm),
    '/1': (1, Opcode_ModRm),
    '/2': (2, Opcode_ModRm),
    '/3': (3, Opcode_ModRm),
    '/4': (4, Opcode_ModRm),
    '/5': (5, Opcode_ModRm),
    '/6': (6, Opcode_ModRm),
    '/7': (7, Opcode_ModRm),
}

# Parsing ######################################################################

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

# The rest #####################################################################

def split_modrm(arch, operands, opcodes, modrm_operand_idx, modrm_opcode_idx):
    result = []
    operands_variants = operands[modrm_operand_idx].modrm_split(arch)
    opcodes_variants = opcodes[modrm_opcode_idx].modrm_split(arch)
    # Return the operand and opcode sets with different variants of
    # ModRM-related component.
    # There must the same amount of ModRM operand and opcode variants.
    assert(len(operands_variants) == len(opcodes_variants))
    for i in range(len(operands_variants)):
        result.append((
            (
                operands[:modrm_operand_idx] +
                [operands_variants[i]] +
                operands[modrm_operand_idx + 1:]
            ),
            (
                opcodes[:modrm_opcode_idx] +
                [opcodes_variants[i]] +
                opcodes[modrm_opcode_idx + 1:]
            )
        ))
    # Here we go.
    return tuple(result)

def arch_specific(arch, operands, opcodes, op_size):
    operands = tuple(
        [operand.arch_specific(arch) for operand in operands]
    )
    opcodes = tuple(
        [opcode.arch_specific(arch) for opcode in opcodes]
    )
    if arch in (ARCH_I386, ARCH_AMD64) and op_size == 16:
        prefixes = (Opcode_Prefix_OperandSizeOverride(),)
    elif op_size == 64:
        prefixes = (Opcode_Prefix_RexW(),)
    else:
        prefixes = tuple()
    return operands, prefixes + opcodes

def generate_generator(arch, name, operands, opcodes):
    def get_mnemonic(name, operands):
        if len(operands) == 0:
            return name
        return '%s %s' % (name, ', '.join(
            [str(operand) for operand in operands]
        ))

    def get_warnings(operands):
        return without_nones([ operand.warning() for operand in operands])

    def get_comment(mnemonic, warnings):
        c_warnings = ''
        for warning in warnings:
            c_warnings += '\n * @warning %s' % (warning,)
        return '/* %s%s */' % (mnemonic, c_warnings)

    def get_parameters(operands):
        parameterss = without_nones(tuple(
            [operand.c_parameters() for operand in operands]
        ))
        parameters = tuple()
        for parameters_it in parameterss:
            parameters += parameters_it
        return CGen_Parameters(parameters)

    def get_output(opcodes):
        outputss = tuple(
            [opcode.c_output_components() for opcode in opcodes]
        )
        outputs = tuple()
        for outputs_it in outputss:
            outputs += outputs_it
        return CGen_Output(outputs)

    def get_function_name(arch, name, operands):
        return '%s_%s%s' % (arch, name, '_%s' % ('_'.join(
            [operand.c_name() for operand in operands]
        ),) if len(operands) != 0 else '')

    mnemonic = get_mnemonic(name, operands)
    warnings = get_warnings(operands)
    comment = get_comment(mnemonic, warnings)
    function_name = get_function_name(arch, name, operands)
    parameters = get_parameters(operands)
    output = get_output(opcodes)
    function = CGen_Function(comment, function_name, parameters, output)
    return function

def generate_tests(arch, name, operands, opcodes, function):
    def generate_combinations(operand_test_sets, my_index):
        if my_index >= len(operand_test_sets):
            # The only combination of nothing is nothing.
            return (tuple(),)
        my_combinations = []
        my_test_values = operand_test_sets[my_index]
        for test_value in my_test_values:
            next_combinations = generate_combinations(operand_test_sets, my_index + 1)
            for combination in next_combinations:
                my_combinations.append((test_value,) + combination)
        return tuple(my_combinations)

    function_to_call = 'x86gen_%s' % (function.name,)
    out_name = 'out_%s' % (arch,)
    # Contains lists of test values for each operand.
    operand_test_sets = []
    # Skip the first parameter - it's C output destination.
    for parameter in function.parameters.parameters[1:]:
        operand_test_sets.append(parameter.test_values()[:test_values_limit])
    combinations = generate_combinations(operand_test_sets, 0)
    if len(combinations) == 0:
        return '%s(%s);\n' % (function_to_call, out_name,)
    else:
        result = ''
        for combination in combinations:
            args = ', '.join(combination)
            # FIXME: Why is this happening?
            if len(args) == 0:
                return '%s(%s);\n' % (function_to_call, out_name,)
            result += '%s(%s, %s);\n' % (function_to_call, out_name, args,)
        return result

def main():
    def entry(mnemonic, opcode, archs = (ARCH_I386, ARCH_AMD64), op_size = None):
        return (mnemonic, opcode, archs, op_size)

    def handle_entry(entry):
        mnemonic = entry[0]
        opcode = entry[1]
        archs = entry[2]
        op_size_arg = entry[3]
        # Entry parsing result.
        name, operand_strings = mnemonic_parts(mnemonic)
        opcode_parts = get_opcode_parts(opcode)
        # Generic (form-independent) operands of the instruction.
        operands = []
        # Generic (form-independent) opcodes of the instruction.
        opcodes = []
        # Index of modrm operand in operands or None if none.
        modrm_operand_idx = None
        # Index of modrm opcode in opcodes.
        modrm_opcode_idx = None
        # Reg value of ModRM byte or None if not specified.
        modrm_n = None
        # ModRM reg/mem operand reg variant size.
        modrm_reg_size = None
        # Reg operand size.
        reg_size = None
        # Existance of a moffset operand in the instruction.
        moffset_exists = None
        # Get operands, modrm_operand_idx, modrm_reg_size and reg_size.
        for operand_string in operand_strings:
            if operand_string in specifiedregs:
                reg_size = specifiedregs[operand_string]
                operands.append(Operand_SpecificRegister(operand_string))
            elif operand_string in segregs:
                operands.append(Operand_SpecificRegister(operand_string))
            elif operand_string in imms:
                operands.append(Operand_Imm(imms[operand_string]))
            elif operand_string in regmems:
                # Only one operand should be reg/mem.
                assert(modrm_operand_idx == None)
                modrm_operand_idx = len(operands)
                # The regmems table specifies constructor arguments and class.
                assert(len(regmems[operand_string]) == 2)
                params = regmems[operand_string][0]
                cls = regmems[operand_string][1]
                # The params specifies reg and mem sizes separately.
                assert(len(params) == 2)
                modrm_reg_size = params[0]
                operands.append(cls(params))
            elif operand_string in regs:
                # If there's several sources of reg size they all should
                # specify the same size.
                assert(reg_size == None or reg_size == regs[operand_string])
                reg_size = regs[operand_string]
                operands.append(Operand_Reg(regs[operand_string]))
            elif operand_string == 'segReg':
                operands.append(Operand_SegReg())
            elif operand_string in moffsets:
                # Only one moffset is possible in an instruction.
                assert(not moffset_exists)
                moffset_exists = True
                operands.append(Operand_Moffset(moffsets[operand_string]))
            else:
                raise Exception('Unknown operand kind: %s' % (operand_string,))
        # Get opcodes, modrm_opcode_idx and modrm_n.
        for opcode_part in opcode_parts:
            if is_hex_byte(opcode_part):
                value = int(opcode_part, 16)
                opcodes.append(Opcode_Byte(value))
            elif opcode_part in modrms:
                # Only one opcode should specify ModRM byte.
                assert(modrm_opcode_idx == None)
                assert(modrm_n == None)
                modrm_opcode_idx = len(opcodes)
                assert(len(modrms[opcode_part]) == 2)
                assert(is_int_or_none(modrms[opcode_part][0]))
                assert(is_class_opcode_modrm(modrms[opcode_part][1]))
                modrm_n = modrms[opcode_part][0]
                cls = modrms[opcode_part][1]
                opcodes.append(cls(modrm_n))
            elif opcode_part in is_:
                opcodes.append(Opcode_Imm(is_[opcode_part]))
            elif opcode_part in plusrs:
                # Plus-reg specifier should only happen after a byte opcode.
                assert(len(opcodes) != 0)
                assert(type(opcodes[-1]) == Opcode_Byte)
                value = opcodes[-1].value
                # Replace the byte opcode with byte-plus-reg.
                opcodes[-1] = Opcode_BytePlusReg(value, plusrs[opcode_part])
            else:
                raise Exception('Unknown opcode part: %s' % (opcode_part,))
        # Find the instruction operand size (used for adding prefixes when need).
        if op_size_arg != None:
            op_size = op_size_arg
        elif modrm_reg_size != None:
            op_size = modrm_reg_size
        elif reg_size != None:
            op_size = reg_size
        else:
            op_size = None
        # If there's moffset in the instruction - let's add it to opcode.
        if moffset_exists:
            opcodes.append(Opcode_Moffset())
        # If we have reg/mem operand we should also ModRM opcode.
        assert((modrm_operand_idx == None and modrm_opcode_idx == None) or
               (modrm_operand_idx != None and modrm_opcode_idx != None))
        # Instruction generators for each form of the instruction and each CPU.
        generators = []
        # Tests for each instruction form for each CPU.
        tests = ''
        for arch in archs:
            # If the instruction uses ModRM byte, let's split it into specific ModRM forms.
            if modrm_operand_idx != None:
                variants = split_modrm(arch, operands, opcodes, modrm_operand_idx, modrm_opcode_idx)
            else:
                variants = ((operands, opcodes),)
            # Now let's get the arch-specific instruction representations.
            for variant in variants:
                v_operands = variant[0]
                v_opcodes = variant[1]
                v_operands, v_opcodes = arch_specific(arch, v_operands, v_opcodes, op_size)
                generators.append(generate_generator(arch, name.lower(), v_operands, v_opcodes))
                if with_tests:
                    tests += generate_tests(arch, name.lower(), v_operands, v_opcodes, generators[-1])

        return ((name, operand_strings), generators, tests)

    with_tests = True if len(sys.argv) > 1 else False
    tests_file = open('tests.h', 'w')

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
        entry('ADD AL, imm8', '04 ib'),
        entry('ADD AX, imm16', '05 iw'),
        entry('ADD EAX, imm32', '05 id'),
        entry('ADD RAX, imm32', '05 id', (ARCH_AMD64,)),
        entry('ADD reg/mem8, imm8', '80 /0 ib'),
        entry('ADD reg/mem16, imm16', '81 /0 iw'),
        entry('ADD reg/mem32, imm32', '81 /0 id'),
        entry('ADD reg/mem64, imm32', '81 /0 id', (ARCH_AMD64,)),
        entry('ADD reg/mem16, imm8', '83 /0 ib'),
        entry('ADD reg/mem32, imm8', '83 /0 ib'),
        entry('ADD reg/mem64, imm8', '83 /0 ib', (ARCH_AMD64,)),
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
        entry('MOV AL, moffset8', 'A0'),
        entry('MOV AX, moffset16', 'A1'),
        entry('MOV EAX, moffset32', 'A1'),
        entry('MOV RAX, moffset64', 'A1', (ARCH_AMD64,)),
        entry('MOV moffset8, AL', 'A2'),
        entry('MOV moffset16, AX', 'A3'),
        entry('MOV moffset32, EAX', 'A3'),
        entry('MOV moffset64, RAX', 'A3', (ARCH_AMD64,)),
        entry('MOV reg8, imm8', 'B0 +rb ib'),
        entry('MOV reg16, imm16', 'B8 +rw iw'),
        entry('MOV reg32, imm32', 'B8 +rd id'),
        entry('MOV reg64, imm64', 'B8 +rq iq', (ARCH_AMD64,)),
        entry('MOV reg/mem8, imm8', 'C6 /0 ib'),
        entry('MOV reg/mem16, imm16', 'C7 /0 iw'),
        entry('MOV reg/mem32, imm32', 'C7 /0 id'),
        entry('MOV reg/mem64, imm32', 'C7 /0 id', (ARCH_AMD64,)),
        # POP
        entry('POP reg/mem16', '8F /0'),
        entry('POP reg/mem32', '8F /0', (ARCH_I386,)),
        entry('POP reg/mem64', '8F /0', (ARCH_AMD64,), 32),
        entry('POP reg16', '58 +rw'),
        entry('POP reg32', '58 +rd', (ARCH_I386,)),
        entry('POP reg64', '58 +rq', (ARCH_AMD64,), 32),
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
        entry('RET imm16', 'C2 iw'),
    )

    instructions = tuple()
    for entry in entries:
        instructions += (handle_entry(entry),)

    for instruction in instructions:
        mnemonic = instruction[0]
        generators = instruction[1]
        tests = instruction[2]
        name = mnemonic[0]
        operand_strings = mnemonic[1]
        # Print instruction family.
        print('/*\n * %s %s\n */\n' % (name.lower(), ', '.join(
            [operand_string.lower() for operand_string in operand_strings]
        )))
        for generator in generators:
            print(generator.emit(), end = '\n\n')
        if with_tests:
            tests_file.write('%s' % (tests,))


if __name__ == '__main__':
    main()
