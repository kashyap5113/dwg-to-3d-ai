import os
os.environ["PYOPENGL_PLATFORM"] = "egl"

import trimesh
import pyrender
import numpy as np
from PIL import Image
from pathlib import Path


def render_png(obj_path, output_png):
    mesh = trimesh.load(obj_path)

    scene = pyrender.Scene(bg_color=[255, 255, 255, 255])

    if isinstance(mesh, trimesh.points.PointCloud):
        points = mesh.vertices
        colors = np.ones_like(points)
        cloud = pyrender.Mesh.from_points(points, colors=colors)
        scene.add(cloud)
    else:
        mesh = pyrender.Mesh.from_trimesh(mesh)
        scene.add(mesh)

    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
    camera_pose = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, -2],
        [0, 0, 1, 2],
        [0, 0, 0, 1],
    ])
    scene.add(camera, pose=camera_pose)

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    scene.add(light, pose=camera_pose)

    r = pyrender.OffscreenRenderer(640, 480)
    color, _ = r.render(scene)

    img = Image.fromarray(color)
    Path(output_png).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_png)

    r.delete()
