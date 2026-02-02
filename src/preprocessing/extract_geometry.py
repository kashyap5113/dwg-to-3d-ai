import json
import numpy as np


def geometry_to_3d(json_file):
    with open(json_file) as f:
        data = json.load(f)

    vertices = []

    for item in data:

        if item["type"] == "LINE":
            x1, y1, _ = item["start"]
            x2, y2, _ = item["end"]
            vertices.append([x1, y1, 0])
            vertices.append([x2, y2, 1])

        elif item["type"] in ["POLYLINE", "SPLINE"]:
            for p in item["points"]:
                vertices.append([p[0], p[1], 0])

        elif item["type"] == "CIRCLE":
            cx, cy, _ = item["center"]
            r = item["radius"]
            vertices.append([cx + r, cy, 0])
            vertices.append([cx - r, cy, 0])
            vertices.append([cx, cy + r, 0])
            vertices.append([cx, cy - r, 0])

        elif item["type"] == "ARC":
            cx, cy, _ = item["center"]
            r = item["radius"]
            vertices.append([cx + r, cy, 0])
            vertices.append([cx - r, cy, 0])

        elif item["type"] == "ELLIPSE":
            cx, cy, _ = item["center"]
            vertices.append([cx, cy, 0])

    if len(vertices) == 0:
        return None

    vertices = np.array(vertices, dtype=float)

    # Center and normalize
    center = vertices.mean(axis=0)
    vertices = vertices - center

    scale = np.max(np.abs(vertices))
    if scale > 0:
        vertices = vertices / scale

    return vertices
