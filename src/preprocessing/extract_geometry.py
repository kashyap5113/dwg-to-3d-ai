
# from shapely.geometry import Polygon, MultiPolygon, LineString


# # ======================
# # FLEXIBLE LAYER DEFINITIONS
# # ======================

# WALL_LAYERS = ["wall", "a-wall", "partition", "a-part"]
# FLOOR_LAYERS = ["floor", "slab", "a-flor"]
# DOOR_LAYERS = ["door", "a-door", "opening"]
# WINDOW_LAYERS = ["window", "a-win", "glaz"]


# # ======================
# # MAIN FUNCTION
# # ======================

# def extract_walls_floors_doors_windows(entities):
#     walls = []
#     floors = []
#     doors = []
#     windows = []

#     for item in entities:
#         layer = item.get("layer", "").lower()
#         etype = item.get("type")

#         pts = []

#         if etype == "LINE":
#             x1, y1, _ = item["start"]
#             x2, y2, _ = item["end"]
#             pts = [(x1, y1), (x2, y2)]

#         elif etype in ["POLYLINE", "LWPOLYLINE", "SPLINE"]:
#             pts = [(p[0], p[1]) for p in item.get("points", [])]

#         if len(pts) < 2:
#             continue

#         # ------------------
#         # WALLS (store layer info!)
#         # ------------------
#         if any(k in layer for k in WALL_LAYERS):
#             walls.append({
#                 "points": pts,
#                 "layer": layer
#             })

#         # ------------------
#         # FLOORS
#         # ------------------
#         elif any(k in layer for k in FLOOR_LAYERS) and etype in ["POLYLINE", "LWPOLYLINE"]:
#             if not item.get("closed", False):
#                 continue
#             try:
#                 poly = Polygon(pts)
#                 if poly.is_valid and poly.area > 10:
#                     floors.append(list(poly.exterior.coords))
#             except:
#                 continue

#         # ------------------
#         # DOORS
#         # ------------------
#         elif any(k in layer for k in DOOR_LAYERS):
#             doors.append(pts)

#         # ------------------
#         # WINDOWS
#         # ------------------
#         elif any(k in layer for k in WINDOW_LAYERS):
#             windows.append(pts)

#     print("Filtered walls:", len(walls))
#     print("Filtered floors:", len(floors))
#     print("Filtered doors:", len(doors))
#     print("Filtered windows:", len(windows))

#     return {
#         "walls": walls,
#         "floors": floors,
#         "doors": doors,
#         "windows": windows
#     }

from shapely.geometry import Polygon, MultiPolygon


def categorize_layer(layer_name: str):
    layer = layer_name.lower()

    if any(k in layer for k in ["wall", "a-wall", "partition", "a-part"]):
        return "walls"
    elif any(k in layer for k in ["floor", "slab", "a-flor"]):
        return "floors"
    elif any(k in layer for k in ["door", "a-door", "opening"]):
        return "doors"
    elif any(k in layer for k in ["window", "a-win", "glaz"]):
        return "windows"
    else:
        return "ignore"


def extract_walls_floors_doors_windows(entities):
    walls = []
    floors_raw = []
    doors = []
    windows = []
    ignored = 0

    for item in entities:
        layer = item.get("layer", "")
        etype = item["type"]
        category = categorize_layer(layer)

        pts = []

        if etype == "LINE":
            x1, y1, _ = item["start"]
            x2, y2, _ = item["end"]
            pts = [(x1, y1), (x2, y2)]

        elif etype in ["POLYLINE", "LWPOLYLINE", "SPLINE"]:
            pts = [(p[0], p[1]) for p in item.get("points", [])]

        if len(pts) < 2:
            continue

        # ---------------- WALLS ----------------
        if category == "walls":
            walls.append({
                "points": pts,
                "layer": layer
            })

        # ---------------- FLOORS ----------------
        elif category == "floors" and etype in ["POLYLINE", "LWPOLYLINE"] and item.get("closed", False):
            try:
                poly = Polygon(pts)
                if poly.is_valid and poly.area > 10:
                    floors_raw.append(poly)
            except:
                continue

        # ---------------- DOORS ----------------
        elif category == "doors":
            doors.append(pts)

        # ---------------- WINDOWS ----------------
        elif category == "windows":
            windows.append(pts)

        else:
            ignored += 1

    # ---------------- FLOOR PLAN DETECTION ----------------
    floor_boundary = []
    rooms = []

    if floors_raw:
        largest_floor = max(floors_raw, key=lambda p: p.area)
        floor_boundary = list(largest_floor.exterior.coords)

        for poly in floors_raw:
            if poly.area < largest_floor.area:
                rooms.append(list(poly.exterior.coords))

    print("Filtered walls:", len(walls))
    print("Filtered doors:", len(doors))
    print("Filtered windows:", len(windows))
    print("Floor boundary detected:", bool(floor_boundary))
    print("Rooms detected:", len(rooms))
    print("Ignored entities:", ignored)

    return {
        "walls": walls,
        "floors": [floor_boundary] if floor_boundary else [],
        "rooms": rooms,
        "doors": doors,
        "windows": windows
    }
