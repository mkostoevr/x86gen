# Constants ####################################################################

ARCH_I386 = 'i386'
ARCH_AMD64 = 'amd64'

ARCHS_I386 = (ARCH_I386,)
ARCHS_AMD64 = (ARCH_AMD64,)
ARCHS_ALL = (ARCH_I386, ARCH_AMD64,)

imms = {
    'imm8u': 8,
    'imm16u': 16,
    'imm32u': 32,
    'imm64u': 64,
    'imm8s': 8,
    'imm16s': 16,
    'imm32s': 32,
    'imm64s': 64,
}

reloffs = {
    'rel8off': 8,
    'rel16off': 16,
    'rel32off': 32,
}

imms_without_signs = ('imm8', 'imm16', 'imm32', 'imm64')

regs = {
    'reg8': 8,
    'reg16': 16,
    'reg32': 32,
    'reg64': 64,
}

moffsets = {
    'moffset8': 8,
    'moffset16': 16,
    'moffset32': 32,
    'moffset64': 64,
}

regmems = {
    'reg/mem8': (8, 8),
    'reg/mem16': (16, 16),
    'reg/mem32': (32, 32),
    'reg/mem64': (64, 64),
    'reg32/mem16': (32, 16),
    'reg64/mem16': (64, 16),
}

slashes = {
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

cs = {
    'cb': 8,
    'cw': 16,
    'cd': 32,
    'cp': 48,
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

specifiedsegregs = {
    'DS': 16,
    'ES': 16,
    'FS': 16,
    'GS': 16,
    'SS': 16,
}


