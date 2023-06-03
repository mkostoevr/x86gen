CGEN_OUTPUT_COMPONENT_SEPARATOR = ',\n    '
CGEN_PARAMETER_SEPARATOR = ',\n  '

PREFIX = 'X86GEN'

ARCH_I386 = 'i386'
ARCH_AMD64 = 'amd64'

arch_variants = (ARCH_I386, ARCH_AMD64)

imms = {
    'imm8': 8,
    'imm16': 16,
    'imm32': 32,
    'imm64': 64,
}

regs = {
    'reg8': 8,
    'reg16': 16,
    'reg32': 32,
    'reg64': 64,
}

regmems = {
    'reg/mem8': (8, 8),
    'reg/mem16': (16, 16),
    'reg/mem32': (32, 32),
    'reg/mem64': (64, 64),
    'reg16/mem16': (16, 16),
    'reg32/mem16': (32, 16),
    'reg64/mem16': (64, 16),
}

moffsets = {
    'moffset8': 8,
    'moffset16': 16,
    'moffset32': 32,
    'moffset64': 64,
}

modrms = {
    '/r': None,
    '/0': 0,
    '/1': 1,
    '/2': 2,
    '/3': 3,
    '/4': 4,
    '/5': 5,
    '/6': 6,
    '/7': 7,
}

is_ = {
    'ib': 8,
    'iw': 16,
    'id': 32,
    'iq': 64,
}

plusrs = {
    '+rb': 8,
    '+rw': 16,
    '+rd': 32,
    '+rq': 64,
}

specifiedregs = {
    'AL': 8,
    'AX': 16,
    'EAX': 32,
    'RAX': 64,
}

segregs = {
    'DS': 16,
    'ES': 16,
    'FS': 16,
    'GS': 16,
    'SS': 16,
}

B00 = 0
B01 = 1
B10 = 2
B11 = 3

B000 = 0
B001 = 1
B010 = 2
B011 = 3
B100 = 4
B101 = 5
B110 = 6
B111 = 7
