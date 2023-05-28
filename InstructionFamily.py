from utils import *
from Instruction import *

def is_instructionfamily_parameter(x):
    return isinstance(x, InstructionFamily_Parameter)

def is_instructionfamily_parameters(x):
    return isinstance(x, InstructionFamily_Parameters)

def is_instructionfamily_opcode_component(x):
    return isinstance(x, InstructionFamily_Opcode_Component)

def is_instructionfamily_opcode(x):
    return isinstance(x, InstructionFamily_Opcode)

class InstructionFamily_Opcode_Component:
    def __init__(self):
        self.modrm = None
        self.modrm_n = None

class InstructionFamily_Opcode_Component_ModRm(InstructionFamily_Opcode_Component):
    def __init__(self):
        super().__init__()
        self.modrm = True

    def create_instruction_modrm_opcodes(self, modrm_variant, modrm_size, native_size):
        if modrm_variant == MODRM_VARIANT_REG:
            return (
                Instruction_Opcode_Component_ModRm_Reg(modrm_size),
            )
        elif modrm_variant == MODRM_VARIANT_ATREG:
            return (
                Instruction_Opcode_Component_ModRm_AtReg(modrm_size, native_size),
            )
        elif modrm_variant == MODRM_VARIANT_ATDISP32:
            return (
                Instruction_Opcode_Component_ModRm_AtDisp32(modrm_size),
                Instruction_Opcode_Component_Disp(32),
            )
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP8:
            return (
                Instruction_Opcode_Component_ModRm_AtRegPlusDisp(modrm_size, native_size, 8),
                Instruction_Opcode_Component_Disp(8),
            )
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP32:
            return (
                Instruction_Opcode_Component_ModRm_AtRegPlusDisp(modrm_size, native_size, 32),
                Instruction_Opcode_Component_Disp(32),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASE:
            return (
                Instruction_Opcode_Component_ModRm_AtScaleIndexBase(modrm_size),
                Instruction_Opcode_Component_Sib(),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return (
                Instruction_Opcode_Component_ModRm_AtScaleIndexBaseDisp(modrm_size, 8),
                Instruction_Opcode_Component_Sib(),
                Instruction_Opcode_Component_Disp(8),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return (
                Instruction_Opcode_Component_ModRm_AtScaleIndexBaseDisp(modrm_size, 32),
                Instruction_Opcode_Component_Sib(),
                Instruction_Opcode_Component_Disp(32),
            )
        else:
            raise Exception('Unknown ModRM variant: %s' % (modrm_variant,))

class InstructionFamily_Opcode_Component_RN(InstructionFamily_Opcode_Component_ModRm):
    def __init__(self, n):
        assert(is_int(n))
        assert(n >= 0 and n <= 7)
        super().__init__()
        self.modrm_n = n

class InstructionFamily_Opcode_Component_R(InstructionFamily_Opcode_Component_ModRm):
    def __init__(self):
        super().__init__()

class InstructionFamily_Opcode_Component_Byte(InstructionFamily_Opcode_Component):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        super().__init__()
        self.value = value

    def create_instruction_opcodes(self):
        return Instruction_Opcode_Component_Byte(self.value)

class InstructionFamily_Opcode:
    def __init__(self, components):
        assert(is_tuple(components))
        for component in components:
            assert(is_instructionfamily_opcode_component(component))
        self.modrm = the_only_if_any_in(
            [component.modrm for component in components]
        )
        self.modrm_n = the_only_if_any_in(
            [component.modrm_n for component in components]
        )
        self.components = components

    def split(self):
        raw = []
        modrm = None
        for component in self.components:
            if component.modrm == None:
                raw.append(component)
            else:
                modrm = component
        return tuple(raw), modrm

class InstructionFamily_Parameter:
    def __init__(self):
        self.rm_size = None
        self.reg_size = None

class InstructionFamily_Parameter_Reg(InstructionFamily_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        super().__init__()
        self.reg_size = size

    def create_instruction_modrm_parameters(self, modrm_variant, modrm_size, native_size):
        return (Instruction_Parameter_Reg(self.reg_size),)

    # FIXME: Ad-hoc, should be refactored.
    def create_mnemonic_operand(self, modrm_variant, modrm_size, native_size):
        return 'reg%d' % (self.reg_size,)

    # FIXME: Ad-hoc, should be refactored.
    def create_c_name(self, modrm_variant, modrm_size, native_size):
        return 'reg%d' % (self.reg_size,)

class InstructionFamily_Parameter_RegMem(InstructionFamily_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        super().__init__()
        self.rm_size = size

    def create_instruction_modrm_parameters(self, modrm_variant, modrm_size, native_size):
        if modrm_variant == MODRM_VARIANT_REG:
            return (
                Instruction_Parameter_RmReg(modrm_size),
            )
        elif modrm_variant == MODRM_VARIANT_ATREG:
            return (
                Instruction_Parameter_RmReg(native_size),
            )
        elif modrm_variant == MODRM_VARIANT_ATDISP32:
            return (
                Instruction_Parameter_Disp(32),
            )
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP8:
            return (
                Instruction_Parameter_RmReg(native_size),
                Instruction_Parameter_Disp(8),
            )
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP32:
            return (
                Instruction_Parameter_RmReg(native_size),
                Instruction_Parameter_Disp(32),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASE:
            return (
                Instruction_Parameter_Base(native_size),
                Instruction_Parameter_Index(native_size),
                Instruction_Parameter_Scale(),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return (
                Instruction_Parameter_Base(native_size),
                Instruction_Parameter_Index(native_size),
                Instruction_Parameter_Scale(),
                Instruction_Parameter_Disp(8),
            )
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return (
                Instruction_Parameter_Base(native_size),
                Instruction_Parameter_Index(native_size),
                Instruction_Parameter_Scale(),
                Instruction_Parameter_Disp(32),
            )
        else:
            raise Exception('Unknown ModRM variant: %s' % (modrm_variant,))

    # FIXME: Ad-hoc, should be refactored.
    def create_mnemonic_operand(self, modrm_variant, modrm_size, native_size):
        modrm_size_word = size_to_word(modrm_size)
        if modrm_variant == MODRM_VARIANT_REG:
            return 'reg%d' % (modrm_size,)
        elif modrm_variant == MODRM_VARIANT_ATREG:
            return '%s[reg%d]' % (modrm_size_word, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATDISP32:
            return '%s[disp32]' % (modrm_size_word,)
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP8:
            return '%s[reg%d + disp8]' % (modrm_size_word, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP32:
            return '%s[reg%d + disp32]' % (modrm_size_word, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASE:
            return '%s[reg%d + reg%d * scale]' % (modrm_size_word, native_size, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return '%s[reg%d + reg%d * scale + disp8]' % (modrm_size_word, native_size, native_size)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return '%s[reg%d + reg%d * scale + disp32]' % (modrm_size_word, native_size, native_size)
        else:
            raise Exception('Unknown ModRM variant: %s' % (modrm_variant,))

    # FIXME: Ad-hoc, should be refactored.
    def create_c_name(self, modrm_variant, modrm_size, native_size):
        if modrm_variant == MODRM_VARIANT_REG:
            return 'rm%dreg%d' % (modrm_size, modrm_size,)
        elif modrm_variant == MODRM_VARIANT_ATREG:
            return 'rm%datreg%d' % (modrm_size, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATDISP32:
            return 'rm%datdisp32' % (modrm_size,)
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP8:
            return 'rm%datreg%dplusdisp8' % (modrm_size, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATREGPLUSDISP32:
            return 'rm%datreg%dplusdisp32' % (modrm_size, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASE:
            return 'rm%datbasereg%dindexreg%dscale' % (modrm_size, native_size, native_size,)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return 'rm%datbasereg%dindexreg%dscaledisp8' % (modrm_size, native_size, native_size)
        elif modrm_variant == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return 'rm%datbasereg%dindexreg%dscaledisp32' % (modrm_size, native_size, native_size)
        else:
            raise Exception('Unknown ModRM variant: %s' % (modrm_variant,))

class InstructionFamily_Parameters:
    def __init__(self, parameters):
        assert(is_tuple(parameters))
        for parameter in parameters:
            assert(is_instructionfamily_parameter(parameter))
        # Only one parameter can be reg/memX.
        self.rm_size = the_only_if_any_in(
            [parameter.rm_size for parameter in parameters]
        )
        # Only one parameter can be regX.
        self.reg_size = the_only_if_any_in(
            [parameter.reg_size for parameter in parameters]
        )
        self.parameters = parameters

    def create_instruction_modrm_parameters(self, modrm_variant, modrm_size, native_size):
        result = tuple()
        for parameter in self.parameters:
            result += parameter.create_instruction_modrm_parameters(
                modrm_variant,
                modrm_size,
                native_size
            )
        return result

    def create_mnemonic_comment(self, name, modrm_variant, modrm_size, native_size):
        mnemonic_operands = ', '.join([
            parameter.create_mnemonic_operand(modrm_variant, modrm_size, native_size)
            for parameter in self.parameters
        ])
        c_name_parameters = '_'.join([
            parameter.create_c_name(modrm_variant, modrm_size, native_size)
            for parameter in self.parameters
        ])
        return '%s %s' % (name, mnemonic_operands,), '%s_%s' % (name, c_name_parameters,)

class InstructionFamily:
    def __init__(self, name, parameters, opcode, archs):
        assert(is_str(name))
        assert(is_instructionfamily_parameters(parameters))
        assert(is_instructionfamily_opcode(opcode))
        assert(is_tuple(archs))
        for arch in archs:
            assert(is_arch(arch))
        # If there's reg/memX in parameters there must be either /r or /N in opcodes.
        # If there's no reg/memX in parameters there must be no /r nor /N in opcodes.
        assert(both_or_none(parameters.rm_size, opcode.modrm))
        self.modrm = opcode.modrm
        self.modrm_n = opcode.modrm_n
        self.modrm_size = parameters.rm_size
        self.name = name.lower()
        self.parameters = parameters
        self.opcode = opcode
        self.archs = archs

    def generate(self):
        for arch in self.archs:
            if self.modrm:
                prefix_oso = None
                prefix_rex_w = None
                if self.modrm_size == 16 and arch in (ARCH_I386, ARCH_AMD64):
                    prefix_oso = Instruction_Opcode_Component_Prefix_OperandSizeOverride()
                elif self.modrm_size == 64:
                    # Only can use reg/mem64 on AMD64-compatible CPUs.
                    assert(arch == ARCH_AMD64)
                    prefix_rex_w = Instruction_Opcode_Component_Prefix_RexW()
                prefixes = without_nones((prefix_oso, prefix_rex_w))
                raw_components, modrm_component = self.opcode.split()
                raw_components_opcodes = tuple(
                    [
                        raw_component.create_instruction_opcodes()
                        for raw_component in raw_components
                    ]
                )
                # If we are here that means the instruction is ModRM.
                assert(modrm_component != None)
                for modrm_variant in modrm_variants:
                    modrm_opcodes = modrm_component.create_instruction_modrm_opcodes(
                        modrm_variant,
                        self.modrm_size,
                        get_native_size(arch)
                    )
                    opcodes = prefixes + raw_components_opcodes + modrm_opcodes
                    parameters = self.parameters.create_instruction_modrm_parameters(
                        modrm_variant,
                        self.modrm_size,
                        get_native_size(arch)
                    )
                    mnemonic_comment, c_name = self.parameters.create_mnemonic_comment(
                        self.name,
                        modrm_variant,
                        self.modrm_size,
                        get_native_size(arch)
                    )
                    # FIXME: Ad-hoc, should be refactored.
                    c_name = '%s_%s' % (arch, c_name,)
                    c_comment = '/* %s */' % (mnemonic_comment,)
                    c_parameters = CGen_Parameters(tuple(
                        [parameter.create_c_parameter() for parameter in parameters]
                    ))
                    c_output_components = tuple(
                        [opcode.create_c_output_component() for opcode in opcodes]
                    )
                    c_output = CGen_Output(c_output_components)
                    c_function = CGen_Function(c_comment, c_name, c_parameters, c_output)
                    print(c_function.emit(), '\n')
            else:
                raise Exception('Unknown instruction structure.')
