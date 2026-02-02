import os
import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import trimesh
import numpy as np

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from model.encoder import Encoder
from model.decoder import Decoder


DATASET_IMAGES = Path("dataset/images")
DATASET_MODELS = Path("dataset/models")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class CAD3DDataset(Dataset):
    def __init__(self, image_dir, model_dir):
        self.image_files = sorted(image_dir.glob("*.png"))
        self.model_files = sorted(model_dir.glob("*.obj"))

        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((128, 128)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img = Image.open(self.image_files[idx])
        img = self.transform(img)

        mesh = trimesh.load(self.model_files[idx])
        vertices = mesh.vertices

        # Sample fixed number of points (512)
        if len(vertices) >= 512:
            indices = np.random.choice(len(vertices), 512, replace=False)
        else:
            indices = np.random.choice(len(vertices), 512, replace=True)

        points = vertices[indices]
        points = torch.tensor(points, dtype=torch.float32)

        return img, points


def train():
    dataset = CAD3DDataset(DATASET_IMAGES, DATASET_MODELS)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    encoder = Encoder().to(DEVICE)
    decoder = Decoder(num_points=512).to(DEVICE)

    optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-3)
    criterion = nn.MSELoss()

    epochs = 10

    for epoch in range(epochs):
        total_loss = 0

        for images, points in dataloader:
            images = images.to(DEVICE)
            points = points.to(DEVICE)

            features = encoder(images)
            outputs = decoder(features)

            loss = criterion(outputs, points)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(dataloader):.4f}")

    torch.save(encoder.state_dict(), "encoder.pth")
    torch.save(decoder.state_dict(), "decoder.pth")

    print("✅ Training completed and models saved!")


if __name__ == "__main__":
    train()
