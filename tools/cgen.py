from dataclasses import dataclass
from instruction import *
from constants import *
from utils import *

# C Generator ##################################################################

@dataclass
class C_Parameter:
    name: str
    type_: str

    def __str__(self):
        return '%s %s' % (self.type_, self.name,)

def generate_c_from_instr(instr):
    def instr_c_name(instr):
        suffix = ''
        for operand in instr.operands:
            suffix += '_'
            if operand.kind in operand_kind_specified_regmems:
                suffix += ('rm%d' % (operand.size,) if operand.size == operand.mem_size
                           else 'r%dm%d' % (operand.size, operand.mem_size,))
            if operand.kind == OP_REG:
                suffix += 'reg%d' % (operand.size,)
            elif operand.kind == OP_REGMEM_REG:
                suffix += 'reg%d' % (operand.size,)
            elif operand.kind == OP_REGMEM_ATREG:
                suffix += 'mem%datreg%d' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATREGPLUSDISP8:
                suffix += 'mem%datreg%dplusdisp8' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATREGPLUSDISP32:
                suffix += 'mem%datreg%dplusdisp32' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIB:
                suffix += 'mem%datbasereg%dindexreg%dscale' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIBPLUSDISP8:
                suffix += 'mem%datbasereg%dindexreg%dscaleplusdisp8' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATSIBPLUSDISP32:
                suffix += 'mem%datbasereg%dindexreg%dscaleplusdisp32' % (
                    operand.mem_size,
                    get_native_size(instr.archs[0]),
                    get_native_size(instr.archs[0]),
                )
            elif operand.kind == OP_REGMEM_ATDISP32:
                suffix += 'mem%datdisp32' % (operand.mem_size,)
            elif operand.kind == OP_REGMEM_ATRIPPLUSDISP32:
                suffix += 'mem%datripplusdisp32' % (operand.mem_size,)
            elif operand.kind == OP_MOFFSET:
                suffix += 'moffset%d' % (operand.size,)
            elif operand.kind == OP_SPECREG:
                suffix += operand.contents.lower()
            elif operand.kind == OP_SPECSEGREG:
                suffix += operand.contents.lower()
            elif operand.kind == OP_SEGREG:
                suffix += 'segreg'
            elif operand.kind == OP_IMM:
                suffix += 'imm%d' % (operand.size,)
            else:
                raise Exception('Unsupported operand: %s' % (str(operand),))
        return 'x86gen_%s_%s%s' % (instr.archs[0], instr.name.lower(), suffix,)

    def instr_c_parameters(instr):
        lambdas = {
            OP_REG: lambda operand, arch: (
                C_Parameter('reg', 'enum X86Gen_Reg%d' % (operand.size,)),
            ),
            OP_REGMEM_REG: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (operand.size,)),
            ),
            OP_REGMEM_ATREG: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
            ),
            OP_REGMEM_ATREGPLUSDISP8: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('disp', 'int8_t',),
            ),
            OP_REGMEM_ATREGPLUSDISP32: lambda operand, arch: (
                C_Parameter('rm_reg', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('disp', 'int32_t',),
            ),
            OP_REGMEM_ATSIB: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
            ),
            OP_REGMEM_ATSIBPLUSDISP8: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
                C_Parameter('disp', 'int8_t'),
            ),
            OP_REGMEM_ATSIBPLUSDISP32: lambda operand, arch: (
                C_Parameter('sib_base', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_index', 'enum X86Gen_Reg%d' % (get_native_size(arch),)),
                C_Parameter('sib_scale', 'enum X86Gen_Scale'),
                C_Parameter('disp', 'int32_t'),
            ),
            OP_REGMEM_ATRIPPLUSDISP32: lambda operand, arch: (
                C_Parameter('disp', 'int32_t'),
            ),
            OP_REGMEM_ATDISP32: lambda operand, arch: (
                C_Parameter('disp', 'uint32_t'),
            ),
            OP_MOFFSET: lambda operand, arch: (
                C_Parameter('disp', 'uint%d_t' % (get_native_size(arch),)),
            ),
            OP_SPECREG: lambda operand, arch: tuple(),
            OP_SPECSEGREG: lambda operand, arch: tuple(),
            OP_SEGREG: lambda operand, arch: (
                C_Parameter('reg', 'enum X86Gen_SegReg'),
            ),
            OP_IMM: lambda operand, arch: (
                C_Parameter('imm', '%sint%d_t' % (
                    '' if operand.signed else 'u',
                    operand.size,
                )),
            ),
        }
        result = tuple([C_Parameter('output', 'X86Gen_Output')])
        for operand in instr.operands:
            if operand.kind in lambdas:
                result += lambdas[operand.kind](operand, instr.archs[0])
            else:
                raise Exception('Unsupported operand: %s' % (str(operand),))
        return result

    def instr_c_output(instr):
        result = []
        oi = instr.opcode_info
        if oi.prefix_operand_size_override:
            result.append('X86GEN_PREFIX_OPERAND_SIZE_OVERRIDE')
        if oi.prefix_rex_w:
            result.append('X86GEN_PREFIX_REX_W')
        for opcode_byte in oi.opcodes:
            result.append('0x%s' % (opcode_byte,))
        if oi.opcode_plus_reg:
            result[-1] += ' + reg'
        if oi.modrm:
            assert(oi.modrm_mod != None)
            result.append('X86GEN_MOD_RM(%s, %s, %s)' % (
                'X86GEN_B%s' % (format(oi.modrm_mod, '02b'),),
                'X86GEN_B%s' % (format(oi.modrm_reg, '03b'),)
                    if oi.modrm_reg != None else 'reg',
                'X86GEN_B%s' % (format(oi.modrm_rm, '03b'),)
                    if oi.modrm_rm != None else 'rm_reg',
            ))
            if oi.sib:
                result.append('X86GEN_SIB(%s, %s, %s)' % (
                    'X86GEN_B%s' % (format(oi.sib_scale, '02b'),)
                        if oi.sib_scale != None else 'sib_scale',
                    'X86GEN_B%s' % (format(oi.sib_index, '03b'),)
                        if oi.sib_index != None else 'sib_index',
                    'X86GEN_B%s' % (format(oi.sib_base, '03b'),)
                        if oi.sib_base!= None else 'sib_base',
                ))
        if oi.disp_size != None:
            if oi.disp_size != 8:
                result.append('X86GEN_EXPAND_%d(disp)' % (oi.disp_size,))
            else:
                result.append('disp')
        if oi.imm_size != None:
            if oi.imm_size != 8:
                result.append('X86GEN_EXPAND_%d(imm)' % (oi.imm_size,))
            else:
                result.append('imm')
        return tuple(result)

    def instr_mnemonic(instr):
        result = instr.name.lower()
        result += ' ' if len(instr.operands) != 0 else ''
        result += ', '.join([operand.stringify(get_native_size(instr.archs[0])) for operand in instr.operands])
        return result

    def instr_notes(instr):
        result = []
        result.append(instr_mnemonic(instr))
        for operand in instr.operands:
            if operand.kind == OP_REGMEM_ATREG:
                result.append('@warning rm_reg can\'t be rSP or rBP.')
            elif operand.kind in (OP_REGMEM_ATREGPLUSDISP8, OP_REGMEM_ATREGPLUSDISP32,):
                result.append('@warning rm_reg can\'t be rSP.')
        return tuple(result)

    def build_c_function(name, parameters, notes, c_output):
        return (
            '/* %s */\n' +
            'static void %s(\n' +
            '  %s\n'
            ') {\n' +
            '  const uint8_t buf[] = {\n' +
            '    %s\n' +
            '  };\n' +
            '  X86Gen_Output_Write(output, sizeof(buf), buf);\n' +
            '}\n'
        ) % (
            '\n * '.join(notes),
            name,
            ',\n  '.join([str(parameter) for parameter in parameters]),
            ',\n    '.join(c_output)
        )

    def instr_original_mnemonic(instr):
        result = instr.name.lower()
        result += ' ' if len(instr.operands) != 0 else ''
        result += ', '.join([(
            operand.contents if 'imm' not in operand.contents
            else operand.contents[:-1]).lower() # There's a signity in the end.
                for operand in instr.operands])
        return result

    name = instr_c_name(instr)
    parameters = instr_c_parameters(instr)
    c_output = instr_c_output(instr)
    notes = instr_notes(instr)
    c_function = build_c_function(name, parameters, notes, c_output)
    original_mnemonic = instr_original_mnemonic(instr)
    return original_mnemonic, c_function

def generate_c(instructions):
    emitted_mnemonics = set()
    for instr in instructions:
        original_mnemonic, c_function = generate_c_from_instr(instr)
        if original_mnemonic not in emitted_mnemonics:
            print('/*\n * %s\n */\n' % (original_mnemonic,))
            emitted_mnemonics.add(original_mnemonic)
        print(c_function)
