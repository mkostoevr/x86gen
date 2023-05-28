from utils import *
from CFunction import *

def is_opcode_set(obj):
    return isinstance(obj, OpcodeSet_ModRmSibDisp)

class OpcodeSet_ModRmSibDisp:
    def variant(self, modrm, arch):
        return self

    def exists(self):
        return True

class OpcodeSet_ModRmSibDisp_Unexisting(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return tuple()

    def exists(self):
        return False

class OpcodeSet_ModRmSibDisp_Abstract(OpcodeSet_ModRmSibDisp):
    def variant(self, modrm, arch):
        native_size = get_native_size(arch)
        if modrm == MODRM_VARIANT_REG:
            return OpcodeSet_ModRmSibDisp_Reg()
        elif modrm == MODRM_VARIANT_ATREG:
            return OpcodeSet_ModRmSibDisp_AtReg()
        elif modrm == MODRM_VARIANT_ATDISP32:
            return OpcodeSet_ModRmSibDisp_AtDisp32()
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP8:
            return OpcodeSet_ModRmSibDisp_AtRegPlusDisp(8)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP32:
            return OpcodeSet_ModRmSibDisp_AtRegPlusDisp(32)
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASE:
            return OpcodeSet_ModRmSibDisp_AtScaleIndexBase()
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return OpcodeSet_ModRmSibDisp_AtScaleIndexBaseDisp8()
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return OpcodeSet_ModRmSibDisp_AtScaleIndexBaseDisp32()
        else:
            raise 'Error: Unknown modrm variant: %s' % (modrm,)

class OpcodeSet_ModRmSibDisp_AtScaleIndexBase(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
        )

class OpcodeSet_ModRmSibDisp_AtScaleIndexBaseDisp8(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
            CFunction_Opcode_Disp(8),
        )

class OpcodeSet_ModRmSibDisp_AtScaleIndexBaseDisp32(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
            CFunction_Opcode_Disp(32),
        )

class OpcodeSet_ModRmSibDisp_AtDisp32(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_Disp32(),
            CFunction_Opcode_Disp(32),
        )

class OpcodeSet_ModRmSibDisp_Reg(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_Reg(),
        )

class OpcodeSet_ModRmSibDisp_AtReg(OpcodeSet_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_AtReg(),
        )

class OpcodeSet_ModRmSibDisp_AtRegPlusDisp(OpcodeSet_ModRmSibDisp):
    def __init__(self, rm_disp_size):
        self.rm_disp_size = rm_disp_size

    def opcodes(self):
        return (
            cfunction_opcode_modrm_atregplusdisp(self.rm_disp_size),
            CFunction_Opcode_Disp(self.rm_disp_size),
        )
