from efficientnet_pytorch import EfficientNet
import torch.nn as nn
from model_abstract import AbstractClassifier


class EfficientnetClassifier(AbstractClassifier, nn.Module):
    def __init__(self):
        super(EfficientnetClassifier, self).__init__()
        self.resnet = EfficientNet.from_pretrained("efficientnet-b0")
        self.l1 = nn.Linear(1000, 256)
        self.dropout = nn.Dropout(0.75)
        self.l2 = nn.Linear(256, 6)
        self.relu = nn.ReLU()

    def forward(self, input):
        x = self.resnet(input)
        x = x.view(x.size(0), -1)
        x = self.dropout(self.relu(self.l1(x)))
        x = self.l2(x)
        return x

    def model_log(self):
        return "The result of FacenofaceClassifier"
