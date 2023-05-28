# TODO: Assert for non-valid register number for some versions of ModRm.
# TODO: Create comment about assertions.
# TODO: Generate tests.
# TODO: Create aliases for generators with the same parameters emitting the same code.
# TODO: Store generators and other data in some objective representaion (unlike strings).
# TODO: Conditionally beautifulize the C output.

from constants import *
from InstructionFamily import *

def create_instructionfamily_parameter(mnemonic_operand):
    assert(is_str(mnemonic_operand))
    if mnemonic_operand.startswith('reg/mem'):
        size = int(mnemonic_operand[len('reg/mem'):])
        return InstructionFamily_Parameter_RegMem(size)
    elif mnemonic_operand.startswith('reg'):
        size = int(mnemonic_operand[len('reg'):])
        return InstructionFamily_Parameter_Reg(size)
    else:
        raise Exception('Unknown mnemonic operand: %s' % (mnemonic_operand,))

def create_instructionfamily_parameters(mnemonic_operands):
    assert(is_tuple(mnemonic_operands))
    for mnemonic_operand in mnemonic_operands:
        assert(is_str(mnemonic_operand))
    parameters = []
    for mnemonic_operand in mnemonic_operands:
        parameters.append(create_instructionfamily_parameter(mnemonic_operand))
    return InstructionFamily_Parameters(tuple(parameters))

def create_instructionfamily_opcode_component(opcode_component):
    assert(is_str(opcode_component))
    if is_hex_byte(opcode_component):
        return InstructionFamily_Opcode_Component_Byte(int(opcode_component, 16))
    elif opcode_component == '/r':
        return InstructionFamily_Opcode_Component_R()
    else:
        raise Exception('Unknown opcode component: %s' % (opcode_component,))

def create_instructionfamily_opcode(opcode_components):
    assert(is_tuple(opcode_components))
    for opcode_component in opcode_components:
        assert(is_str(opcode_component))
    components = []
    for opcode_component in opcode_components:
        components.append(create_instructionfamily_opcode_component(opcode_component))
    return InstructionFamily_Opcode(tuple(components))

def main():
    class InstructionDefinition:
        def __init__(self, mnemonic, opcode, archs = (ARCH_I386, ARCH_AMD64)):
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

            def opcode_parts(opcode):
                # Only single spaces allowed.
                assert('  ' not in opcode)
                return tuple(opcode.split(' '))

            name, operand_strings = mnemonic_parts(mnemonic)

            generic_comment = '/*\n * %s %s\n */\n' % (
                name.lower(),
                ', '.join(operand_strings),
            )

            print(generic_comment)

            f_parameters = create_instructionfamily_parameters(operand_strings)
            f_opcode = create_instructionfamily_opcode(opcode_parts(opcode))
            f = InstructionFamily(name, f_parameters, f_opcode, archs)
            f.generate()

    instructions = (
        # ADD
        #InstructionDefinition('ADD AL, imm8', '04 ib'),
        #InstructionDefinition('ADD AX, imm16', '05 iw'),
        #InstructionDefinition('ADD EAX, imm32', '05 id'),
        #InstructionDefinition('ADD RAX, imm32', '05 id'),
        #InstructionDefinition('ADD reg/mem8, imm8', '80 /0 ib'),
        #InstructionDefinition('ADD reg/mem16, imm16', '81 /0 iw'),
        #InstructionDefinition('ADD reg/mem32, imm32', '81 /0 id'),
        #InstructionDefinition('ADD reg/mem64, imm32', '81 /0 id'),
        #InstructionDefinition('ADD reg/mem16, imm8', '83 /0 ib'),
        #InstructionDefinition('ADD reg/mem32, imm8', '83 /0 ib'),
        #InstructionDefinition('ADD reg/mem64, imm8', '83 /0 ib'),
        InstructionDefinition('ADD reg/mem8, reg8', '00 /r'),
        InstructionDefinition('ADD reg/mem16, reg16', '01 /r'),
        InstructionDefinition('ADD reg/mem32, reg32', '01 /r'),
        InstructionDefinition('ADD reg/mem64, reg64', '01 /r', (ARCH_AMD64,)),
        InstructionDefinition('ADD reg8, reg/mem8', '02 /r'),
        InstructionDefinition('ADD reg16, reg/mem16', '03 /r'),
        InstructionDefinition('ADD reg32, reg/mem32', '03 /r'),
        InstructionDefinition('ADD reg64, reg/mem64', '03 /r', (ARCH_AMD64,)),
        # MOV
        InstructionDefinition('MOV reg/mem8, reg8', '88 /r'),
        InstructionDefinition('MOV reg/mem16, reg16', '89 /r'),
        InstructionDefinition('MOV reg/mem32, reg32', '89 /r'),
        InstructionDefinition('MOV reg/mem64, reg64', '89 /r', (ARCH_AMD64,)),
        InstructionDefinition('MOV reg8, reg/mem8', '8A /r'),
        InstructionDefinition('MOV reg16, reg/mem16', '8B /r'),
        InstructionDefinition('MOV reg32, reg/mem32', '8B /r'),
        InstructionDefinition('MOV reg64, reg/mem64', '8B /r', (ARCH_AMD64,)),
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
