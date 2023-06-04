#ifndef __MAGOMED__X86GEN_H__
#define __MAGOMED__X86GEN_H__

#define X86Gen_Output void *
#define X86Gen_Output_Write(out, size, data) do { for (size_t i = 0; i < size; i++) { printf("%02x", data[i]); } } while (0)

#define X86GEN_REG8_EXPAND(WRAPPER) \
  WRAPPER(AL)                       \
  WRAPPER(CL)                       \
  WRAPPER(DL)                       \
  WRAPPER(BL)                       \
  WRAPPER(AH)                       \
  WRAPPER(CH)                       \
  WRAPPER(DH)                       \
  WRAPPER(BH)

#define X86GEN_REG16_EXPAND(WRAPPER) \
  WRAPPER(AX)                        \
  WRAPPER(CX)                        \
  WRAPPER(DX)                        \
  WRAPPER(BX)                        \
  WRAPPER(SP)                        \
  WRAPPER(BP)                        \
  WRAPPER(SI)                        \
  WRAPPER(DI)                     

#define X86GEN_REG32_EXPAND(WRAPPER) \
  WRAPPER(EAX)                       \
  WRAPPER(ECX)                       \
  WRAPPER(EDX)                       \
  WRAPPER(EBX)                       \
  WRAPPER(ESP)                       \
  WRAPPER(EBP)                       \
  WRAPPER(ESI)                       \
  WRAPPER(EDI)                     

#define X86GEN_REG64_EXPAND(WRAPPER) \
  WRAPPER(RAX)                       \
  WRAPPER(RCX)                       \
  WRAPPER(RDX)                       \
  WRAPPER(RBX)                       \
  WRAPPER(RSP)                       \
  WRAPPER(RBP)                       \
  WRAPPER(RSI)                       \
  WRAPPER(RDI)                     

enum X86Gen_Reg8 {
  #define X86GEN_ENTRY(x) X86Gen_Reg8_ ## x,
  X86GEN_REG8_EXPAND(X86GEN_ENTRY)
  #undef X86GEN_ENTRY
};

enum X86Gen_Reg16 {
  #define X86GEN_ENTRY(x) X86Gen_Reg16_ ## x,
  X86GEN_REG16_EXPAND(X86GEN_ENTRY)
  #undef X86GEN_ENTRY
};

enum X86Gen_Reg32 {
  #define X86GEN_ENTRY(x) X86Gen_Reg32_ ## x,
  X86GEN_REG32_EXPAND(X86GEN_ENTRY)
  #undef X86GEN_ENTRY
};

enum X86Gen_Reg64 {
  #define X86GEN_ENTRY(x) X86Gen_Reg64_ ## x,
  X86GEN_REG64_EXPAND(X86GEN_ENTRY)
  #undef X86GEN_ENTRY
};

enum X86Gen_SegReg {
  X86Gen_SegReg_Es,
  X86Gen_SegReg_Cs,
  X86Gen_SegReg_Ss,
  X86Gen_SegReg_Ds,
  X86Gen_SegReg_Fs,
  X86Gen_SegReg_Gs,
};

#define X86GEN_ENTRY(x) #x,

static const char *const x86gen_reg8_cstr[] = {
  X86GEN_REG8_EXPAND(X86GEN_ENTRY)
};

static const char *const x86gen_reg16_cstr[] = {
  X86GEN_REG16_EXPAND(X86GEN_ENTRY)
};

static const char *const x86gen_reg32_cstr[] = {
  X86GEN_REG32_EXPAND(X86GEN_ENTRY)
};

static const char *const x86gen_reg64_cstr[] = {
  X86GEN_REG64_EXPAND(X86GEN_ENTRY)
};

#undef X86GEN_ENTRY

enum X86Gen_Scale {
  X86Gen_Scale_1 = 0,
  X86Gen_Scale_2 = 1,
  X86Gen_Scale_4 = 2,
  X86Gen_Scale_8 = 3,
};

#define X86GEN_B00 0
#define X86GEN_B01 1
#define X86GEN_B10 2
#define X86GEN_B11 3

#define X86GEN_B000 0
#define X86GEN_B001 1
#define X86GEN_B010 2
#define X86GEN_B011 3
#define X86GEN_B100 4
#define X86GEN_B101 5
#define X86GEN_B110 6
#define X86GEN_B111 7

#define X86GEN_MOD_RM(mod, reg, rm) ((mod << 6) | (reg << 3) | rm)
#define X86GEN_SIB(scale, index, base) ((scale << 6) | (index << 3) | base)

#define X86GEN_PREFIX_REX_WRXB(w, r, x, b) ((0x4 << 4) | (w << 3) | (r << 2) | (x << 1) | b)

/* 64-bit operand size. */
#define X86GEN_PREFIX_REX_W X86GEN_PREFIX_REX_WRXB(1, 0, 0, 0)

/* MOD_RM[R] extension (MSB) to access 16 regs. */
#define X86GEN_PREFIX_REX_R X86GEN_PREFIX_REX_WRXB(0, 1, 0, 0)

