import trimesh
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


def render_multiview(obj_path, output_dir, base_name):
    mesh = trimesh.load(obj_path)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    views = {
        "front": (0, 0),
        "side": (90, 0),
        "top": (0, 90),
        "iso": (45, 30)
    }

    for view_name, (azim, elev) in views.items():
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='3d')

        vertices = mesh.vertices
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], s=1)

        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()

        output_path = Path(output_dir) / f"{base_name}_{view_name}.png"
        plt.savefig(output_path, bbox_inches="tight", pad_inches=0)
        plt.close()

        print(f"Saved view: {output_path}")

