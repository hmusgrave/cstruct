from struct import Struct
from dataclasses import dataclass

@dataclass
class _spec:
    s: Struct
    len: int
    byte_len: int

    @classmethod
    def from_fmt(cls, fmt):
        s = Struct(fmt)
        bl = s.size
        l = len(s.unpack(b'\0'*bl))
        return cls(s, l, bl)

def cstruct(*components):
    l, bl = 0, 0
    specs = {}
    for c in components:
        if isinstance(c, str):
            x = specs[(l, bl)] = _spec.from_fmt(c)
            l += x.len
            bl += x.byte_len
        else:
            specs[(l, bl)] = c
            l += 1
            bl += c.size

    def dec(cls):
        fields = list(cls.__dataclass_fields__)

        @classmethod
        def unpack(cls, b):
            return cls(*(x
                for (l, bl), v in specs.items()
                for x in (
                    v.s.unpack(b[bl:bl+v.byte_len]) if isinstance(v, _spec)
                    else [v.unpack(b[bl:bl+v.size])]
                )
            ))

        def pack(self):
            return b''.join(
                (
                    v.s.pack(*(getattr(self, s) for s in fields[l:l+v.len]))
                    if isinstance(v, _spec)
                    else getattr(self, fields[l]).pack()
                )
                for (l, bl), v in specs.items()
            )

        cls.size = bl
        cls.unpack = unpack
        cls.pack = pack

        return cls

    return dec

__all__ = ['cstruct']
