# # src/renderer/mesh_reconstruction.py

# import trimesh
# import numpy as np
# from shapely.geometry import Polygon, LineString
# from shapely.ops import unary_union


# WALL_HEIGHT = 5.0
# WALL_THICKNESS = 0.3
# FLOOR_HEIGHT = 0.2


# def build_mesh(geometry, output_path):
#     meshes = []

#     walls = geometry.get("walls", [])
#     floors = geometry.get("floors", [])

#     print("Building mesh...")
#     print("Walls:", len(walls))
#     print("Floors:", len(floors))

#     # -------- WALLS --------
#     for wall in walls:
#         try:
#             if len(wall) < 2:
#                 continue

#             line = LineString(wall)
#             poly = line.buffer(WALL_THICKNESS)

#             if not poly.is_valid or poly.area == 0:
#                 continue

#             wall_mesh = trimesh.creation.extrude_polygon(poly, height=WALL_HEIGHT)
#             meshes.append(wall_mesh)

#         except Exception as e:
#             print("Wall error:", e)

#     # -------- FLOORS --------
#     for floor in floors:
#         try:
#             if len(floor) < 3:
#                 continue

#             poly = Polygon(floor)

#             if not poly.is_valid or poly.area == 0:
#                 continue

#             floor_mesh = trimesh.creation.extrude_polygon(poly, height=FLOOR_HEIGHT)
#             meshes.append(floor_mesh)

#         except Exception as e:
#             print("Floor error:", e)

#     if not meshes:
#         raise ValueError("No mesh generated")

#     # -------- MERGE --------
#     final_mesh = trimesh.util.concatenate(meshes)

#     # Center model
#     final_mesh.apply_translation(-final_mesh.centroid)

#     # Scale to reasonable size
#     scale = final_mesh.scale
#     if scale > 0:
#         final_mesh.apply_scale(1.0 / scale)

#     final_mesh.export(output_path)
#     print("Mesh saved to:", output_path)

#     return output_path
# src/renderer/mesh_reconstruction.py

import trimesh
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union


# ======================
# PARAMETERS
# ======================

WALL_HEIGHT = 4.0
WALL_THICKNESS = 0.25
FLOOR_HEIGHT = 0.2

DOOR_HEIGHT = 2.2
WINDOW_HEIGHT = 1.2
WINDOW_BASE = 1.0


# ======================
# MAIN FUNCTION
# ======================

def build_mesh(geometry, output_path):
    meshes = []

    # ------------------
    # BUILD WALL POLYGONS
    # ------------------
    wall_polys = []

    for wall in geometry["walls"]:
        if len(wall) < 2:
            continue

        try:
            line = LineString(wall)
            poly = line.buffer(WALL_THICKNESS)

            if poly.is_valid and poly.area > 0.1:
                wall_polys.append(poly)

        except Exception as e:
            print("Wall geometry error:", e)

    if not wall_polys:
        raise ValueError("No valid wall geometry")

    wall_union = unary_union(wall_polys)

    # ------------------
    # BUILD DOOR CUTOUTS
    # ------------------
    door_polys = []

    for door in geometry.get("doors", []):
        if len(door) < 2:
            continue

        try:
            line = LineString(door)
            poly = line.buffer(WALL_THICKNESS * 1.2)

            if poly.is_valid and poly.area > 0.05:
                door_polys.append(poly)

        except Exception as e:
            print("Door geometry error:", e)

    if door_polys:
        wall_union = wall_union.difference(unary_union(door_polys))

    # ------------------
    # EXTRUDE WALLS
    # ------------------
    wall_meshes = []

    if isinstance(wall_union, MultiPolygon):
        geoms = wall_union.geoms
    else:
        geoms = [wall_union]

    for poly in geoms:
        try:
            mesh = trimesh.creation.extrude_polygon(poly, height=WALL_HEIGHT)
            wall_meshes.append(mesh)
        except Exception as e:
            print("Wall extrusion error:", e)

    meshes.extend(wall_meshes)

    # ------------------
    # FLOORS
    # ------------------
    for floor in geometry["floors"]:
        try:
            if len(floor) < 3:
                continue

            poly = Polygon(floor)

            if not poly.is_valid or poly.area < 5:
                continue

            floor_mesh = trimesh.creation.extrude_polygon(poly, height=FLOOR_HEIGHT)
            meshes.append(floor_mesh)

        except Exception as e:
            print("Floor error:", e)

    # ------------------
    # WINDOWS (visual only)
    # ------------------
    for win in geometry.get("windows", []):
        if len(win) < 2:
            continue

        try:
            line = LineString(win)
            poly = line.buffer(WALL_THICKNESS * 0.8)

            if not poly.is_valid:
                continue

            win_mesh = trimesh.creation.extrude_polygon(poly, height=WINDOW_HEIGHT)
            win_mesh.apply_translation((0, 0, WINDOW_BASE))
            meshes.append(win_mesh)

        except Exception as e:
            print("Window error:", e)

    # ------------------
    # FINAL MESH
    # ------------------
    if not meshes:
        raise ValueError("No mesh generated")

    final_mesh = trimesh.util.concatenate(meshes)

    # Center model
    final_mesh.apply_translation(-final_mesh.centroid)

    # Export GLB
    glb_path = output_path.with_suffix(".glb")
    final_mesh.export(glb_path)

    print("✅ GLB exported:", glb_path)
