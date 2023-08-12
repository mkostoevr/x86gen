#ifndef __MAGOMED__X86GEN_H__
#define __MAGOMED__X86GEN_H__

#ifndef X86Gen_Output
#define X86Gen_Output void *
#endif

#ifndef X86Gen_Output_Write
#define X86Gen_Output_Write(out, size, data) do { for (size_t i = 0; i < size; i++) { printf("%02x", data[i]); } } while (0)
#endif

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
  X86Gen_SegReg_ES,
  X86Gen_SegReg_CS,
  X86Gen_SegReg_SS,
  X86Gen_SegReg_DS,
  X86Gen_SegReg_FS,
  X86Gen_SegReg_GS,
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

#endif
