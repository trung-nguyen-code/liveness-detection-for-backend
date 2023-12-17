import torch
from torchvision import transforms
from google.cloud import storage
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
from PIL import Image
import numpy as np
import cv2
import torchvision
from tqdm import tqdm
from PIL import ImageFile
import datetime

ImageFile.LOAD_TRUNCATED_IMAGES = True


class FaceNoFaceloader:
    def __init__(self, img_size, batch_size, src_dir):
        self.img_size = img_size
        self.batch_size = batch_size
        self.root = src_dir
        self.train_transforms = transforms.Compose(
            [transforms.Resize((img_size, img_size)), transforms.ToTensor()]
        )

    def get_test_transform(self):
        return self.test_transforms

    def normalization_parameter(self, dataloader):
        mean = 0.0
        std = 0.0
        nb_samples = len(dataloader.dataset)
        for data, _ in tqdm(dataloader):
            batch_samples = data.size(0)
            data = data.view(batch_samples, data.size(1), -1)
            mean += data.mean(2).sum(0)
            std += data.std(2).sum(0)
        mean /= nb_samples
        std /= nb_samples
        return mean.numpy(), std.numpy()

    def load_data(self):
        self.train_data = torchvision.datasets.ImageFolder(
            self.root, transform=self.train_transforms
        )
        self.train_loader = DataLoader(
            self.train_data, batch_size=self.batch_size, shuffle=True
        )
        mean, std = self.normalization_parameter(self.train_loader)

        self.train_transforms = transforms.Compose(
            [
                transforms.Resize((self.img_size, self.img_size)),
                transforms.RandomResizedCrop(size=315, scale=(0.95, 1.0)),
                transforms.RandomRotation(degrees=10),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean, std),
            ]
        )
        self.test_transforms = transforms.Compose(
            [
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean, std),
            ]
        )
        inv_normalize = transforms.Normalize(
            mean=-1 * np.divide(mean, std), std=1 / std
        )
        dataloader = self.build_data_loader()
        return dataloader, self.encoder, inv_normalize

    def data_loader(self, train_data, test_data=None, valid_size=None, batch_size=32):
        train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
        if test_data is None and valid_size is None:
            dataloaders = {"train": train_loader}
            return dataloaders
        if test_data is None and valid_size is not None:
            data_len = len(train_data)
            indices = list(range(data_len))
            np.random.shuffle(indices)
            split1 = int(np.floor(valid_size * data_len))
            valid_idx, test_idx = indices[:split1], indices[split1:]
            valid_sampler = SubsetRandomSampler(valid_idx)
            valid_loader = DataLoader(
                train_data, batch_size=batch_size, sampler=valid_sampler
            )
            dataloaders = {"train": train_loader, "val": valid_loader}
            return dataloaders
        if test_data is not None and valid_size is not None:
            data_len = len(test_data)
            indices = list(range(data_len))
            np.random.shuffle(indices)
            split1 = int(np.floor(valid_size * data_len))
            valid_idx, test_idx = indices[:split1], indices[split1:]
            valid_sampler = SubsetRandomSampler(valid_idx)
            test_sampler = SubsetRandomSampler(test_idx)
            valid_loader = DataLoader(
                test_data, batch_size=batch_size, sampler=valid_sampler
            )
            test_loader = DataLoader(
                test_data, batch_size=batch_size, sampler=test_sampler
            )
            dataloaders = {
                "train": train_loader,
                "val": valid_loader,
                "test": test_loader,
            }
            return dataloaders

    def build_data_loader(self):
        # data loader
        train_data = torchvision.datasets.ImageFolder(
            self.root + "/train", transform=self.train_transforms
        )
        test_data = torchvision.datasets.ImageFolder(
            self.root + "/val", transform=self.test_transforms
        )
        dataloaders = self.data_loader(
            train_data, test_data, valid_size=0.2, batch_size=self.batch_size
        )
        # label of classes
        classes = train_data.classes
        print(classes)
        # encoder and decoder to convert classes into integer
        decoder = {}
        for i in range(len(classes)):
            decoder[classes[i]] = i
        encoder = {}
        for i in range(len(classes)):
            encoder[i] = classes[i]
        print(encoder)
        self.encoder = encoder
        return dataloaders

    def save_model(self, model, model_dir):
        """Saves the model to Google Cloud Storage"""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        image = cv2.imread("./test.jpg")
        image = Image.fromarray(image)
        image = self.test_transforms(image)
        data = image.expand(1, -1, -1, -1)
        data = data.type(torch.FloatTensor).to(device)
        model.resnet.set_swish(memory_efficient=False)
        traced_fn = torch.jit.trace(model, data)
        traced_fn.save("traced_efficientnet.pt")

        bucket = storage.Client().bucket(model_dir)
        blob = bucket.blob(
            "{}/{}".format(
                datetime.now().strftime("torch_%Y%m%d_%H%M%S"),
                "traced_efficientnet",
            )
        )
        blob.upload_from_filename("traced_efficientnet")


# face_noface_loader = FaceNoFaceloader(150, 8, r"C:\Users\thanh.nt163727\Downloads
# \FACES_CLASSIFIED\FACES_CLASSIFIED").load_data()
# dataLoader =  face_noface_loader.build_data_loader()
