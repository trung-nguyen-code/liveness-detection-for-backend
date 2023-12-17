from model_factory import ClassifierFactory
from data_loader import FaceNoFaceloader
from jobs import Trainer

from google.cloud import storage
import os
import shutil
import splitfolders
import argparse
import torch
import torch.nn as nn
import zipfile
from PIL import Image
from PIL import ImageFile
import cv2
import pandas as pd
from datetime import datetime
import pathlib
from torch.utils.tensorboard import SummaryWriter

ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_args():
    """Argument parser.
    Returns:
        Dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description="PyTorch Efficientnet")
    parser.add_argument("--job-dir", type=str, help="Where to save the model")
    parser.add_argument("--version", type=str, default="1", help="model version")
    parser.add_argument(
        "--model-name",
        type=str,
        default="efficientnet",
        help="What to name the saved model file",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="FACES_NOFACE",
        help="name of dataset file",
    )
    parser.add_argument(
        "--model-bucket",
        type=str,
        default="mek_models",
        help="name of model bucket to save model",
    )
    parser.add_argument(
        "--dataset-bucket",
        type=str,
        default="mek_datasets",
        help="bucket of dataset file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="input batch size for training (default: 4)",
    )
    parser.add_argument(
        "--test-split",
        type=float,
        default=0.2,
        help="split size for training / testing dataset",
    )
    parser.add_argument(
        "--epochs", type=int, default=50, help="number of epochs to train (default: 5)"
    )
    parser.add_argument(
        "--lr", type=float, default=2.33e-04, help="learning rate (default: 2.33E-04)"
    )
    parser.add_argument(
        "--patience", type=float, default=20, help="learning rate patience count"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="random seed (default: 42)"
    )
    parser.add_argument(
        "--env", type=str, default="STAGING", help="random seed (default: STAGING)"
    )
    args = parser.parse_args()

    return args


def main():
    args = get_args()
    gs_client = storage.Client.from_service_account_json("certs/mek_gs.json")

    mek_datasets_bucket = gs_client.get_bucket(args.dataset_bucket)
    pytorch_training_bucket = gs_client.get_bucket(args.model_bucket)
    job_event_bucket = gs_client.get_bucket("mek_ai_job_dir")

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

    """Prepare dataset"""
    metrics_path = "{}/models.csv".format(args.env)
    csv_blob = pytorch_training_bucket.blob(metrics_path)
    csv_blob.download_to_filename(metrics_path)
    model_metrics = pd.read_csv(metrics_path)

    blob = mek_datasets_bucket.blob("{}.zip".format(args.dataset_name))
    blob.download_to_filename("{}.zip".format(args.dataset_name))
    with zipfile.ZipFile("{}.zip".format(args.dataset_name), "r") as zip_ref:
        zip_ref.extractall("face_noface")
    splitfolders.ratio(
        "./face_noface/{}".format(args.dataset_name),
        output="output",
        seed=1337,
        ratio=(0.8, 0.1, 0.1),
        group_prefix=None,
    )
    face_noface_dataloader = FaceNoFaceloader(150, 8, "./output")
    dataloaders, encoder, inv_normalize = face_noface_dataloader.load_data()

    """Produce model"""
    classifier_factory = ClassifierFactory()
    face_classifier = classifier_factory.create_classifier()
    print(f"{face_classifier.model_log()}")
    criterion = nn.CrossEntropyLoss()

    trainer = Trainer(
        model=face_classifier,
        dataloaders=dataloaders,
        criterion=criterion,
        num_epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch_size,
        patience=args.patience,
        encoder=encoder,
        inv_normalize=inv_normalize,
        train_writer=train_writer,
        test_writer=test_writer,
    )
    """Start training"""
    model = trainer.train_model()
    val_accuracy = trainer.accuracy
    val_losses = trainer.losses

    print("val_accuracy: ", val_accuracy)
    print("highest val_accuracy: ", max(val_accuracy))

    """Trace model to get weight"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test_transforms = face_noface_dataloader.get_test_transform()
    image = cv2.imread("./test.jpg")
    image = Image.fromarray(image)
    image = test_transforms(image)
    data = image.expand(1, -1, -1, -1)
    data = data.type(torch.FloatTensor).to(device)
    model.resnet.set_swish(memory_efficient=False)
    traced_fn = torch.jit.trace(model, data)
    model_path = "{}/{}/{}/{}/{}.pt".format(
        args.env, args.model_name, args.version, current_date, "saved_model"
    )
    traced_fn.save(model_path)

    to_append = [
        now_date,
        args.model_name,
        args.version,
        "gs://mek_models/{}/{}/{}/{}/{}.pt".format(
            args.env, args.model_name, args.version, current_date, "saved_model"
        ),
        "classifier",
        args.dataset_name,
        args.dataset_name,
        max(val_accuracy),
        min(val_losses),
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
        shutil.rmtree("face_noface", ignore_errors=True)
        shutil.rmtree(tensorboard_train_dir, ignore_errors=True)
        shutil.rmtree(tensorboard_test_dir, ignore_errors=True)

        os.remove("{}.zip".format(args.dataset_name))
    except Exception as e:
        print("[ERROR]: ", e)
        pass


if __name__ == "__main__":
    main()
