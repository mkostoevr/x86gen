from constants import *
from utils import *
from CGen import *

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

# Operand ######################################################################

class Operand:
    def arch_specific(self, arch):
        return self

    def warning(self):
        return None

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
    def __init__(self, size, address_size = None):
        self.size = size
        self.address_size = address_size

    def __str__(self):
        return '%s[addr%s]' % (
            size_to_word(self.size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_Moffset(self.size, addr_size)

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_Moffset(self.address_size),)

    def c_name(self):
        return 'moffset%d' % (self.size,)

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
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'reg%d' % (self.size,)

    def c_parameters(self):
        return (CGen_Parameter_RmReg(self.size),)

    def c_name(self):
        return 'rm%dreg%d' % (self.size, self.size)

class Operand_RegMem_AtReg(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtReg(self.mem_size, addr_size)

    def warning(self):
        return 'rm_reg can\'t be rSP or rBP.'

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_RmReg(self.address_size),)

    def c_name(self):
        assert(self.address_size != None)
        return 'rm%datreg%d' % (self.mem_size, self.address_size)

class Operand_RegMem_AtDisp32(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[disp32]' % (size_to_word(self.mem_size),)

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtDisp32(self.mem_size, addr_size)

    def c_parameters(self):
        assert(self.address_size != None)
        return (CGen_Parameter_Disp(32),)

    def c_name(self):
        assert(self.address_size != None)
        return 'rm%datdisp32' % (self.mem_size)

class Operand_RegMem_AtRegPlusDisp8(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + disp8]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtRegPlusDisp8(self.mem_size, addr_size)

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
        return 'rm%datreg%dplusdisp8' % (self.mem_size, self.address_size,)

class Operand_RegMem_AtRegPlusDisp32(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + disp32]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtRegPlusDisp32(self.mem_size, addr_size)

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
        return 'rm%datreg%dplusdisp32' % (self.mem_size, self.address_size,)

class Operand_RegMem_AtScaleIndexBase(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtScaleIndexBase(self.mem_size, addr_size)

    def c_parameters(self):
        assert(self.address_size != None)
        return (
            CGen_Parameter_Base(self.address_size),
            CGen_Parameter_Index(self.address_size),
            CGen_Parameter_Scale(),
        )

    def c_name(self):
        assert(self.address_size != None)
        return 'rm%datbasereg%dindexreg%dscale' % (self.mem_size, self.address_size, self.address_size,)

class Operand_RegMem_AtScaleIndexBaseDisp8(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale + disp8]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtScaleIndexBaseDisp8(self.mem_size, addr_size)

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
        return 'rm%datbasereg%dindexreg%dscaledisp8' % (self.mem_size, self.address_size, self.address_size,)

class Operand_RegMem_AtScaleIndexBaseDisp32(Operand):
    def __init__(self, mem_size, address_size = None):
        self.mem_size = mem_size
        self.address_size = address_size

    def __str__(self):
        return '%s[reg%s + reg%s * scale + disp32]' % (
            size_to_word(self.mem_size),
            '?' if self.address_size == None else str(self.address_size),
            '?' if self.address_size == None else str(self.address_size),
        )

    def arch_specific(self, arch):
        if self.address_size == None:
            addr_size = get_native_size(arch)
            return Operand_RegMem_AtScaleIndexBaseDisp32(self.mem_size, addr_size)

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
        return 'rm%datbasereg%dindexreg%dscaledisp32' % (self.mem_size, self.address_size, self.address_size,)

class Operand_RegMem:
    def __init__(self, sizes):
        self.reg_size = sizes[0]
        self.mem_size = sizes[1]

    def __str__(self):
        return 'reg%d/mem%d' % (self.reg_size, self.mem_size)

    def modrm_split(self):
        return (
            Operand_RegMem_Reg(self.reg_size),
            Operand_RegMem_AtReg(self.mem_size),
            Operand_RegMem_AtDisp32(self.mem_size),
            Operand_RegMem_AtRegPlusDisp8(self.mem_size),
            Operand_RegMem_AtRegPlusDisp32(self.mem_size),
            Operand_RegMem_AtScaleIndexBase(self.mem_size),
            Operand_RegMem_AtScaleIndexBaseDisp8(self.mem_size),
            Operand_RegMem_AtScaleIndexBaseDisp32(self.mem_size),
        )

# Opcode #######################################################################

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

    def modrm_split(self):
        return (
            Opcode_ModRm_Reg(self.reg_value),
            Opcode_ModRm_AtReg(self.reg_value),
            Opcode_ModRm_AtDisp32(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp8(self.reg_value),
            Opcode_ModRm_AtRegPlusDisp32(self.reg_value),
            Opcode_ModRm_AtScaleIndexBase(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp8(self.reg_value),
            Opcode_ModRm_AtScaleIndexBaseDisp32(self.reg_value),
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

# The rest #####################################################################

def split_modrm(operands, opcodes, modrm_operand_idx, modrm_opcode_idx):
    result = []
    operands_variants = operands[modrm_operand_idx].modrm_split()
    opcodes_variants = opcodes[modrm_opcode_idx].modrm_split()
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
    print('%s\n' % (function.emit(),))

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
        # Print instruction family.
        print('/*\n * %s %s\n */\n' % (name.lower(), ', '.join(
            [operand_string.lower() for operand_string in operand_strings]
        )))
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
                # The regmems table specifies reg and mem size separately.
                assert(len(regmems[operand_string]) == 2)
                modrm_reg_size = regmems[operand_string][0]
                operands.append(Operand_RegMem(regmems[operand_string]))
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
                modrm_n = modrms[opcode_part]
                opcodes.append(Opcode_ModRm(modrms[opcode_part]))
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
        # If there's moffset in the instruction - let's add it to opcode.
        if moffset_exists:
            opcodes.append(Opcode_Moffset())
        # If we have reg/mem operand we should also ModRM opcode.
        assert((modrm_operand_idx == None and modrm_opcode_idx == None) or
               (modrm_operand_idx != None and modrm_opcode_idx != None))
        # If the instruction uses ModRM byte, let's split it into specific ModRM forms.
        if modrm_operand_idx != None:
            variants = split_modrm(operands, opcodes, modrm_operand_idx, modrm_opcode_idx)
        else:
            variants = ((operands, opcodes),)
        # Find the instruction operand size (used for adding prefixes when need).
        if modrm_reg_size != None:
            op_size = modrm_reg_size
        elif reg_size != None:
            op_size = reg_size
        else:
            op_size = op_size_arg
        # Generate specific instuctions for each suppored CPU.
        for arch in archs:
            for variant in variants:
                operands = variant[0]
                opcodes = variant[1]
                operands, opcodes = arch_specific(arch, operands, opcodes, op_size)
                generate_generator(arch, name.lower(), operands, opcodes)

    entries = (
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
        entry('POP reg/mem32', '8F /0'),
        entry('POP reg/mem64', '8F /0', (ARCH_AMD64,)),
        entry('POP reg16', '58 +rw'),
        entry('POP reg32', '58 +rd'),
        entry('POP reg64', '58 +rq', (ARCH_AMD64,)),
        entry('POP DS', '1F'),
        entry('POP ES', '07'),
        entry('POP SS', '17'),
        entry('POP FS', '0F A1'),
        entry('POP GS', '0F A9'),
    )

    for entry in entries:
        handle_entry(entry)

main()
