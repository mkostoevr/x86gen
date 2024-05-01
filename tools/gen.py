from dataclasses import dataclass
from database import generic_instructions
from constants import *
from utils import *
from instruction import *
from cgen import *

def main():
    def instruction_split_modrm(instr):
        def specialized_operands(new_modrm_operand_kind):
            # The stuff here is not cached for the sake of readability.
            # Find the index of the generic ModRM operand.
            for i in range(len(instr.operands)):
                if instr.operands[i].kind == OP_REGMEM:
                    modrm_i = i
                    break
            else:
                raise Exception('This can only be called with operand list containig ModRM operand.')
            # Get the generic ModRM operand.
            generic_modrm_operand = instr.operands[modrm_i]
            # Get all the previous and next generic operands.
            prev_operands = instr.operands[:modrm_i]
            next_operands = instr.operands[modrm_i + 1:]
            # Specialize the generic modrm operand.
            specialized_modrm_operand = generic_modrm_operand.dup_specialized_modrm(new_modrm_operand_kind)
            # Put it back where it was in the operand list and return it.
            return tuple(prev_operands + (specialized_modrm_operand,) + next_operands)

        def specialized_opcode_info(mod = None, rm = None, sib = False, disp = None):
            return instr.opcode_info.dup_specialize_modrm(mod = mod, rm = rm, sib = sib, disp = disp)

        def variant(archs, operand_kind, mod = None, rm = None, sib = False, disp = None):
            return (
                archs,
                specialized_operands(operand_kind),
                specialized_opcode_info(mod, rm, sib, disp),
            )

        result = []
        # If it's not a ModRM instruction - just return it.
        if not instr.opcode_info.modrm:
            return (instr,)
        # If it is - split the instruction into several with different forms of ModRM.
        # First, split operands.
        variants = (
            # reg32
            variant(ARCHS_ALL,   OP_REGMEM_REG,             mod = 0b11),
            # [reg32]
            variant(ARCHS_ALL,   OP_REGMEM_ATREG,           mod = 0b00),
            # [disp32]
            variant(ARCHS_I386,  OP_REGMEM_ATDISP32,        mod = 0b00, rm = 0b101, disp = 32),
            # [rip + disp32]
            variant(ARCHS_AMD64, OP_REGMEM_ATRIPPLUSDISP32, mod = 0b00, rm = 0b101, disp = 32),
            # [reg32 + disp8]
            variant(ARCHS_ALL,   OP_REGMEM_ATREGPLUSDISP8,  mod = 0b01, disp = 8),
            # [reg32 + disp32]
            variant(ARCHS_ALL,   OP_REGMEM_ATREGPLUSDISP32, mod = 0b10, disp = 32),
            # [base + index * scale]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIB,           mod = 0b00, rm = 0b100, sib = True),
            # [base + index * scale + disp8]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIBPLUSDISP8,  mod = 0b01, rm = 0b100, sib = True, disp = 8),
            # [base + index * scale + disp32]
            variant(ARCHS_ALL,   OP_REGMEM_ATSIBPLUSDISP32, mod = 0b10, rm = 0b100, sib = True, disp = 32),
        )
        for variant in variants:
            v_archs = variant[0]
            v_operands = variant[1]
            v_opcode_info = variant[2]
            for arch in instr.archs:
                if arch in v_archs:
                    result.append(instr.dup(operands = v_operands, opcode_info = v_opcode_info, archs = (arch,)))
        return tuple(result)

    def instruction_split_arch(instr):
        result = []
        for arch in instr.archs:
            new_opcode_info = instr.opcode_info.dup_add_prefixes(
                operand_size_override = (arch in (ARCH_AMD64, ARCH_I386,) and instr.op_size == 16),
                rex_w = (instr.op_size == 64),
            )
            result.append(instr.dup(opcode_info = new_opcode_info, archs = (arch,)))
        return tuple(result)

    def instruction_find_op_size(instr):
        if instr.op_size != None:
            return
        op_size = 0
        for operand in instr.operands:
            if operand.size > op_size:
                op_size = operand.size
        instr.op_size = op_size

    def instruction_update_opcode_info_sizes(instr):
        assert(len(instr.archs) == 1)
        if instr.opcode_info.disp_size == 0:
            instr.opcode_info.disp_size = get_native_size(instr.archs[0])

    def instruction_verify(instr):
        assert(not (instr.op_size == 64 and ARCH_AMD64 not in instr.archs))

    instructions = generic_instructions()
    pass_foreach(instructions, instruction_find_op_size)

    instructions = pass_split(instructions, instruction_split_arch)
    instructions = pass_split(instructions, instruction_split_modrm)

    # Now we know the native size of e. g. pointers.
    pass_foreach(instructions, instruction_update_opcode_info_sizes)
    pass_foreach(instructions, instruction_verify)

    generate_c(instructions)

if __name__ == '__main__':
    main()
