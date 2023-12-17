import torch.nn as nn
from torch.optim import lr_scheduler
from torchvision import models
import torch.optim as optim


def init(device="cpu"):
    model_ft = models.resnet152(pretrained=True)
    num_ftrs = model_ft.fc.in_features
    # Here the size of each output sample is set to 2.
    # Alternatively, it can be generalized to nn.Linear(num_ftrs, len(class_names)).
    model_ft.fc = nn.Linear(num_ftrs, 2)

    model_ft = model_ft.to(device)

    criterion = nn.CrossEntropyLoss()

    # Observe that all parameters are being optimized
    optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

    return {
        "model": model_ft,
        "criterion": criterion,
        "optimizer": optimizer_ft,
        "lr_scheduler": exp_lr_scheduler,
    }
