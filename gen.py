# TODO: Assert for non-valid register number for some versions of ModRm.
# TODO: Generate tests.
# TODO: Create aliases for generators with the same parameters emitting the same code.
# TODO: Store generators and other data in some objective representaion (unlike strings).
# TODO: Conditionally beautifulize the C output.

from constants import *
from CFunction import *
from ParsedOperand import *
from ParsedOpcodePart import *
from ParametersComponent import *
from OpcodeComponent import *

def generate_c_output(required_prefixes, opcodes, modrm_sib_disp):
    legacy_prefix_opcodes = tuple(
        [CFunction_Opcode_Value(prefix, 8) for prefix in required_prefixes]
    )
    instr_opcodes = tuple(
        [CFunction_Opcode_HexByte(opcode) for opcode in opcodes]
    )
    modrm_sib_disp_opcodes = modrm_sib_disp.opcodes()
    return legacy_prefix_opcodes + instr_opcodes + modrm_sib_disp_opcodes

def generate_c_parameters(parameters):
    result = [parameter.parameter() for parameter in parameters]
    return tuple(result)

def generate_comment(name, parameters):
    return '/* %s %s */' % (name, ', '.join(
        [parameter.comment() for parameter in parameters]
    ))

def generate_cfunction(arch, name, parameters, required_prefixes, opcodes, modrm_sib_disp):
    c_parameters = generate_c_parameters(parameters)
    c_output = generate_c_output(required_prefixes, opcodes, modrm_sib_disp)
    comment = generate_comment(name, parameters)
    print(CFunction(arch, name, c_parameters, c_output, comment).generate(), '\n')

def generate_modrm_variants(arch, name, parameters, opcodes, abstract_modrm_sib_disp):
    assert(is_str(arch))
    assert(is_str(name))
    assert(is_parameters_components(parameters))
    assert(is_tuple(opcodes))
    for opcode in opcodes:
        assert(is_int(opcode))
    assert(is_opcode_component(abstract_modrm_sib_disp))
    for modrm in modrm_variants:
        required_prefixes = parameters.required_prefixes(arch)
        generate_cfunction(
            arch,
            name,
            parameters.variant(modrm, arch),
            required_prefixes,
            opcodes,
            abstract_modrm_sib_disp.variant(modrm, arch)
        )

def main():
    class InstructionDefinition:
        def __init__(self, mnemonic, opcode, valid_in_i386 = True):
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
                return name, operands

            def opcode_parts(opcode):
                # Only single spaces allowed.
                assert('  ' not in opcode)
                result = []
                parts = opcode.split(' ')
                for part in parts:
                    if part == '/r':
                        result.append(ParsedOpcodePart_ModRm())
                    elif is_hex_byte(part):
                        result.append(ParsedOpcodePart_Byte(int(part, base = 16)))
                    else:
                        print('Unknown opcode part: %s' % (part,))
                        exit(1)
                return tuple(result)

            def parsed_operands(operand_strings):
                result = []
                for string in operand_strings:
                    result.append(parsed_operand(string))
                return ParsedOperands(tuple(result))

            name, operand_strings = mnemonic_parts(mnemonic)
            operands = parsed_operands(operand_strings)
            opcodes = ParsedOpcodeParts(opcode_parts(opcode))

            generic_comment = '/*\n * %s %s\n */\n' % (
                name.lower(),
                str(operands),
            )

            print(generic_comment)

            parameters = operands.parameters_components()
            raw_opcodes = opcodes.raw_part()
            modrm_sib_disp = opcodes.modrm_sib_disp()

            if valid_in_i386:
                if modrm_sib_disp.exists():
                    generate_modrm_variants(ARCH_I386, name.lower(), parameters, raw_opcodes, modrm_sib_disp)

            if modrm_sib_disp.exists():
                generate_modrm_variants(ARCH_AMD64, name.lower(), parameters, raw_opcodes, modrm_sib_disp)

    instructions = (
        # Information from mnemonic:
        # - instruction name, required for generator name.
        # - reg/mem size, required for choosing right types for parameters and for generator name.
        # - type of reg (segReg or usual reg), required for choosing right reg parameter type and for generator name.
        # - parameter order (are reg/mem parameters or reg parameter first?), required for generator name and parameters.
        InstructionDefinition('MOV reg/mem8, reg8', '88 /r'),
        InstructionDefinition('MOV reg/mem16, reg16', '89 /r'),
        InstructionDefinition('MOV reg/mem32, reg32', '89 /r'),
        InstructionDefinition('MOV reg/mem64, reg64', '89 /r', False),
        InstructionDefinition('MOV reg8, reg/mem8', '8A /r'),
        InstructionDefinition('MOV reg16, reg/mem16', '8B /r'),
        InstructionDefinition('MOV reg32, reg/mem32', '8B /r'),
        InstructionDefinition('MOV reg64, reg/mem64', '8B /r', False),
        #InstructionDefinition('MOV reg16/32/64/mem16, segReg', '8C /r'),
        #InstructionDefinition('MOV segReg, reg/mem16', '8E /r'),
        #InstructionDefinition('MOV AL, moffset8', 'A0'),
        #InstructionDefinition('MOV AX, moffset16', 'A1'),
        #InstructionDefinition('MOV EAX, moffset32', 'A1'),
        #InstructionDefinition('MOV RAX, moffset64', 'A1'),
        #InstructionDefinition('MOV moffset8, AL', 'A2'),
        #InstructionDefinition('MOV moffset16, AX', 'A3'),
        #InstructionDefinition('MOV moffset32, EAX', 'A3'),
        #InstructionDefinition('MOV moffset64, RAX', 'A3'),
        #InstructionDefinition('MOV reg8, imm8', 'B0 +rb ib'),
        #InstructionDefinition('MOV reg16, imm16', 'B8 +rw iw'),
        #InstructionDefinition('MOV reg32, imm32', 'B8 +rd id'),
        #InstructionDefinition('MOV reg64, imm64', 'B8 +rq iq'),
        #InstructionDefinition('MOV reg/mem8, imm8', 'C6 /0 ib'),
        #InstructionDefinition('MOV reg/mem16, imm16', 'C7 /0 iw'),
        #InstructionDefinition('MOV reg/mem32, imm32', 'C7 /0 id'),
        #InstructionDefinition('MOV reg/mem64, imm32', 'C7 /0 id'),
        #InstructionDefinition('', ''),
    )

if __name__ == '__main__':
    main()
