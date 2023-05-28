from CFunction import *

def is_parameter_set(obj):
    return isinstance(obj, ParameterSet)

def is_parameter_sets(obj):
    return isinstance(obj, ParameterSets)

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
        raise 'Unknown size: %d' % (size,)

class ParameterSet:
    def variant(self, modrm, arch):
        return self

    def required_prefixes(self, arch):
        return tuple()

class ParameterSet_ModRm_Abstract(ParameterSet):
    def __init__(self, size):
        self.size = size

    def variant(self, modrm, arch):
        native_size = get_native_size(arch)
        if modrm == MODRM_VARIANT_REG:
            return ParameterSet_ModRm_Reg(self.size, self.size)
        elif modrm == MODRM_VARIANT_ATREG:
            return ParameterSet_ModRm_AtReg(self.size, native_size)
        elif modrm == MODRM_VARIANT_ATDISP32:
            return ParameterSet_ModRm_AtDisp32(self.size)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP8:
            return ParameterSet_ModRm_AtRegPlusDisp(self.size, native_size, 8)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP32:
            return ParameterSet_ModRm_AtRegPlusDisp(self.size, native_size, 32)
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASE:
            return ParameterSet_ModRm_AtScaleIndexBase(self.size, native_size)
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return ParameterSet_ModRm_AtScaleIndexBaseDisp8(self.size, native_size)
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return ParameterSet_ModRm_AtScaleIndexBaseDisp32(self.size, native_size)
        else:
            raise 'Error: Unknown modrm variant: %s' % (modrm,)

    def required_prefixes(self, arch):
        if self.size == 16 and (arch == ARCH_I386 or arch == ARCH_AMD64):
            return ('%s_PREFIX_OPERAND_SIZE_OVERRIDE' % (PREFIX,),)
        elif self.size == 64 and arch == ARCH_AMD64:
            return ('%s_PREFIX_REX_W' % (PREFIX,),)
        return tuple()

    def __str__(self):
        return 'reg/mem%d' % (self.size,)

class ParameterSet_ModRm_Reg(ParameterSet):
    def __init__(self, rm_size, rm_reg_size):
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size

    def parameter(self):
        return CFunction_Parameter_RmReg(self.rm_size, self.rm_reg_size)

    def comment(self):
        return 'reg%d' % (self.rm_reg_size,)

class ParameterSet_ModRm_AtScaleIndexBase(ParameterSet):
    def __init__(self, rm_size, reg_size):
        self.rm_size = rm_size
        self.reg_size = reg_size

    def parameter(self):
        return CFunction_Parameter_RmAtScaleIndexBase(self.rm_size, self.reg_size)

    def comment(self):
        return '%s[reg%d + reg%d * scale]' % (
            size_to_word(self.rm_size),
            self.reg_size,
            self.reg_size,
        )

class ParameterSet_ModRm_AtScaleIndexBaseDisp8(ParameterSet):
    def __init__(self, rm_size, reg_size):
        self.rm_size = rm_size
        self.reg_size = reg_size

    def parameter(self):
        return CFunction_Parameter_RmAtScaleIndexBaseDisp8(self.rm_size, self.reg_size)

    def comment(self):
        return '%s[reg%d + reg%d * scale + disp8]' % (
            size_to_word(self.rm_size),
            self.reg_size,
            self.reg_size,
        )

class ParameterSet_ModRm_AtScaleIndexBaseDisp32(ParameterSet):
    def __init__(self, rm_size, reg_size):
        self.rm_size = rm_size
        self.reg_size = reg_size

    def parameter(self):
        return CFunction_Parameter_RmAtScaleIndexBaseDisp32(self.rm_size, self.reg_size)

    def comment(self):
        return '%s[reg%d + reg%d * scale + disp32]' % (
            size_to_word(self.rm_size),
            self.reg_size,
            self.reg_size,
        )

class ParameterSet_ModRm_AtDisp32(ParameterSet):
    def __init__(self, rm_size):
        self.rm_size = rm_size

    def parameter(self):
        return CFunction_Parameter_RmAtDisp32(self.rm_size)

    def comment(self):
        return '%s[disp32]' % (size_to_word(self.rm_size),)

class ParameterSet_ModRm_AtReg(ParameterSet):
    def __init__(self, rm_size, rm_reg_size):
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size

    def parameter(self):
        return CFunction_Parameter_RmAtReg(self.rm_size, self.rm_reg_size)

    def comment(self):
        return '%s[reg%d]' % (size_to_word(self.rm_size), self.rm_reg_size)

class ParameterSet_ModRm_AtRegPlusDisp(ParameterSet):
    def __init__(self, rm_size, rm_reg_size, rm_disp_size):
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size
        self.rm_disp_size = rm_disp_size

    def parameter(self):
        return CFunction_Parameter_RmAtRegPlusDisp(
            self.rm_size,
            self.rm_reg_size,
            self.rm_disp_size
        )

    def comment(self):
        return '%s[reg%d + disp%d]' % (size_to_word(self.rm_size), self.rm_reg_size, self.rm_disp_size)

class ParameterSet_Reg(ParameterSet):
    def __init__(self, reg_size):
        self.reg_size = reg_size

    def parameter(self):
        return CFunction_Parameter_Reg('reg', self.reg_size)

    def comment(self):
        return 'reg%d' % (self.reg_size,)

    def __str__(self):
        return 'reg%d' % (self.reg_size,)

class ParameterSets:
    def __init__(self, parameters):
        assert(is_tuple(parameters))
        for parameter in parameters:
            assert(is_parameter_set(parameter))
        self.parameters = parameters

    def variant(self, modrm, arch):
        return tuple([parameter.variant(modrm, arch) for parameter in self.parameters])

    def required_prefixes(self, arch):
        for parameter in self.parameters:
            # FIXME: Dirty hack, returns prefixes required for the first
            # operand that needs any. Need a better way to find required
            # legacy prefixes.
            prefixes = parameter.required_prefixes(arch)
            if len(prefixes) != 0:
                return prefixes
        return tuple()

    def __str__(self):
        return ', '.join(
            [str(parameter) for parameter in self.parameters]
        )