/* SIB[INDEX] extension (MSB) to access 16 regs. */
#define X86GEN_PREFIX_REX_X X86GEN_PREFIX_REX_WRXB(0, 0, 1, 0)

/* MOD_RM[RM], SIB[BASE] or instruction's REG fieldextension (MSB) to access 16 regs. */
#define X86GEN_PREFIX_REX_B X86GEN_PREFIX_REX_WRXB(0, 0, 0, 1)

#define X86GEN_PREFIX_OPERAND_SIZE_OVERRIDE 0x66

#define X86GEN_EXPAND_16(val) (val & 0xff), ((val & 0xff00) >> 8)
#define X86GEN_EXPAND_32(val) (val & 0xff), ((val & 0xff00) >> 8), ((val & 0xff0000) >> 16), ((val & 0xff000000) >> 24)
#define X86GEN_EXPAND_64(val) ((val & 0xff) >> 0), \
                              ((val & 0xff00) >> 8), \
                              ((val & 0xff0000) >> 16), \
                              ((val & 0xff000000) >> 24), \
                              ((val & 0xff00000000) >> 32), \
                              ((val & 0xff0000000000) >> 40), \
                              ((val & 0xff000000000000) >> 48), \
                              ((val & 0xff00000000000000) >> 56)

#define X86GEN_EMIT(...) do {                  \
  const uint8_t buf[] = { __VA_ARGS__ }; \
  X86Gen_Output_Write(out, sizeof(buf), buf);  \
} while (0)

#include "generated.h"

/* 
 * mov reg/mem8, reg8
 */

/* mov reg8, reg8 */
static void x86gen_i386_mov_rm8r_reg8(X86Gen_Output out, enum X86Gen_Reg8 src, enum X86Gen_Reg8 dst) {
  X86GEN_EMIT(0x88, X86GEN_MOD_RM(X86GEN_B11, dst, src));
}

/* mov reg/mem16, reg16 */
static void x86gen_i386_mov_rm16r_reg16(X86Gen_Output out, enum X86Gen_Reg16 src, enum X86Gen_Reg16 dst) {
  X86GEN_EMIT(X86GEN_PREFIX_OPERAND_SIZE_OVERRIDE, 0x89, X86GEN_MOD_RM(X86GEN_B11, dst, src));
}

/* mov reg/mem32, reg32 */
static void x86gen_i386_mov_rm32r_reg32(X86Gen_Output out, enum X86Gen_Reg32 src, enum X86Gen_Reg32 dst) {
  X86GEN_EMIT(0x89, X86GEN_MOD_RM(X86GEN_B11, dst, src));
}

/* mov reg/mem64, reg64 */
static void x86gen_amd64_mov_rm64r_reg64(X86Gen_Output out, enum X86Gen_Reg64 src, enum X86Gen_Reg64 dst) {
  X86GEN_EMIT(X86GEN_PREFIX_REX_W, 0x89, X86GEN_MOD_RM(X86GEN_B11, dst, src));
}

/* mov reg8, reg/mem8 */
static void x86gen_i386_mov_reg8_rm8r(X86Gen_Output out, enum X86Gen_Reg8 src, enum X86Gen_Reg8 dst) {
  X86GEN_EMIT(0x8A, X86GEN_MOD_RM(X86GEN_B11, src, dst));
}

/* mov reg16, reg/mem16 */
static void x86gen_i386_mov_reg16_rm16r(X86Gen_Output out, enum X86Gen_Reg16 src, enum X86Gen_Reg16 dst) {
  X86GEN_EMIT(X86GEN_PREFIX_OPERAND_SIZE_OVERRIDE, 0x8B, X86GEN_MOD_RM(X86GEN_B11, src, dst));
}

/* mov reg32, reg/mem32 */
static void x86gen_i386_mov_reg32_rm32r(X86Gen_Output out, enum X86Gen_Reg32 src, enum X86Gen_Reg32 dst) {
  X86GEN_EMIT(0x8B, X86GEN_MOD_RM(X86GEN_B11, src, dst));
}

/* mov reg64, reg/mem64 */
static void x86gen_amd64_mov_reg64_rm64r(X86Gen_Output out, enum X86Gen_Reg64 src, enum X86Gen_Reg64 dst) {
  X86GEN_EMIT(X86GEN_PREFIX_REX_W, 0x8B, X86GEN_MOD_RM(X86GEN_B11, src, dst));
}

#define x86gen_amd64_mov_rm8r_reg8 x86gen_i386_mov_rm8r_reg8
#define x86gen_amd64_mov_rm16r_reg16 x86gen_i386_mov_rm16r_reg16
#define x86gen_amd64_mov_rm32r_reg32 x86gen_i386_mov_rm32r_reg32
#define x86gen_amd64_mov_reg8_rm8r x86gen_i386_mov_reg8_rm8r
#define x86gen_amd64_mov_reg16_rm16r x86gen_i386_mov_reg16_rm16r
#define x86gen_amd64_mov_reg32_rm32r x86gen_i386_mov_reg32_rm32r
#define x86gen_amd64_ret x86gen_i386_ret
#define x86gen_amd64_ret_imm16 x86gen_i386_ret_imm16

#endif
