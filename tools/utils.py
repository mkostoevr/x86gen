from constants import ARCH_I386, ARCH_AMD64

# Utils ########################################################################

def get_native_size(arch):
    if arch == ARCH_I386:
        return 32
    elif arch == ARCH_AMD64:
        return 64
    else:
        raise Exception('Error: Unknown architecture: %s' % (arch,))

def is_str(obj):
    return isinstance(obj, str)

def is_hex_byte(x):
    assert(is_str(x))
    hexdigits = '0123456789ABCDEF'
    return len(x) == 2 and all(c in hexdigits for c in x)

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
        raise Exception('Unknown size: %d' % (size,))

def gen_id():
    if not hasattr(gen_id, 'next'):
        gen_id.next = 0
    gen_id.next += 1
    return gen_id.next

def pass_split(iterable, the_pass):
    result = tuple()
    for it in iterable:
        result += the_pass(it)
    return result

def pass_transform(iterable, func):
    return tuple(map(func, iterable))

def pass_foreach(instructions, func):
    for instr in instructions:
        func(instr)
