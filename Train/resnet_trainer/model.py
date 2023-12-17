import torch.nn as nn
from model_abstract import AbstractClassifier
from torchvision import models


class ResnetClassifier(AbstractClassifier, nn.Module):
    def __init__(self):
        super(ResnetClassifier, self).__init__()
        self.model = models.resnet152(pretrained=True)
        self.num_ftrs = self.model.fc.in_features
        self.fc = nn.Linear(self.num_ftrs, 2)

    def forward(self, input):
        self.model.fc = self.fc
        x = self.model(input)
        return x

    def model_log(self):
        return "The result of ResnetClassifier"
