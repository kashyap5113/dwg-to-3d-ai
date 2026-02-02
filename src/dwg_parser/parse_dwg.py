import ezdxf
import json
from pathlib import Path


def parse_dwg(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    entities = []

    for e in msp:
        etype = e.dxftype()

        # LINE
        if etype == "LINE":
            entities.append({
                "type": "LINE",
                "start": list(e.dxf.start),
                "end": list(e.dxf.end)
            })

        # POLYLINE / LWPOLYLINE
        elif etype in ["LWPOLYLINE", "POLYLINE"]:
            points = []
            for p in e.get_points():
                points.append([p[0], p[1], 0])
            entities.append({
                "type": "POLYLINE",
                "points": points
            })

        # CIRCLE
        elif etype == "CIRCLE":
            entities.append({
                "type": "CIRCLE",
                "center": list(e.dxf.center),
                "radius": e.dxf.radius
            })

        # ARC
        elif etype == "ARC":
            entities.append({
                "type": "ARC",
                "center": list(e.dxf.center),
                "radius": e.dxf.radius,
                "start_angle": e.dxf.start_angle,
                "end_angle": e.dxf.end_angle
            })

        # ELLIPSE
        elif etype == "ELLIPSE":
            entities.append({
                "type": "ELLIPSE",
                "center": list(e.dxf.center),
                "major_axis": list(e.dxf.major_axis),
                "ratio": e.dxf.ratio
            })

        # SPLINE (approximate with control points)
        elif etype == "SPLINE":
            points = []
            for p in e.control_points:
                points.append([p[0], p[1], 0])
            entities.append({
                "type": "SPLINE",
                "points": points
            })

        # Ignore TEXT, MTEXT, DIMENSION, INSERT, HATCH, IMAGE, etc.
        else:
            continue

    return entities


def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
