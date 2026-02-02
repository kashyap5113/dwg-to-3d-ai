import trimesh
from pathlib import Path


def save_obj(vertices, output_path):
    mesh = trimesh.points.PointCloud(vertices)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    mesh.export(output_path)
