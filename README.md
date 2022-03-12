# cstruct

Easily add nesting to Python's struct interface

## Installation

```
pip install -e git+https://github.com/hmusgrave/cstruct.git#egg=cstruct
```

## Examples

```python
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

# we can initialize an empty struct
ie = input_event.zero()

# or treat these as ordinary dataclasses
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

@cstruct('<H>H')  # mixed alignment is supported
@dataclass(order=True)  # you have full control over what the dataclass looks like
class foo:
    a: int
    b: int

@cstruct(foo, 'l')
@dataclass
class bar:
    a: foo
    b: int

def test_padding():
    assert foo.size == 4

    #   4 bytes of bar.a
    # + 4 bytes of padding to meet bar.b alignment
    # + 8 bytes of bar.b
    assert bar.size == 16
```

## Notes

- The `pack`, `unpack`, `size`, `alignment`, and `zero` fields of the decorated class are reserved for use by `cstruct`.
