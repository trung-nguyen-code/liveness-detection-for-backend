# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the \"License\");
# you may not use this file except in compliance with the License.\n",
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an \"AS IS\" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from model_factory import ClassifierFactory
from inputs import Dataloader

import torch
import torch.optim as optim
import torch.nn as nn
from torch.optim import lr_scheduler
from google.cloud import storage
import zipfile
import time
import copy
import splitfolders
import cv2
from torchvision import models
from PIL import Image
from PIL import ImageFile
import pathlib
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import pandas as pd
import os
import shutil

ImageFile.LOAD_TRUNCATED_IMAGES = True

# flake8: noqa: C901
def train_model(
    model,
    criterion,
    optimizer,
    scheduler,
    dataloaders,
    device,
    dataset_sizes,
    train_writer,
    test_writer,
    num_epochs=25,
):
    # wandb.watch(model_ft,criterion, log="all", log_freq=100)
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    min_loss = 1000

    for epoch in range(num_epochs):
        print("Epoch {}/{}".format(epoch, num_epochs - 1))
        print("-" * 10)

        # Each epoch has a training and validation phase
        for phase in ["train", "val"]:
            if phase == "train":
                model.train()  # Set model to training mode
            else:
                model.eval()  # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == "train"):
                    outputs = model.forward(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == "train":
                        loss.backward()
                        optimizer.step()
                        # wandb.log({"loss": loss})

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            if phase == "train":
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            if phase == "train":
                train_writer.add_scalar(
                    "Loss", running_loss / dataset_sizes[phase], epoch
                )
                train_writer.add_scalar(
                    "Accuracy", running_corrects.double() / dataset_sizes[phase], epoch
                )

            if phase == "val":
                test_writer.add_scalar(
                    "Loss", running_loss / dataset_sizes[phase], epoch
                )
                test_writer.add_scalar(
                    "Accuracy", running_corrects.double() / dataset_sizes[phase], epoch
                )

            print("{} Loss: {:.4f} Acc: {:.4f}".format(phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == "val" and epoch_acc > best_acc:
                best_acc = epoch_acc.item()
                best_model_wts = copy.deepcopy(model.state_dict())
            if phase == "val" and epoch_loss < min_loss:
                min_loss = epoch_loss

    time_elapsed = time.time() - since
    print(
        "Training complete in {:.0f}m {:.0f}s".format(
            time_elapsed // 60, time_elapsed % 60
        )
    )
    print("Best val Acc: {:4f}".format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model, best_acc, min_loss


def run(args):
    """Load the data, train, evaluate, and export the model for serving and
     evaluating.
    Args:
      args: experiment parameters.
    """
    cuda_availability = torch.cuda.is_available()
    # device = "cpu"
    if cuda_availability:
        device = torch.device("cuda:{}".format(torch.cuda.current_device()))
    else:
        device = "cpu"
    print("\n*************************")
    print("`cuda` available: {}".format(cuda_availability))
    print("Current Device: {}".format(device))
    print("*************************\n")
    torch.cuda.empty_cache()
    now_date = datetime.now()
    current_date = str(now_date).replace(":", "")
    pathlib.Path(
        "{}/{}/{}/{}".format(args.env, args.model_name, args.version, current_date)
    ).mkdir(parents=True, exist_ok=True)

    gs_client = storage.Client.from_service_account_json("certs/mek_gs.json")

    mek_datasets_bucket = gs_client.get_bucket(args.dataset_bucket)
    pytorch_training_bucket = gs_client.get_bucket(args.model_bucket)
    job_event_bucket = gs_client.get_bucket("mek_ai_job_dir")

    metrics_path = "{}/models.csv".format(args.env)

    blob = mek_datasets_bucket.blob("{}.zip".format(args.dataset_name))
    blob.download_to_filename("tmp.zip")
    with zipfile.ZipFile("tmp.zip", "r") as zip_ref:
        zip_ref.extractall("tmp")
    splitfolders.ratio(
        "./tmp/{}".format(args.dataset_name),
        output="output",
        seed=1337,
        ratio=(0.8, 0.1, 0.1),
        group_prefix=None,
    )  # default values
    csv_blob = pytorch_training_bucket.blob(metrics_path)
    csv_blob.download_to_filename(metrics_path)
    model_metrics = pd.read_csv(metrics_path)

    # Open our dataset
    loaders = Dataloader(img_size=224, batch_size=1, src_dir="output")
    dataloaders, dataset_sizes = loaders.load_data()
    classifier_factory = ClassifierFactory()
    sunglasses_classifier = classifier_factory.create_classifier()
    sunglasses_classifier = sunglasses_classifier.to(device)
    # model_ft = models.resnet152(pretrained=True)
    # num_ftrs = model_ft.fc.in_features
    # # Here the size of each output sample is set to 2.
    # # Alternatively, it can be generalized to nn.Linear(num_ftrs, len(class_names)).
    # model_ft.fc = nn.Linear(num_ftrs, 2)

    # model_ft = model_ft.to(device)

    criterion = nn.CrossEntropyLoss()

    # Observe that all parameters are being optimized
    optimizer_ft = optim.SGD(sunglasses_classifier.parameters(), lr=0.001, momentum=0.9)

    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

    now_date = datetime.now()
    current_date = str(now_date).replace(":", "")
    pathlib.Path(
        "{}/{}/{}/{}".format(args.env, args.model_name, args.version, current_date)
    ).mkdir(parents=True, exist_ok=True)
    tensorboard_train_dir = "{}_{}/tensorboard/train".format(
        args.model_name, now_date.strftime("%d%m%Y_%H%M%S")
    )
    tensorboard_test_dir = "{}_{}/tensorboard/test".format(
        args.model_name, now_date.strftime("%d%m%Y_%H%M%S")
    )
    train_writer = SummaryWriter(tensorboard_train_dir)
    test_writer = SummaryWriter(tensorboard_test_dir)

    criterion = nn.CrossEntropyLoss()
    # optimizer_ft = optim.SGD(
    #     sunglasses_classifier.parameters(), lr=args.lr, momentum=args.momentum
    # )
    # exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

    model, best_acc, min_loss = train_model(
        sunglasses_classifier,
        criterion,
        optimizer_ft,
        exp_lr_scheduler,
        num_epochs=args.epochs,
        dataloaders=dataloaders,
        device=device,
        dataset_sizes=dataset_sizes,
        train_writer=train_writer,
        test_writer=test_writer,
    )
    # traced_fn = torch.jit.script(model)
    # model_path = "{}/{}/{}/{}/{}.pt".format(
    #     args.env, args.model_name, args.version, current_date, "saved_model"
    # )
    # traced_fn.save(model_path)
    test_transforms = loaders.data_transforms['test']
    image = cv2.imread("./test.jpg")
    image = Image.fromarray(image)
    image = test_transforms(image)
    data = image.expand(1, -1, -1, -1)
    data = data.type(torch.FloatTensor).to(device)
    traced_fn = torch.jit.trace(model, data)
    model_path = "{}/{}/{}/{}/{}.pt".format(
        args.env, args.model_name, args.version, current_date, "saved_model"
    )
    traced_fn.save(model_path)
    train_writer.close()
    test_writer.close()

    to_append = [
        now_date,
        args.model_name,
        args.version,
        "gs://mek_models/{}/{}/{}/{}/{}.pt".format(
            args.env, args.model_name, args.version, str(datetime.now()), "saved_model"
        ),
        "classifier",
        args.dataset_name,
        args.dataset_name,
        best_acc,
        min_loss,
        0.9,
    ]
    series = pd.Series(to_append, index=model_metrics.columns)
    model_metrics = model_metrics.append(series, ignore_index=True)
    model_metrics.to_csv(metrics_path, index=False)

    """Saves the model to Google Cloud Storage"""
    model_blob = pytorch_training_bucket.blob(model_path)
    model_blob.upload_from_filename(model_path)
    csv_blob.upload_from_filename(metrics_path)

    for event in os.listdir(tensorboard_train_dir):
        event_path = tensorboard_train_dir + "/{}".format(event)
        event_blob = job_event_bucket.blob(event_path)
        event_blob.upload_from_filename(event_path)

    for event in os.listdir(tensorboard_test_dir):
        event_path = tensorboard_test_dir + "/{}".format(event)
        event_blob = job_event_bucket.blob(event_path)
        event_blob.upload_from_filename(event_path)
    """ CLEAN UP """
    train_writer.close()
    try:
        shutil.rmtree(args.env, ignore_errors=True)
        shutil.rmtree("output", ignore_errors=True)
        shutil.rmtree("tmp", ignore_errors=True)
        shutil.rmtree(tensorboard_train_dir, ignore_errors=True)
        shutil.rmtree(tensorboard_test_dir, ignore_errors=True)

        os.remove("tmp.zip")
    except Exception as e:
        print("[ERROR]: ", e)
        pass
