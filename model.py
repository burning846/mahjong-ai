import torch
import torch.nn as nn
import torch.nn.functional as F

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        layers = []
        layers.append(nn.Conv2d(in_channels=51, out_channels=256, kernel_size=3, stride=1, padding=1, bias=False))
        for _ in range(1):
            layers.append(nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, stride=1, padding=1, bias=False))
            layers.append(nn.ReLU(inplace=True))

        self.feature = nn.Sequential(*layers)
        self.pooling = nn.AdaptiveAvgPool2d(output_size=1)
        self.fc = nn.Linear(in_features=256, out_features=1024)
        self.out = nn.Linear(in_features=1024, out_features=36)

    def forward(self, x):
        x = self.feature(x)
        x = self.pooling(x)
        x = self.fc(x)
        x = self.out(x)
        x = F.softmax(x)
        return x