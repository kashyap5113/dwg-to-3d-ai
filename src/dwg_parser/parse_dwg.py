# # src/dwg_parser/parse_dwg.py

# import ezdxf
# import json
# from pathlib import Path


# def parse_dwg(file_path):
#     doc = ezdxf.readfile(file_path)
#     msp = doc.modelspace()

#     entities = []

#     for e in msp:
#         etype = e.dxftype()
#         layer = e.dxf.layer.lower() if hasattr(e.dxf, "layer") else "default"

#         # -------- LINE --------
#         if etype == "LINE":
#             entities.append({
#                 "type": "LINE",
#                 "start": list(e.dxf.start),
#                 "end": list(e.dxf.end),
#                 "layer": layer
#             })

#         # -------- POLYLINE / LWPOLYLINE --------
#         elif etype in ["LWPOLYLINE", "POLYLINE"]:
#             points = []
#             for p in e.get_points():
#                 points.append([p[0], p[1], 0])

#             entities.append({
#                 "type": "POLYLINE",
#                 "points": points,
#                 "closed": bool(e.closed),
#                 "layer": layer
#             })

#         # -------- CIRCLE --------
#         elif etype == "CIRCLE":
#             entities.append({
#                 "type": "CIRCLE",
#                 "center": list(e.dxf.center),
#                 "radius": e.dxf.radius,
#                 "layer": layer
#             })

#         # -------- ARC --------
#         elif etype == "ARC":
#             entities.append({
#                 "type": "ARC",
#                 "center": list(e.dxf.center),
#                 "radius": e.dxf.radius,
#                 "start_angle": e.dxf.start_angle,
#                 "end_angle": e.dxf.end_angle,
#                 "layer": layer
#             })

#         # -------- ELLIPSE --------
#         elif etype == "ELLIPSE":
#             entities.append({
#                 "type": "ELLIPSE",
#                 "center": list(e.dxf.center),
#                 "major_axis": list(e.dxf.major_axis),
#                 "ratio": e.dxf.ratio,
#                 "layer": layer
#             })

#         # -------- SPLINE --------
#         elif etype == "SPLINE":
#             points = []
#             for p in e.control_points:
#                 points.append([p[0], p[1], 0])

#             entities.append({
#                 "type": "SPLINE",
#                 "points": points,
#                 "layer": layer
#             })

#         else:
#             continue

#     print("Parsed entities:", len(entities))
#     return entities


# def save_json(data, path):
#     Path(path).parent.mkdir(parents=True, exist_ok=True)
#     with open(path, "w") as f:
#         json.dump(data, f, indent=2)
# src/dwg_parser/parse_dwg.py

import ezdxf
import json
from pathlib import Path


IGNORE_ENTITY_TYPES = ["TEXT", "MTEXT", "DIMENSION", "HATCH", "INSERT"]


def parse_dwg(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    entities = []
    layers_found = set()
    ignored_count = 0

    for e in msp:
        etype = e.dxftype()

        # Ignore noise entities
        if etype in IGNORE_ENTITY_TYPES:
            ignored_count += 1
            continue

        layer = e.dxf.layer.lower() if hasattr(e.dxf, "layer") else "default"
        layers_found.add(layer)

        # -------- LINE --------
        if etype == "LINE":
            entities.append({
                "type": "LINE",
                "start": [float(e.dxf.start.x), float(e.dxf.start.y), 0],
                "end": [float(e.dxf.end.x), float(e.dxf.end.y), 0],
                "layer": layer
            })

        # -------- POLYLINE / LWPOLYLINE --------
        elif etype in ["LWPOLYLINE", "POLYLINE"]:
            points = []
            for p in e.get_points():
                points.append([float(p[0]), float(p[1]), 0])

            entities.append({
                "type": "POLYLINE",
                "points": points,
                "closed": bool(e.closed),
                "layer": layer
            })

        # -------- SPLINE --------
        elif etype == "SPLINE":
            points = []
            for p in e.control_points:
                points.append([float(p[0]), float(p[1]), 0])

            entities.append({
                "type": "SPLINE",
                "points": points,
                "layer": layer
            })

        else:
            ignored_count += 1
            continue

    print("Parsed entities:", len(entities))
    print("Ignored entities:", ignored_count)
    print("DXF Layers found:", layers_found)

    return entities


def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
