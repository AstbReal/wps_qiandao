from utils.checkin import Checkin

import torch.nn as nn
import torch.nn.functional as F


if __name__ == "__main__":
    Checkin().checkAndSendMsg()

class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 128, 3, padding=1)
            self.conv2 = nn.Conv2d(128, 64, 3, padding=1)
            self.conv3 = nn.Conv2d(64, 32, 3, padding=1)
            self.fc1 = nn.Linear(32 * 25, 40)
            self.fc2 = nn.Linear(40, 2)

        def forward(self, x):
            x = F.max_pool2d(F.relu(self.conv1(x)), 2)
            x = F.max_pool2d(F.relu(self.conv2(x)), 2)
            x = F.max_pool2d(F.relu(self.conv3(x)), 2)
            x = x.view(-1, self.num_flat_features(x))
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return x

        def num_flat_features(self, x):
            size = x.size()[1:]  # all dimensions except the batch dimension
            num_features = 1
            for s in size:
                num_features *= s
            return num_features