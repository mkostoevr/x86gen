from utils import *

def is_cgen_parameter(x):
    return isinstance(x, CGen_Parameter)

class CGen_Output_Component:
    pass

class CGen_Output_Component_ModRm(CGen_Output_Component):
    def __init__(self, mod, reg, rm):
        assert(is_str(mod))
        assert(is_str(reg))
        assert(is_str(rm))
        self.mod = mod if mod[0] != 'B' else '%s_%s' % (
            PREFIX,
            mod,
        )
        self.reg = reg
        self.rm = rm if rm[0] != 'B' else '%s_%s' % (
            PREFIX,
            rm,
        )

    def emit(self):
        return '%s_MOD_RM(%s, %s, %s)' % (PREFIX, self.mod, self.reg, self.rm,)

class CGen_Output_Component_Sib(CGen_Output_Component):
    def emit(self):
        return '%s_SIB(sib_scale, sib_index, sib_base)' % (PREFIX,)

class CGen_Output_Component_Disp(CGen_Output_Component):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_disp_size(size))
        self.size = size

    def emit(self):
        if self.size == 8:
            return 'disp'
        elif self.size == 32:
            return '%s_EXPAND_32(disp)' % (PREFIX,)
        else:
            raise Exception('Unknown disp size: %d' % (self.size,))

class CGen_Output_Component_Byte(CGen_Output_Component):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        self.value = value

    def emit(self):
        return '0x%02X' % (self.value,)

class CGen_Output_Component_Prefix_OperandSizeOverride(CGen_Output_Component):
    def emit(self):
        return '%s_PREFIX_OPERAND_SIZE_OVERRIDE' % (PREFIX,)

class CGen_Output_Component_Prefix_RexW(CGen_Output_Component):
    def emit(self):
        return '%s_PREFIX_REX_W' % (PREFIX,)

class CGen_Output:
    def __init__(self, components):
        self.components = components

    def emit(self):
        return CGEN_OUTPUT_COMPONENT_SEPARATOR.join(
            [component.emit() for component in self.components]
        )

class CGen_Parameter:
    pass

class CGen_Parameter_Disp(CGen_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_disp_size(size))
        self.size = size

    def emit(self):
        return 'uint%d_t disp' % (self.size,)

class CGen_Parameter_Reg(CGen_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        self.size = size

    def emit(self):
        return 'enum X86Gen_Reg%d reg' % (self.size,)

class CGen_Parameter_RmReg(CGen_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        self.size = size

    def emit(self):
        return 'enum X86Gen_Reg%d rm_reg' % (self.size,)

class CGen_Parameter_Scale(CGen_Parameter):
    def emit(self):
        return 'enum X86Gen_Scale sib_scale'

class CGen_Parameter_Index(CGen_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_native_size(size))
        self.size = size

    def emit(self):
        return 'enum X86Gen_Reg%d sib_index' % (self.size,)

class CGen_Parameter_Base(CGen_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_native_size(size))
        self.size = size

    def emit(self):
        return 'enum X86Gen_Reg%d sib_base' % (self.size,)

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

