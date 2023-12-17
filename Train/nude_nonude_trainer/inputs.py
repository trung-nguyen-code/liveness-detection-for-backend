import torch
from torchvision import datasets, transforms
import os
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Dataloader:
    def __init__(self, img_size, batch_size, src_dir):
        self.img_size = img_size
        self.batch_size = batch_size
        self.root = src_dir
        self.data_transforms = {
            "train": transforms.Compose(
                [
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomVerticalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ]
            ),
            "val": transforms.Compose(
                [
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ]
            ),
            "test": transforms.Compose(
                [
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ]
            ),
        }

    def load_data(self):
        image_datasets = {
            x: datasets.ImageFolder(os.path.join(self.root, x), self.data_transforms[x])
            for x in ["train", "val", "test"]
        }
        dataloaders = {
            x: torch.utils.data.DataLoader(
                image_datasets[x], batch_size=32, shuffle=True, num_workers=2
            )
            for x in ["train", "val", "test"]
        }
        dataset_sizes = {x: len(image_datasets[x]) for x in ["train", "val", "test"]}
        class_names = image_datasets["train"].classes
        print("Classes: ", class_names)
        return dataloaders, dataset_sizes
