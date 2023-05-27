from utils import *
from constants import *

def is_cfunction_parameter(obj):
    return isinstance(obj, CFunction_Parameter)

def is_cfunction_opcode(obj):
    return isinstance(obj, CFunction_Opcode)

class CFunction_Parameter:
    pass

class CFunction_Parameter_Uint(CFunction_Parameter):
    def __init__(self, name, size):
        assert(size in (8, 16, 32, 64))

        self.name = name
        self.size = size

    def signature(self):
        return 'uint%d_t %s' % (self.size, self.name)

class CFunction_Parameter_Reg(CFunction_Parameter):
    def __init__(self, name, size):
        assert(size in (8, 16, 32, 64))

        self.name = name
        self.size = size

    def signature(self):
        return 'enum X86Gen_Reg%d %s' % (self.size, self.name)

    def name_part(self):
        return 'reg%d' % (self.size,)

class CFunction_Parameter_Scale(CFunction_Parameter):
    def __init__(self, name):
        self.name = name

    def signature(self):
        return 'enum X86Gen_Scale %s' % (self.name)

    def name_part(self):
        return 'scale'

class CFunction_Parameter_RmReg(CFunction_Parameter):
    def __init__(self, size, reg_size):
        assert(size in (8, 16, 32, 64))
        assert(reg_size in (8, 16, 32, 64))
        self.reg_size = reg_size
        self.size = size

    def signature(self):
        return CFunction_Parameter_Reg('rm_reg', self.reg_size).signature()

    def name_part(self):
        return 'rm%dreg%d' % (self.size, self.reg_size)

class CFunction_Parameter_RmAtDisp32(CFunction_Parameter):
    def __init__(self, size):
        assert(size in (8, 16, 32, 64))
        self.size = size

    def signature(self):
        return CFunction_Parameter_Uint('disp', 32).signature()

    def name_part(self):
        return 'rm%datdisp32' % (self.size)

class CFunction_Parameter_RmAtScaleIndexBase(CFunction_Parameter):
    def __init__(self, size, reg_size):
        assert(size in (8, 16, 32, 64))
        assert(reg_size in (8, 16, 32, 64))
        self.size = size
        self.reg_size = reg_size

    def signature(self):
        return ', '.join([
            CFunction_Parameter_Reg('sib_base', self.reg_size).signature(),
            CFunction_Parameter_Reg('sib_index', self.reg_size).signature(),
            CFunction_Parameter_Scale('sib_scale').signature(),
        ])

    def name_part(self):
        return 'rm%datbasereg%dindexreg%dscale' % (
            self.size,
            self.reg_size,
            self.reg_size,
        )

class CFunction_Parameter_RmAtReg(CFunction_Parameter):
    def __init__(self, size, reg_size):
        assert(size in (8, 16, 32, 64))
        assert(reg_size in (8, 16, 32, 64))
        self.reg_size = reg_size
        self.size = size
   
    def signature(self):
        return CFunction_Parameter_Reg('rm_reg', self.reg_size).signature()

    def name_part(self):
        return 'rm%datreg%d' % (self.size, self.reg_size)

class CFunction_Parameter_RmAtRegPlusDisp(CFunction_Parameter):
    def __init__(self, size, reg_size, disp_size):
        assert(size in (8, 16, 32, 64))
        assert(reg_size in (8, 16, 32, 64))
        assert(disp_size in (8, 16, 32, 64))
        self.size = size
        self.reg_size = reg_size
        self.disp_size = disp_size
   
    def signature(self):
        return ', '.join([
            CFunction_Parameter_Reg('rm_reg', self.reg_size).signature(),
            CFunction_Parameter_Uint('rm_disp', self.disp_size).signature()
        ])

    def name_part(self):
        return 'rm%datreg%dplusdisp%d' % (
            self.size,
            self.reg_size,
            self.disp_size
        )

class CFunction_Opcode:
    pass

class CFunction_Opcode_ModRm_Generic(CFunction_Opcode):
    def __init__(self, mod, reg, rm):
        assert(is_str(mod))
        assert(is_str(reg))
        assert(is_str(rm))
        self.mod = mod
        self.reg = reg
        self.rm = rm

    def emit(self):
        return '%s_MOD_RM(%s, %s, %s)' % (PREFIX, self.mod, self.reg, self.rm)

