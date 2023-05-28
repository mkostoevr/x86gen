from utils import *
from CGen import *

class Instruction_Opcode_Component:
    pass

class Instruction_Opcode_Component_ModRm(Instruction_Opcode_Component):
    def __init__(self, mod, reg, rm):
        assert(is_str(mod))
        assert(is_str(reg))
        assert(is_str(rm))
        self.mod = mod
        self.reg = reg
        self.rm = rm

    def __str__(self):
        return 'ModRM(%s, %s, %s)' % (self.mod, self.reg, self.rm,)

    def create_c_output_component(self):
        return CGen_Output_Component_ModRm(self.mod, self.reg, self.rm)

class Instruction_Opcode_Component_ModRm_Reg(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        self.rm_size = rm_size
        super().__init__('B11', 'reg', 'rm_reg')

class Instruction_Opcode_Component_ModRm_AtReg(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size, rm_reg_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        assert(is_int(rm_reg_size))
        assert(is_reg_size(rm_reg_size))
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size
        super().__init__('B00', 'reg', 'rm_reg')

class Instruction_Opcode_Component_ModRm_AtDisp32(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        self.rm_size = rm_size
        super().__init__('B00', 'reg', 'B101')

class Instruction_Opcode_Component_ModRm_AtRegPlusDisp(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size, rm_reg_size, disp_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        assert(is_int(rm_reg_size))
        assert(is_reg_size(rm_reg_size))
        assert(is_int(disp_size))
        assert(is_disp_size(disp_size))
        self.rm_size = rm_size
        self.rm_reg_size = rm_reg_size
        self.disp_size = disp_size
        super().__init__('B01' if disp_size == 8 else 'B10', 'reg', 'rm_reg')

class Instruction_Opcode_Component_ModRm_AtScaleIndexBase(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        self.rm_size = rm_size
        super().__init__('B00', 'reg', 'B100')

class Instruction_Opcode_Component_ModRm_AtScaleIndexBaseDisp(Instruction_Opcode_Component_ModRm):
    def __init__(self, rm_size, disp_size):
        assert(is_int(rm_size))
        assert(is_reg_size(rm_size))
        assert(is_int(disp_size))
        assert(is_disp_size(disp_size))
        self.rm_size = rm_size
        self.disp_size = disp_size
        super().__init__('B01' if disp_size == 8 else 'B10', 'reg', 'B100')

class Instruction_Opcode_Component_Sib(Instruction_Opcode_Component):
    def __str__(self):
        return 'SIB'

    def create_c_output_component(self):
        return CGen_Output_Component_Sib()

class Instruction_Opcode_Component_Disp(Instruction_Opcode_Component):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_disp_size(size))
        self.size = size

    def __str__(self):
        return 'disp%d' % (self.size,)

    def create_c_output_component(self):
        return CGen_Output_Component_Disp(self.size)

class Instruction_Opcode_Component_Byte(Instruction_Opcode_Component):
    def __init__(self, value):
        assert(is_int(value))
        assert(is_byte_value(value))
        self.value = value

    def __str__(self):
        return '%02x' % (self.value,)

    def create_c_output_component(self):
        return CGen_Output_Component_Byte(self.value)

class Instruction_Opcode_Component_Prefix(Instruction_Opcode_Component):
    pass

class Instruction_Opcode_Component_Prefix_OperandSizeOverride(Instruction_Opcode_Component_Prefix):
    def __str__(self):
        return '66'

    def create_c_output_component(self):
        return CGen_Output_Component_Prefix_OperandSizeOverride()

class Instruction_Opcode_Component_Prefix_RexW(Instruction_Opcode_Component_Prefix):
    def __str__(self):
        return 'REX.W'

    def create_c_output_component(self):
        return CGen_Output_Component_Prefix_RexW()

class Instruction_Parameter:
    pass

class Instruction_Parameter_Disp(Instruction_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_disp_size(size))
        self.size = size

    def create_c_parameter(self):
        return CGen_Parameter_Disp(self.size)

class Instruction_Parameter_Reg(Instruction_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        self.size = size

    def create_c_parameter(self):
        return CGen_Parameter_Reg(self.size)

class Instruction_Parameter_RmReg(Instruction_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_reg_size(size))
        self.size = size

    def create_c_parameter(self):
        return CGen_Parameter_RmReg(self.size)

class Instruction_Parameter_Scale(Instruction_Parameter):
    def create_c_parameter(self):
        return CGen_Parameter_Scale()

class Instruction_Parameter_Index(Instruction_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_native_size(size))
        self.size = size

    def create_c_parameter(self):
        return CGen_Parameter_Index(self.size)

class Instruction_Parameter_Base(Instruction_Parameter):
    def __init__(self, size):
        assert(is_int(size))
        assert(is_native_size(size))
        self.size = size

    def create_c_parameter(self):
        return CGen_Parameter_Base(self.size)

