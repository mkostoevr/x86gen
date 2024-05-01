from dataclasses import dataclass
from instruction import *
from constants import ARCH_I386, ARCH_AMD64
from utils import pass_transform

def generic_instructions():
    @dataclass
    class Entry:
        mnemonic: str
        opcode: str
        archs: tuple
        op_size: int

    def entry(mnemonic, opcode, archs = (ARCH_I386, ARCH_AMD64), op_size = None):
        return Entry(mnemonic, opcode, archs, op_size)

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
        # CALL (Near)
        entry('CALL rel16off', 'E8 iw'),
        entry('CALL rel32off', 'E8 id'),
        entry('CALL reg/mem16', 'FF /2'),
        entry('CALL reg/mem32', 'FF /2', (ARCH_I386,)),
        entry('CALL reg/mem64', 'FF /2', (ARCH_AMD64,)),
        # CMP
        entry('CMP AL, imm8u', '3C ib'),
        entry('CMP AX, imm16u', '3D iw'),
        entry('CMP EAX, imm32u', '3D id'),
        entry('CMP RAX, imm32u', '3D id', (ARCH_AMD64,)),
        entry('CMP reg/mem8, imm8u', '80 /7 ib'),
        entry('CMP reg/mem16, imm16u', '81 /7 iw'),
        entry('CMP reg/mem32, imm32u', '81 /7 id'),
        entry('CMP reg/mem64, imm32s', '81 /7 id', (ARCH_AMD64,)),
        entry('CMP reg/mem16, imm8s', '83 /7 ib'),
        entry('CMP reg/mem32, imm8s', '83 /7 ib'),
        entry('CMP reg/mem64, imm8s', '83 /7 ib', (ARCH_AMD64,)),
        entry('CMP reg/mem8, reg8', '38 /r'),
        entry('CMP reg/mem16, reg16', '39 /r'),
        entry('CMP reg/mem32, reg32', '39 /r'),
        entry('CMP reg/mem64, reg64', '39 /r', (ARCH_AMD64,)),
        entry('CMP reg8, reg/mem8', '3A /r'),
        entry('CMP reg16, reg/mem16', '3B /r'),
        entry('CMP reg32, reg/mem32', '3B /r'),
        entry('CMP reg64, reg/mem64', '3B /r', (ARCH_AMD64,)),
        # DAA
        entry('DAA', '27', (ARCH_I386,)),
        # DAS
        entry('DAS', '2F', (ARCH_I386,)),
        # Jcc
        entry('JO rel8off', '70 cb'),
        entry('JO rel16off', '0F 80 cw'),
        entry('JO rel32off', '0F 80 cd'),
        entry('JNO rel8off', '71 cb'),
        entry('JNO rel16off', '0F 81 cw'),
        entry('JNO rel32off', '0F 81 cd'),
        entry('JB rel8off', '72 cb'),
        entry('JB rel16off', '0F 82 cw'),
        entry('JB rel32off', '0F 82 cd'),
        entry('JC rel8off', '72 cb'),
        entry('JC rel16off', '0F 82 cw'),
        entry('JC rel32off', '0F 82 cd'),
        entry('JNAE rel8off', '72 cb'),
        entry('JNAE rel16off', '0F 82 cw'),
        entry('JNAE rel32off', '0F 82 cd'),
        entry('JNB rel8off', '73 cb'),
        entry('JNB rel16off', '0F 83 cw'),
        entry('JNB rel32off', '0F 83 cd'),
        entry('JNC rel8off', '73 cb'),
        entry('JNC rel16off', '0F 83 cw'),
        entry('JNC rel32off', '0F 83 cd'),
        entry('JAE rel8off', '73 cb'),
        entry('JAE rel16off', '0F 83 cw'),
        entry('JAE rel32off', '0F 83 cd'),
        entry('JZ rel8off', '74 cb'),
        entry('JZ rel16off', '0F 84 cw'),
        entry('JZ rel32off', '0F 84 cd'),
        entry('JE rel8off', '74 cb'),
        entry('JE rel16off', '0F 84 cw'),
        entry('JE rel32off', '0F 84 cd'),
        entry('JNZ rel8off', '75 cb'),
        entry('JNZ rel16off', '0F 85 cw'),
        entry('JNZ rel32off', '0F 85 cd'),
        entry('JNE rel8off', '75 cb'),
        entry('JNE rel16off', '0F 85 cw'),
        entry('JNE rel32off', '0F 85 cd'),
        entry('JBE rel8off', '76 cb'),
        entry('JBE rel16off', '0F 86 cw'),
        entry('JBE rel32off', '0F 86 cd'),
        entry('JNA rel8off', '76 cb'),
        entry('JNA rel16off', '0F 86 cw'),
        entry('JNA rel32off', '0F 86 cd'),
        entry('JNBE rel8off', '77 cb'),
        entry('JNBE rel16off', '0F 87 cw'),
        entry('JNBE rel32off', '0F 87 cd'),
        entry('JA rel8off', '77 cb'),
        entry('JA rel16off', '0F 87 cw'),
        entry('JA rel32off', '0F 87 cd'),
        entry('JS rel8off', '78 cb'),
        entry('JS rel16off', '0F 88 cw'),
        entry('JS rel32off', '0F 88 cd'),
        entry('JNS rel8off', '79 cb'),
        entry('JNS rel16off', '0F 89 cw'),
        entry('JNS rel32off', '0F 89 cd'),
        entry('JP rel8off', '7A cb'),
        entry('JP rel16off', '0F 8A cw'),
        entry('JP rel32off', '0F 8A cd'),
        entry('JPE rel8off', '7A cb'),
        entry('JPE rel16off', '0F 8A cw'),
        entry('JPE rel32off', '0F 8A cd'),
        entry('JNP rel8off', '7B cb'),
        entry('JNP rel16off', '0F 8B cw'),
        entry('JNP rel32off', '0F 8B cd'),
        entry('JPO rel8off', '7B cb'),
        entry('JPO rel16off', '0F 8B cw'),
        entry('JPO rel32off', '0F 8B cd'),
        entry('JL rel8off', '7C cb'),
        entry('JL rel16off', '0F 8C cw'),
        entry('JL rel32off', '0F 8C cd'),
        entry('JNGE rel8off', '7C cb'),
        entry('JNGE rel16off', '0F 8C cw'),
        entry('JNGE rel32off', '0F 8C cd'),
        entry('JNL rel8off', '7D cb'),
        entry('JNL rel16off', '0F 8D cw'),
        entry('JNL rel32off', '0F 8D cd'),
        entry('JGE rel8off', '7D cb'),
        entry('JGE rel16off', '0F 8D cw'),
        entry('JGE rel32off', '0F 8D cd'),
        entry('JLE rel8off', '7E cb'),
        entry('JLE rel16off', '0F 8E cw'),
        entry('JLE rel32off', '0F 8E cd'),
        entry('JNG rel8off', '7E cb'),
        entry('JNG rel16off', '0F 8E cw'),
        entry('JNG rel32off', '0F 8E cd'),
        entry('JNLE rel8off', '7F cb'),
        entry('JNLE rel16off', '0F 8F cw'),
        entry('JNLE rel32off', '0F 8F cd'),
        entry('JG rel8off', '7F cb'),
        entry('JG rel16off', '0F 8F cw'),
        entry('JG rel32off', '0F 8F cd'),
        # JMP (Near)
        entry('JMP rel8off', 'EB cb'),
        entry('JMP rel16off', 'E9 cw'),
        entry('JMP rel32off', 'E9 cd'),
        entry('JMP reg/mem16', 'FF /4'),
        entry('JMP reg/mem32', 'FF /4'),
        entry('JMP reg/mem64', 'FF /4', (ARCH_AMD64,)),
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
        # SUB
        entry('SUB AL, imm8u', '2C ib'),
        entry('SUB AX, imm16u', '2D iw'),
        entry('SUB EAX, imm32u', '2D id'),
        entry('SUB RAX, imm32s', '2D id', (ARCH_AMD64,)),
        entry('SUB reg/mem8, imm8u', '80 /5 ib'),
        entry('SUB reg/mem16, imm16u', '81 /5 iw'),
        entry('SUB reg/mem32, imm32u', '81 /5 id'),
        entry('SUB reg/mem64, imm32s', '81 /5 id', (ARCH_AMD64,)),
        entry('SUB reg/mem16, imm8s', '83 /5 ib'),
        entry('SUB reg/mem32, imm8s', '83 /5 ib'),
        entry('SUB reg/mem64, imm8s', '83 /5 ib', (ARCH_AMD64,)),
        entry('SUB reg/mem8, reg8', '28 /r'),
        entry('SUB reg/mem16, reg16', '29 /r'),
        entry('SUB reg/mem32, reg32', '29 /r'),
        entry('SUB reg/mem64, reg64', '29 /r', (ARCH_AMD64,)),
        entry('SUB reg8, reg/mem8', '2A /r'),
        entry('SUB reg16, reg/mem16', '2B /r'),
        entry('SUB reg32, reg/mem32', '2B /r'),
        entry('SUB reg64, reg/mem64', '2B /r', (ARCH_AMD64,)),
    )

    @dataclass
    class Entry_Decomposed:
        name: str
        operands: tuple
        opcodes: tuple
        archs: tuple
        op_size: int

    def decompose_entry(entry):
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

    def decomposed_entry_to_instruction(e):
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
                elif operand in reloffs:
                    off_size = reloffs[operand]
                    result.append(Instruction_Operand(OP_IMM, operand, off_size, signed = True))
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
                elif opcode in cs:
                    imm_size = cs[opcode]
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

        operands = instruction_operands(e.operands)
        opcode_info = instruction_opcode_info(operands, e.opcodes)
        return Instruction(e.name, operands, opcode_info, e.archs, e.op_size)

    decomposed_entries = pass_transform(entries, decompose_entry)
    return pass_transform(decomposed_entries, decomposed_entry_to_instruction)
