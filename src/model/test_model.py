import torch
from encoder import Encoder
from decoder import Decoder

encoder = Encoder()
decoder = Decoder(num_points=512)

dummy_img = torch.randn(1, 1, 128, 128)

features = encoder(dummy_img)
points = decoder(features)

print("Feature shape:", features.shape)
print("Point cloud shape:", points.shape)
