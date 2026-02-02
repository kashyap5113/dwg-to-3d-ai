import torch
import torch.nn as nn
import torch.nn.functional as F


class Decoder(nn.Module):
    """
    Decoder: takes feature vector and outputs 3D point cloud
    Input: (B, 256)
    Output: (B, N, 3) where N = number of points
    """

    def __init__(self, num_points=512):
        super(Decoder, self).__init__()
        self.num_points = num_points

        self.fc1 = nn.Linear(256, 512)
        self.fc2 = nn.Linear(512, 1024)
        self.fc3 = nn.Linear(1024, num_points * 3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        x = x.view(-1, self.num_points, 3)
        return x
