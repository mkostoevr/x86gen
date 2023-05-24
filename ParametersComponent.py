from CFunction import *

def is_parameters_component(obj):
    return isinstance(obj, ParametersComponent)

def is_parameters_components(obj):
    return isinstance(obj, ParametersComponents)

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

class ParametersComponent:
    def variant(self, modrm, arch):
        return self

    def required_prefixes(self, arch):
        return tuple()

class ParametersComponent_ModRm_Abstract(ParametersComponent):
    def __init__(self, size):
        self.size = size

    def variant(self, modrm, arch):
        native_size = get_native_size(arch)
        if modrm == MODRM_VARIANT_REG:
            return ParametersComponent_ModRm_Reg(self.size, self.size)
        elif modrm == MODRM_VARIANT_ATREG:
            return ParametersComponent_ModRm_AtReg(self.size, native_size)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP8:
            return ParametersComponent_ModRm_AtRegPlusDisp(self.size, native_size, 8)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP32:
            return ParametersComponent_ModRm_AtRegPlusDisp(self.size, native_size, 32)
        else:
            raise 'Error: Unknown modrm variant: %s' % (modrm,)

    def required_prefixes(self, arch):
        if self.size == 16 and (arch == ARCH_I386 or arch == ARCH_AMD64):
            return ('%s_PREFIX_OPERAND_SIZE_OVERRIDE' % (PREFIX,),)
        elif self.size == 64 and arch == ARCH_AMD64:
            return ('%s_PREFIX_REX_W' % (PREFIX,),)
        return tuple()

class ParametersComponent_ModRm_Reg(ParametersComponent):
    def __init__(self, rm_size, rm_reg_size):
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size

    def parameter(self):
        return CFunction_Parameter_RmReg(self.rm_size, self.rm_reg_size)

    def comment(self):
        return 'reg%d' % (self.rm_reg_size,)

class ParametersComponent_ModRm_AtReg(ParametersComponent):
    def __init__(self, rm_size, rm_reg_size):
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size

    def parameter(self):
        return CFunction_Parameter_RmAtReg(self.rm_size, self.rm_reg_size)

    def comment(self):
        return '%s[reg%d]' % (size_to_word(self.rm_size), self.rm_reg_size)

class ParametersComponent_ModRm_AtRegPlusDisp(ParametersComponent):
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

class ParametersComponent_Reg(ParametersComponent):
    def __init__(self, reg_size):
        self.reg_size = reg_size

    def parameter(self):
        return CFunction_Parameter_Reg('reg', self.reg_size)

    def comment(self):
        return 'reg%d' % (self.reg_size,)

class ParametersComponents:
    def __init__(self, parameters):
        assert(is_tuple(parameters))
        for parameter in parameters:
            assert(is_parameters_component(parameter))
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
