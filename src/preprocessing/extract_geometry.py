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

        elif item["type"] == "CIRCLE":
            cx, cy, _ = item["center"]
            r = item["radius"]
            vertices.append([cx, cy, r])

    vertices = np.array(vertices)

    # Center and normalize
    center = vertices.mean(axis=0)
    vertices = vertices - center
    scale = vertices.max()
    vertices = vertices / scale

    return vertices
