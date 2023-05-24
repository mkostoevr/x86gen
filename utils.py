from constants import *

def get_native_size(arch):
    if arch == ARCH_I386:
        return 32
    elif arch == ARCH_AMD64:
        return 64
    else:
        raise 'Error: Unknown architecture: %s' % (arch,)

def is_tuple(obj):
    return isinstance(obj, tuple)

def is_int(obj):
    return isinstance(obj, int)

def is_str(obj):
    return isinstance(obj, str)

def is_hex_byte(x):
    assert(is_str(x))
    from string import hexdigits
    return len(x) == 2 and all(c in hexdigits for c in x)
