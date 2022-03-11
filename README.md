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
```

## Notes

- The `pack`, `unpack`, and `size` fields of the decorated class are reserved for
use by `cstruct`.
- Low alignment nested structs followed by higher alignment fields aren't yet
  supported.

