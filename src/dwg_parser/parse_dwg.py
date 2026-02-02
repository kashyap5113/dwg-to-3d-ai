import ezdxf
import json
from pathlib import Path


def parse_dwg(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    entities = []

    for e in msp:
        etype = e.dxftype()

        if etype == "LINE":
            entities.append({
                "type": "LINE",
                "start": list(e.dxf.start),
                "end": list(e.dxf.end)
            })

        elif etype == "CIRCLE":
            entities.append({
                "type": "CIRCLE",
                "center": list(e.dxf.center),
                "radius": e.dxf.radius
            })

        elif etype == "LWPOLYLINE":
            points = [list(p) for p in e.get_points()]
            entities.append({
                "type": "POLYLINE",
                "points": points,
                "closed": e.closed
            })

    return entities


def save_json(data, output_file):
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
