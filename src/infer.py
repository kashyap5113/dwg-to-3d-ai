import sys
from pathlib import Path
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
import trimesh
import matplotlib.pyplot as plt

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from model.encoder import Encoder
from model.decoder import Decoder
from renderer.mesh_reconstruction import pointcloud_to_mesh


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_ENCODER_PATH = "encoder.pth"
MODEL_DECODER_PATH = "decoder.pth"

INPUT_IMAGE = "dataset/images/001.png"
OUTPUT_OBJ_POINTS = "data/output_3d/ai_points.obj"
OUTPUT_OBJ_MESH = "data/output_3d/ai_mesh.obj"
DEBUG_SCATTER = "data/output_3d/debug_scatter.png"


def load_image(image_path):
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((128, 128)),
        transforms.ToTensor()
    ])

    img = Image.open(image_path)
    img = transform(img)
    img = img.unsqueeze(0)
    return img


def save_pointcloud_as_obj(points, output_path):
    mesh = trimesh.points.PointCloud(points)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    mesh.export(output_path)


def infer():
    encoder = Encoder().to(DEVICE)
    decoder = Decoder(num_points=512).to(DEVICE)

    encoder.load_state_dict(torch.load(MODEL_ENCODER_PATH, map_location=DEVICE))
    decoder.load_state_dict(torch.load(MODEL_DECODER_PATH, map_location=DEVICE))

    encoder.eval()
    decoder.eval()

    img = load_image(INPUT_IMAGE).to(DEVICE)

    with torch.no_grad():
        features = encoder(img)
        points = decoder(features)

    points = points.squeeze(0).cpu().numpy()

    # Save raw point cloud
    save_pointcloud_as_obj(points, OUTPUT_OBJ_POINTS)

    # 🔥 Convert point cloud to surface mesh
    mesh = pointcloud_to_mesh(points, OUTPUT_OBJ_MESH)

    # Debug visualization
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=2)
    ax.set_axis_off()
    plt.savefig(DEBUG_SCATTER)
    plt.close()

    print("✅ AI inference completed!")
    print(f"Point cloud OBJ: {OUTPUT_OBJ_POINTS}")
    print(f"Mesh OBJ: {OUTPUT_OBJ_MESH}")
    print(f"Debug scatter saved: {DEBUG_SCATTER}")


if __name__ == "__main__":
    infer()
