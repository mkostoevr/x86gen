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

def is_byte_value(x):
    return x >= 0 and x <= 255

def is_reg_size(x):
    return x in (8, 16, 32, 64)

def is_disp_size(x):
    return x in (8, 32)

def is_native_size(x):
    return x in (32, 64)

def is_arch(x):
    return x in arch_variants

def the_only_if_any_in(collection):
    result = None
    result_count = 0
    for it in collection:
        if it != None:
            result = it
            result_count += 1
    assert(result_count == 1 or result_count == 0)
    return result

def both_or_none(a, b):
    return (a != None and b != None) or (a == None and b == None)

def without_nones(collection):
    result = []
    for it in collection:
        if it != None:
            result.append(it)
    return tuple(result)

def size_to_word(size):
    if size == 8:
        return 'byte'
    elif size == 16:
        return 'word'
    elif size == 32:
        return 'dword'
    elif size == 64:
        return 'qword'
    else:
        raise 'Unknown size: %d' % (size,)
