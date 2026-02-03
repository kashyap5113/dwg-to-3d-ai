from pathlib import Path
from dwg_parser.parse_dwg import parse_dwg, save_json
from preprocessing.extract_geometry import geometry_to_3d
from preprocessing.multiview_renderer import render_multiview
from renderer.dxf_to_png import dxf_to_png
import trimesh
import numpy as np


INPUT_DIR = Path("data/input_dwg")
JSON_DIR = Path("data/processed")
OBJ_DIR = Path("dataset/models")
IMG_DIR = Path("dataset/images_multiview")


def save_obj(vertices, path):
    mesh = trimesh.points.PointCloud(vertices)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)


def build_dataset():
    idx = 1

    for dxf_file in INPUT_DIR.glob("*.dxf"):
        print(f"Processing {dxf_file.name}")

        entities = parse_dwg(dxf_file)
        json_path = JSON_DIR / f"{idx:03}.json"
        save_json(entities, json_path)

        vertices = geometry_to_3d(json_path)

        if vertices is None:
            print(f"Skipping {dxf_file.name}")
            continue

        obj_path = OBJ_DIR / f"{idx:03}.obj"
        save_obj(vertices, obj_path)

        # Generate multi-view images
        render_multiview(obj_path, IMG_DIR, f"{idx:03}")

        idx += 1

    print("✅ Multi-view dataset generation completed!")


if __name__ == "__main__":
    build_dataset()
