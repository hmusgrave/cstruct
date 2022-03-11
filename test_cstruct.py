from cstruct import cstruct
from dataclasses import dataclass

@cstruct('ll')  # struct.Struct format strings
@dataclass  # cstruct currently only wraps dataclasses
class timeval:
    tv_sec: int
    tv_usec: int

@cstruct(timeval, 'HH', 'i')  # nested cstruct types in addition to format strings
@dataclass
class input_event:
    # nested struct, defined above
    time: timeval
    
    # other primitive fields
    event_type: int
    code: int
    value: int

def test_something():
    # the decorated classes are still ordinary dataclasses
    ie = input_event(
        timeval(1, 2),
        3, 4, 5
    )

    # serialize the data
    serialized = ie.pack()

    # cstruct classes expose their serialied byte length
    assert len(serialized) == input_event.size

    # we can deserialize that data to recover the original object
    assert input_event.unpack(serialized) == ie

    # trailing bytes are ignored
    assert input_event.unpack(serialized*2) == ie

@cstruct('<H>i@3xi')
@dataclass
class mixed_alignment:
    a: int
    b: int
    c: int

def test_mixed_alignment():
    val = mixed_alignment.zero()
    assert val.pack() == b'\0'*mixed_alignment.size
    assert mixed_alignment.unpack(val.pack()) == val

@cstruct('h')
@dataclass
class small:
    a: int

@cstruct(small, 'l')
@dataclass
class big:
    a: small
    b: int

def test_nested_packing():
    assert small.size == 2
    assert small.alignment == 2
    assert big.size == 16
    assert big.alignment == 2