class CFunction_Opcode_ModRm_Reg(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B11' % (PREFIX,)
        reg = 'reg'
        rm = 'rm_reg'
        super().__init__(mod, reg, rm)

class CFunction_Opcode_ModRm_Disp32(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B00' % (PREFIX,)
        reg = 'reg'
        rm = '%s_B101' % (PREFIX,)
        super().__init__(mod, reg, rm)

class CFunction_Opcode_ModRm_AtReg(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B00' % (PREFIX,)
        reg = 'reg'
        rm = 'rm_reg'
        super().__init__(mod, reg, rm)

class CFunction_Opcode_ModRm_AtRegPlusDisp8(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B01' % (PREFIX,)
        reg = 'reg'
        rm = 'rm_reg'
        super().__init__(mod, reg, rm)

class CFunction_Opcode_ModRm_AtRegPlusDisp32(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B10' % (PREFIX,)
        reg = 'reg'
        rm = 'rm_reg'
        super().__init__(mod, reg, rm)

def cfunction_opcode_modrm_atregplusdisp(disp_size):
    assert(disp_size in (8, 32))
    if disp_size == 8:
        return CFunction_Opcode_ModRm_AtRegPlusDisp8()
    else:
        return CFunction_Opcode_ModRm_AtRegPlusDisp32()

class CFunction_Opcode_ModRm_ScaleIndexBase(CFunction_Opcode_ModRm_Generic):
    def __init__(self):
        mod = '%s_B00' % (PREFIX,)
        reg = 'reg'
        rm = '%s_B100' % (PREFIX,)
        super().__init__(mod, reg, rm)

class CFunction_Opcode_Sib(CFunction_Opcode):
    def emit(self):
        return '%s_SIB(sib_scale, sib_index, sib_base)' % (PREFIX,)

class CFunction_Opcode_Value(CFunction_Opcode):
    def __init__(self, name, size):
        assert(is_str(name))
        assert(is_int(size))
        assert(size in (8, 16, 32, 64))
        self.name = name
        self.size = size

    def emit(self):
        if self.size > 8:
            return 'X86GEN_EXPAND_%d(%s)' % (self.size, self.name)
        return '%s' % (self.name,)

class CFunction_Opcode_Disp(CFunction_Opcode_Value):
    def __init__(self, size):
        super().__init__('rm_disp', size)

class CFunction_Opcode_HexByte(CFunction_Opcode):
    def __init__(self, value):
        assert(value >= 0 and value <= 0xff)

        self.value = value

    def emit(self):
        return '0x%02X' % (self.value,)

class CFunction:
    def __init__(self, arch, instr_name, parameters, opcodes, comment):
        assert(is_str(arch))
        assert(is_str(instr_name))
        for parameter in parameters:
            assert(is_cfunction_parameter(parameter))
        for opcode in opcodes:
            assert(is_cfunction_opcode(opcode))
        self.arch = arch
        self.instr_name = instr_name
        self.parameters = parameters
        self.opcodes = opcodes
        self.comment = comment

    def c_function_name(self):
        parameter_parts = tuple(
            parameter.name_part() for parameter in self.parameters
        )

        prefix = 'x86gen'
        arch = self.arch
        inst_name = self.instr_name
        parameters = '_'.join(parameter_parts)
        return '%s_%s_%s_%s' % (
            prefix,
            arch,
            inst_name,
            parameters
        )

    def c_function_parameters(self):
        return ', '.join([
            parameter.signature() for parameter in self.parameters
        ])

    def c_function_outputs(self):
        return ',\n    '.join([
            opcode.emit() for opcode in self.opcodes
        ])

    def generate(self):
        return (
            '%s\n' +
            'static void %s(X86Gen_Output output, %s) {\n' +
            '  const uint8_t buf[] = {\n' +
            '    %s\n' +
            '  };\n' +
            '  X86Gen_Output_Write(output, sizeof(buf), buf);\n' +
            '}'
        ) % (
            self.comment,
            self.c_function_name(),
            self.c_function_parameters(),
            self.c_function_outputs()
        )
