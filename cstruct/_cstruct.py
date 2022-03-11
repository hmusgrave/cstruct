import re
from struct import Struct, calcsize
from dataclasses import dataclass

# The total width is based on the width of the whole thing put together
# The amount of padding is based on width of the next item
# We should support byte swapping

alignment_sep = re.compile(r'([@=<>!])')

def alignment(fmt):
    if alignment_sep.search(fmt):
        # alignment indicator needs to be preserved because
        # of "native sizes" as an option
        f = lambda n: fmt[0] + ('x'*n) + fmt[1:]
    else:
        f = lambda n: ('x'*n) + fmt

    # when increasing size by 1 byte, how much does the size
    # actually increase?
    last = calcsize(f(0))
    for i in range(1<<20):
        if (cur := calcsize(f(i))) != last:
            return cur - last
        last = cur
    unreachable

def alignment_split(s):
    L = alignment_sep.split(s)
    tail = [''.join(L[i:i+2]) for i in range(1, len(L), 2)]
    if not L[0]:  # first character is an alignment character
        return tail
    return [L[0]] + tail

def align_forward(n, align):
    count = (n-1) // align
    return (count+1)*align

@dataclass
class struct_spec:
    s: Struct
    len: int
    byte_len: int
    padded_byte_len: int
    alignment: int

    @classmethod
    def from_fmt(cls, fmt):
        s = Struct(fmt)
        bl = s.size
        l = len(s.unpack(b'\0'*bl))
        return cls(s, l, bl, bl, alignment(fmt))

    def align_to(self, align):
        self.padded_byte_len = align_forward(self.byte_len, align)

    def pack(self, instance, fields, i):
        raw = [getattr(instance, x) for x in fields[i:i+self.len]]
        return self.s.pack(*raw) + b'\0' * (self.padded_byte_len - self.byte_len)

    def unpack(self, buf, i):
        return self.s.unpack(buf[i:i+self.byte_len])

@dataclass
class nested_spec:
    s: type
    len: int
    byte_len: int
    padded_byte_len: int
    alignment: int

    @classmethod
    def from_class(cls, c):
        return cls(c, 1, c.size, c.size, c.alignment)

    def align_to(self, align):
        self.padded_byte_len = align_forward(self.byte_len, align)

    def pack(self, instance, fields, i):
        z = getattr(instance, fields[i]).pack()
        return z + b'\0' * (self.padded_byte_len - self.byte_len)

    def unpack(self, buf, i):
        return [self.s.unpack(buf[i:])]

def skip(g):
    g = iter(g)
    next(g)
    yield from g

def end(g):
    val = None
    for x in g:
        val = x
    return val

def cstruct(*_components):
    l, bl, specs = 0, 0, {}
    components = lambda: (x for c in _components for x in (alignment_split(c) if isinstance(c, str) else [c]))
    first = next(components())
    align = alignment(first) if isinstance(first, str) else first.alignment
    gen_spec = lambda c: struct_spec.from_fmt(c) if isinstance(c, str) else nested_spec.from_class(c)
    for (a, b) in zip(components(), skip(components())):
        x, b_spec = map(gen_spec, (a, b))
        x.align_to(b_spec.alignment)
        specs[(l, bl)] = x
        l += x.len
        bl += x.padded_byte_len
    x = specs[(l, bl)] = gen_spec(end(components()))
    l += x.len
    bl += x.padded_byte_len

    def dec(cls):
        fields = list(cls.__dataclass_fields__)

        @classmethod
        def unpack(cls, b):
            return cls(*(x
                for (l, bl), v in specs.items()
                for x in v.unpack(b, bl)
            ))

        def pack(self):
            return b''.join(
                v.pack(self, fields, l)
                for (l, bl), v in specs.items()
            )

        @classmethod
        def zero(cls):
            return cls.unpack(b'\0' * cls.size)

        cls.size = bl
        cls.alignment = align
        cls.unpack = unpack
        cls.pack = pack
        cls.zero = zero

        return cls

    return dec

__all__ = ['cstruct']
