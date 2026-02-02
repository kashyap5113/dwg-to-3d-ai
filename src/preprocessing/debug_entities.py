import ezdxf
from collections import Counter

doc = ezdxf.readfile("data/input_dwg/sample20.dxf")
msp = doc.modelspace()

types = Counter()

for e in msp:
    types[e.dxftype()] += 1

print(types)
