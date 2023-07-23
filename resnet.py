import torch
import torch.nn as nn


class ResBlock(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.conv1 = nn.Conv2d(num_features, num_features, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_features, num_features, 3, 1, 1)
        self.bnorm1 = nn.BatchNorm2d(num_features)
        self.bnorm2 = nn.BatchNorm2d(num_features)
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        x = self.conv1(x)
        x = self.bnorm1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bnorm2(x)
        x += residual
        x = self.relu(x)
        return x


class ResNet(nn.Module):
    def __init__(self, num_blocks, num_features, policy_size, device="cpu") -> None:
        super().__init__()
        self.device = device
        self.start_block = nn.Sequential(
            nn.Conv2d(1, num_features, 3, 1, 1),
            nn.BatchNorm2d(num_features),
            nn.ReLU()
        )
        self.blocks = nn.ModuleList(
            [ResBlock(num_features) for _ in range(num_blocks)]
        )
        self.policy = nn.Sequential(
            nn.Conv2d(num_features, num_features, 1, 1, 0),
            nn.BatchNorm2d(num_features),
            nn.ReLU(),
            nn.Conv2d(num_features, num_features, 1, 1, 0),
            nn.BatchNorm2d(num_features),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(num_features*policy_size, policy_size)
        )
        self.value = nn.Sequential(
            nn.Conv2d(num_features, 1, 1, 1, 0),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(num_features*policy_size, 1),
            nn.Tanh()
        )
        self.to(device)

    def forward(self, x):
        x = self.start_block(x)
        for block in self.blocks:
            x = block(x)
        p = self.policy(x)
        v = self.value(x)
        return p, v

    def get_tensor_board(self, board):
        return torch.tensor(board).unsqueeze(0).unsqueeze(0).float().to(self.device)

    def get_policy(self, p):
        return torch.softmax(p, 1).squeeze(0).detach().cpu().numpy()

    def get_value(self, v):
        return v.item()
