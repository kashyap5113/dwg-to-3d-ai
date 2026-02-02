import torch
import torch.nn as nn
import torch.nn.functional as F


class Encoder(nn.Module):
    """
    Encoder: takes 2D PNG image and converts it into a feature vector
    Input: (B, 1, 128, 128)
    Output: (B, 256)
    """

    def __init__(self):
        super(Encoder, self).__init__()

        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1)

        self.fc = nn.Linear(128 * 8 * 8, 256)

    def forward(self, x):
        x = F.relu(self.conv1(x))  # (B,16,64,64)
        x = F.relu(self.conv2(x))  # (B,32,32,32)
        x = F.relu(self.conv3(x))  # (B,64,16,16)
        x = F.relu(self.conv4(x))  # (B,128,8,8)

        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x
