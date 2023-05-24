#include <assert.h>
#include <stdio.h>
#include <stdint.h>

#include "x86gen.h"

#define rax X86Gen_Reg64_RAX
#define rbx X86Gen_Reg64_RBX
#define rcx X86Gen_Reg64_RCX
#define rdx X86Gen_Reg64_RDX
#define rsi X86Gen_Reg64_RSI
#define rdi X86Gen_Reg64_RDI
#define rsp X86Gen_Reg64_RSP
#define rbp X86Gen_Reg64_RBP

#define eax X86Gen_Reg32_EAX
#define ebx X86Gen_Reg32_EBX
#define ecx X86Gen_Reg32_ECX
#define edx X86Gen_Reg32_EDX
#define esi X86Gen_Reg32_ESI
#define edi X86Gen_Reg32_EDI
#define esp X86Gen_Reg32_ESP
#define ebp X86Gen_Reg32_EBP

#define ax X86Gen_Reg16_AX
#define bx X86Gen_Reg16_BX
#define cx X86Gen_Reg16_CX
#define dx X86Gen_Reg16_DX
#define si X86Gen_Reg16_SI
#define di X86Gen_Reg16_DI
#define sp X86Gen_Reg16_SP
#define bp X86Gen_Reg16_BP

#define al X86Gen_Reg8_AL
#define bl X86Gen_Reg8_BL
#define cl X86Gen_Reg8_CL
#define dl X86Gen_Reg8_DL
#define ah X86Gen_Reg8_AH
#define bh X86Gen_Reg8_BH
#define ch X86Gen_Reg8_CH
#define dh X86Gen_Reg8_DH

#define test0(x, name) do {        \
  printf(#name "\t# ");            \
  x86gen_ ## x ## _ ## name(NULL); \
  printf("\n");                    \
} while (0)

#define test1(x, name, p1, a) do {               \
  printf(#name " " #a "\t# ");                   \
  x86gen_ ## x ## _ ## name ## _ ## p1(NULL, a); \
  printf("\n");                                  \
} while (0)

#define test2(x, name, p1, p2, a, b) do {                      \
  printf(#name " " #a ", " #b "\t# ");                         \
  x86gen_ ## x ## _ ## name ## _ ## p1 ## _ ## p2(NULL, a, b); \
  printf("\n");                                                \
} while (0)

int main() {
  printf("I386:\n");

  test2(i386, mov, rm8r,  reg8,  al,  ch);
  test2(i386, mov, rm16r, reg16, si,  di);
  test2(i386, mov, rm32r, reg32, ebp, esp);

  test2(i386, mov, reg8,  rm8r,  al,  ch);
  test2(i386, mov, reg16, rm16r, si,  di);
  test2(i386, mov, reg32, rm32r, ebp, esp);

  test0(i386, ret);
  test1(i386, ret, imm16, 26);

  printf("\nAMD64:\n");

  test2(amd64, mov, rm8r,  reg8,  al,  ch);
  test2(amd64, mov, rm16r, reg16, si,  di);
  test2(amd64, mov, rm32r, reg32, ebp, esp);
  test2(amd64, mov, rm64r, reg64, rbp, rsp);

  test2(amd64, mov, reg16, rm16r, si,  di);
  test2(amd64, mov, reg8,  rm8r,  al,  ch);
  test2(amd64, mov, reg32, rm32r, ebp, esp);
  test2(amd64, mov, reg64, rm64r, rbp, rsp);

  test0(amd64, ret);
  test1(amd64, ret, imm16, 26);

  printf("\nWhatever:\n");

  test2(i386, mov, rm8r, reg8, al, al);
  test2(i386, mov, rm8atreg32, reg8, eax, al);
  x86gen_i386_mov_rm8atreg32plusdisp8_reg8(NULL, edi, 0x44, bh); printf("\n");
  x86gen_i386_mov_rm8atreg32plusdisp32_reg8(NULL, edi, 0x12345678, bh); printf("\n");
  x86gen_i386_mov_rm8atdisp32_reg8(NULL, 0x12345678, ch); printf("\n");
  x86gen_i386_mov_rm8atbasereg32indexreg32scale_reg8(NULL, esp, eax, X86Gen_Scale_4, bl); printf("\n");
  x86gen_i386_mov_rm8atbasereg32indexreg32scaledisp8_reg8(NULL, esp, eax, X86Gen_Scale_4, 0x11, bl); printf("\n");
  x86gen_i386_mov_rm8atbasereg32indexreg32scaledisp32_reg8(NULL, esp, eax, X86Gen_Scale_4, 0x11111111, bl); printf("\n");
  x86gen_amd64_mov_reg64_rm64atreg64plusdisp32(NULL, rax, rcx, 0x12345678); printf("\n");
}
