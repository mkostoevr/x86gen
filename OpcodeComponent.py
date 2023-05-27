from utils import *
from CFunction import *

def is_opcode_component(obj):
    return isinstance(obj, OpcodeComponent_ModRmSibDisp)

class OpcodeComponent_ModRmSibDisp:
    def variant(self, modrm, arch):
        return self

    def exists(self):
        return True

class OpcodeComponent_ModRmSibDisp_Unexisting(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return tuple()

    def exists(self):
        return False

class OpcodeComponent_ModRmSibDisp_Abstract(OpcodeComponent_ModRmSibDisp):
    def variant(self, modrm, arch):
        native_size = get_native_size(arch)
        if modrm == MODRM_VARIANT_REG:
            return OpcodeComponent_ModRmSibDisp_Reg()
        elif modrm == MODRM_VARIANT_ATREG:
            return OpcodeComponent_ModRmSibDisp_AtReg()
        elif modrm == MODRM_VARIANT_ATDISP32:
            return OpcodeComponent_ModRmSibDisp_AtDisp32()
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP8:
            return OpcodeComponent_ModRmSibDisp_AtRegPlusDisp(8)
        elif modrm == MODRM_VARIANT_ATREGPLUSDISP32:
            return OpcodeComponent_ModRmSibDisp_AtRegPlusDisp(32)
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASE:
            return OpcodeComponent_ModRmSibDisp_AtScaleIndexBase()
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP8:
            return OpcodeComponent_ModRmSibDisp_AtScaleIndexBaseDisp8()
        elif modrm == MODRM_VARIANT_ATSCALEINDEXBASEDISP32:
            return OpcodeComponent_ModRmSibDisp_AtScaleIndexBaseDisp32()
        else:
            raise 'Error: Unknown modrm variant: %s' % (modrm,)

class OpcodeComponent_ModRmSibDisp_AtScaleIndexBase(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
        )

class OpcodeComponent_ModRmSibDisp_AtScaleIndexBaseDisp8(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
            CFunction_Opcode_Disp(8),
        )

class OpcodeComponent_ModRmSibDisp_AtScaleIndexBaseDisp32(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_ScaleIndexBase(),
            CFunction_Opcode_Sib(),
            CFunction_Opcode_Disp(32),
        )

class OpcodeComponent_ModRmSibDisp_AtDisp32(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_Disp32(),
            CFunction_Opcode_Disp(32),
        )

class OpcodeComponent_ModRmSibDisp_Reg(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_Reg(),
        )

class OpcodeComponent_ModRmSibDisp_AtReg(OpcodeComponent_ModRmSibDisp):
    def opcodes(self):
        return (
            CFunction_Opcode_ModRm_AtReg(),
        )

class OpcodeComponent_ModRmSibDisp_AtRegPlusDisp(OpcodeComponent_ModRmSibDisp):
    def __init__(self, rm_disp_size):
        self.rm_disp_size = rm_disp_size

    def opcodes(self):
        return (
            cfunction_opcode_modrm_atregplusdisp(self.rm_disp_size),
            CFunction_Opcode_Disp(self.rm_disp_size),
        )
