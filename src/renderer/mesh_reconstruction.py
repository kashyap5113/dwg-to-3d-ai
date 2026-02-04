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
from trimesh.visual.material import PBRMaterial
from PIL import Image
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, polygonize
from ml.material_predictor import predict_material
from ml.feature_extractor import extract_wall_features




# ======================
# PARAMETERS
# ======================

FLOOR_STEP = 3.2
WINDOW_HEIGHT = 1.2
WINDOW_BASE = 1.0
ROOM_HEIGHT = 0.05

WALL_THICKNESS = 0.25
DEFAULT_WALL_HEIGHT = 3.0


# ======================
# TEXTURE MAP (PBR)
# ======================

TEXTURE_MAP = {
    "concrete": "assets/textures/concrete.jpg",
    "gypsum": "assets/textures/gypsum.jpg",
    "glass": "assets/textures/glass.png",
    "marble": "assets/textures/marble.jpg",
    "tile": "assets/textures/tile.jpg",
}


# ======================
# WALL HEIGHT LOGIC
# ======================

def get_wall_height_from_layer(layer: str):
    layer = layer.lower()
    if "full" in layer:
        return 3.0
    elif "head" in layer:
        return 1.2
    elif "partition" in layer:
        return 2.5
    elif "half" in layer:
        return 1.5
    else:
        return DEFAULT_WALL_HEIGHT


# ======================
# ROOM CLASSIFICATION
# ======================

def classify_room(room_poly: Polygon):
    area = room_poly.area
    minx, miny, maxx, maxy = room_poly.bounds
    w = maxx - minx
    h = maxy - miny
    aspect_ratio = max(w, h) / max(0.01, min(w, h))

    if aspect_ratio > 4:
        return "corridor"
    elif area < 6:
        return "bathroom"
    elif area < 12:
        return "kitchen"
    elif area < 25:
        return "bedroom"
    else:
        return "living_room"


# ======================
# ROOM DETECTION FROM WALLS
# ======================

def detect_rooms_from_walls(walls):
    lines = []

    for wall in walls:
        try:
            lines.append(LineString(wall["points"]))
        except:
            continue

    merged = unary_union(lines)

    rooms = []
    for poly in polygonize(merged):
        if poly.area > 5:
            rooms.append(poly)

    return rooms


# ======================
# PBR TEXTURE FUNCTION
# ======================

def apply_pbr_texture(mesh, material_name):
    texture_path = TEXTURE_MAP.get(material_name)

    if texture_path is None:
        return mesh

    image = Image.open(texture_path).convert("RGBA")
    image_np = np.array(image)

    material = PBRMaterial(
        baseColorTexture=image_np,
        metallicFactor=0.0,
        roughnessFactor=0.8
    )

    mesh.visual.material = material
    return mesh


# ======================
# MAIN FUNCTION
# ======================

def build_mesh(geometry, output_path, floor_index=0):
    meshes = []
    z_offset = floor_index * FLOOR_STEP

    # ------------------
    # ROOM DETECTION
    # ------------------
    room_polys = detect_rooms_from_walls(geometry["walls"])
    print(f"✅ Rooms detected: {len(room_polys)}")

    # ------------------
    # WALLS (ML MATERIAL CLASSIFICATION)
    # ------------------
    wall_meshes = []

    for wall in geometry["walls"]:
        pts = wall["points"]
        layer = wall["layer"]

        try:
            line = LineString(pts)
            poly = line.buffer(WALL_THICKNESS)

            if not poly.is_valid or poly.area < 0.1:
                continue

            wall_height = get_wall_height_from_layer(layer)

            # --- Extract ML features ---
            features = extract_wall_features(poly, wall_height, layer)

            # --- Predict material using XGBoost ---
            material = predict_material(features)
            print(f"🧠 Wall material predicted: {material}")

            # --- Create mesh ---
            mesh = trimesh.creation.extrude_polygon(poly, height=wall_height)
            mesh.apply_translation((0, 0, z_offset))

            # --- Apply PBR texture ---
            mesh = apply_pbr_texture(mesh, material)

            wall_meshes.append(mesh)

        except Exception as e:
            print("Wall error:", e)

    if not wall_meshes:
        raise ValueError("No wall meshes generated")

    wall_mesh = trimesh.util.concatenate(wall_meshes)
    meshes.append(wall_mesh)

    # ------------------
    # WINDOWS (glass PBR)
    # ------------------
    for win in geometry.get("windows", []):
        try:
            line = LineString(win)
            poly = line.buffer(WALL_THICKNESS)

            win_mesh = trimesh.creation.extrude_polygon(poly, height=WINDOW_HEIGHT)
            win_mesh.apply_translation((0, 0, z_offset + WINDOW_BASE))

            win_mesh = apply_pbr_texture(win_mesh, "glass")

            meshes.append(win_mesh)

        except Exception as e:
            print("Window error:", e)

    # ------------------
    # ROOMS (floor texture)
    # ------------------
    for room in room_polys:
        room_type = classify_room(room)
        print(f"🧠 Room classified as: {room_type}")

        room_mesh = trimesh.creation.extrude_polygon(room, height=ROOM_HEIGHT)
        room_mesh.apply_translation((0, 0, z_offset + 0.01))

        # Assign floor texture (tile for now)
        room_mesh = apply_pbr_texture(room_mesh, "tile")

        meshes.append(room_mesh)

    # ------------------
    # FINAL MESH
    # ------------------
    final_mesh = trimesh.util.concatenate(meshes)
    final_mesh.apply_translation(-final_mesh.centroid)

    glb_path = output_path.with_suffix(".glb")
    final_mesh.export(glb_path)

    print("✅ GLB exported:", glb_path)
