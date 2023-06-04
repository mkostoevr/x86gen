#include <assert.h>
#include <stdio.h>
#include <stdint.h>

#define X86Gen_Output FILE *
#define X86Gen_Output_Write(out_i386, size, data) fwrite(data, 1, size, out_i386)
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

#define cs X86Gen_SegReg_CS
#define ds X86Gen_SegReg_DS
#define es X86Gen_SegReg_ES
#define fs X86Gen_SegReg_FS
#define gs X86Gen_SegReg_GS
#define ss X86Gen_SegReg_SS

int main() {
  FILE *const out_i386 = fopen("test32.bin", "wb");
  FILE *const out_amd64 = fopen("test64.bin", "wb");
#include "tests.h"
  fclose(out_i386);
  fclose(out_amd64);
}
