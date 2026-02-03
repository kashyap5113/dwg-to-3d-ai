# # import json
# # import numpy as np


# # def geometry_to_3d(json_file):
# #     with open(json_file) as f:
# #         data = json.load(f)

# #     vertices = []

# #     for item in data:

# #         if item["type"] == "LINE":
# #             x1, y1, _ = item["start"]
# #             x2, y2, _ = item["end"]
# #             vertices.append([x1, y1, 0])
# #             vertices.append([x2, y2, 1])

# #         elif item["type"] in ["POLYLINE", "SPLINE"]:
# #             for p in item["points"]:
# #                 vertices.append([p[0], p[1], 0])

# #         elif item["type"] == "CIRCLE":
# #             cx, cy, _ = item["center"]
# #             r = item["radius"]
# #             vertices.append([cx + r, cy, 0])
# #             vertices.append([cx - r, cy, 0])
# #             vertices.append([cx, cy + r, 0])
# #             vertices.append([cx, cy - r, 0])

# #         elif item["type"] == "ARC":
# #             cx, cy, _ = item["center"]
# #             r = item["radius"]
# #             vertices.append([cx + r, cy, 0])
# #             vertices.append([cx - r, cy, 0])

# #         elif item["type"] == "ELLIPSE":
# #             cx, cy, _ = item["center"]
# #             vertices.append([cx, cy, 0])

# #     if len(vertices) == 0:
# #         return None
# #     def extract_walls_and_floors(entities):
# #         walls = []
# #         floors = []

# #         for poly in entities["polylines"]:
# #             if poly["closed"]:
# #                 floors.append(poly["points"])
# #             else:
# #                 walls.append(poly["points"])

# #         return {
# #             "walls": walls,
# #             "floors": floors
# #         }

# #     vertices = np.array(vertices, dtype=float)

# #     # Center and normalize
# #     center = vertices.mean(axis=0)
# #     vertices = vertices - center

# #     scale = np.max(np.abs(vertices))
# #     if scale > 0:
# #         vertices = vertices / scale

# #     return vertices
# # src/preprocessing/extract_geometry.py

# # src/preprocessing/extract_geometry.py

# def extract_walls_and_floors(entities):
#     walls = []
#     floors = []

#     for item in entities:
#         layer = item.get("layer", "").lower()

#         if "wall" in layer:
#             if item["type"] == "LINE":
#                 x1, y1, _ = item["start"]
#                 x2, y2, _ = item["end"]
#                 walls.append([(x1, y1), (x2, y2)])

#             elif item["type"] == "POLYLINE":
#                 points = [(p[0], p[1]) for p in item["points"]]
#                 walls.append(points)

#         elif "floor" in layer and item["type"] == "POLYLINE" and item.get("closed"):
#             points = [(p[0], p[1]) for p in item["points"]]
#             floors.append(points)

#     return {"walls": walls, "floors": floors}
# src/preprocessing/extract_geometry.py

# src/preprocessing/extract_geometry.py

# src/preprocessing/extract_geometry.py

# src/preprocessing/extract_geometry.py

from shapely.geometry import Polygon, LineString, MultiPolygon

# Layer rules (lowercase)
WALL_LAYERS = ["a-wall"]
FLOOR_LAYERS = ["a-flor"]
DOOR_LAYERS = ["a-door"]
WINDOW_LAYERS = ["a-glaz", "a-glaz-sill"]


def extract_walls_floors_doors_windows(entities):
    walls = []
    floors = []
    doors = []
    windows = []

    for item in entities:
        layer = item.get("layer", "").lower()
        etype = item["type"]

        # ---------- GET POINTS ----------
        pts = []

        if etype == "LINE":
            x1, y1, _ = item["start"]
            x2, y2, _ = item["end"]
            pts = [(x1, y1), (x2, y2)]

        elif etype in ["POLYLINE", "LWPOLYLINE", "SPLINE"]:
            pts = [(p[0], p[1]) for p in item.get("points", [])]

        if len(pts) < 2:
            continue

        # ---------- WALLS ----------
        if layer in WALL_LAYERS:
            walls.append(pts)

        # ---------- FLOORS (ONLY CLOSED POLYGONS) ----------
        elif layer in FLOOR_LAYERS and etype in ["POLYLINE", "LWPOLYLINE"]:

            if not item.get("closed", False):
                continue

            if len(pts) < 3:
                continue

            try:
                poly = Polygon(pts)

                if not poly.is_valid or poly.area < 5:
                    continue

                # Handle MultiPolygon safely
                if isinstance(poly, MultiPolygon):
                    for p in poly.geoms:
                        floors.append(list(p.exterior.coords))
                else:
                    floors.append(list(poly.exterior.coords))

            except Exception as e:
                print("Floor polygon error:", e)

        # ---------- DOORS ----------
        elif layer in DOOR_LAYERS:
            doors.append(pts)

        # ---------- WINDOWS ----------
        elif layer in WINDOW_LAYERS:
            windows.append(pts)

    print("Filtered walls:", len(walls))
    print("Filtered floors:", len(floors))
    print("Filtered doors:", len(doors))
    print("Filtered windows:", len(windows))

    return {
        "walls": walls,
        "floors": floors,
        "doors": doors,
        "windows": windows
    }
