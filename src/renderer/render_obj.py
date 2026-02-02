import trimesh
from pathlib import Path


def save_obj(vertices, output_path):
    cloud = trimesh.points.PointCloud(vertices)

    # Convert point cloud to mesh (convex hull)
    if len(vertices) >= 4:
        mesh = cloud.convex_hull
    else:
        mesh = cloud

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    mesh.export(output_path)
