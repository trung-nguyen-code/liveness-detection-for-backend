"""
1. Read staging CSV
2. Download test set and model of model-name
3. Test accuracy of model-name in staging CSV, if accuracy >=required_accuracy proceed
4. Check if current accuracy >= prod_accuracy then update PRODUCTION model
"""

import argparse
import os
import glob
import shutil
import torch
import pandas as pd
from torchvision import datasets, models, transforms
from torch import jit
import torch.nn as nn
from google.cloud import storage
import splitfolders  # or import split_folders
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

import util

gs_client = 0


def init():
    global gs_client
    gs_client = storage.Client.from_service_account_json("mek_gs.json")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="Model name to be tested and deploy from Staging to Production",
    )
    parser.add_argument(
        "--model-version",
        type=str,
        required=True,
        help="Model version to be tested and deploy from Staging to Production",
    )
    parser.add_argument(
        "--force", type=bool, required=False, help="Force deploy even if test failed"
    )
    parser.add_argument(
        "--wandb", type=bool, required=False, help="Upload evaluation results to wandb"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        required=False,
        help="batch size, default 32",
    )
    parser.add_argument(
        "--image-height",
        type=int,
        default=224,
        required=False,
        help="image height, default 224",
    )
    parser.add_argument(
        "--image-width",
        type=int,
        default=224,
        required=False,
        help="image width, default 224",
    )

    args, _ = parser.parse_known_args()

    return args


def retrieve(model_name, model_version):
    global gs_client
    bucket = gs_client.get_bucket("mek_models")
    blob = bucket.blob("STAGING/models.csv")
    model_file = "models.csv"
    blob.download_to_filename(model_file)
    df = pd.read_csv(model_file)
    df = df[df.name == model_name]
    df.version = df.version.astype(str)
    df = df[df.version == str(model_version)]
    if len(df) > 0:
        df = df.iloc[df.accuracy.argmax()]
    os.remove(model_file)
    return df


def eval_model(
    model_name,
    model_version,
    model_path,
    test_path,
    require_accuracy,
    batch_size,
    image_height,
    image_width,
):
    print("model name: ", model_name)
    local_model, local_test = util.download(
        gs_client, model_name, model_version, model_path, test_path
    )

    # model = torch.jit.load("{}/saved_model.pt".format("resnet_face_mask/1/"))
    model = torch.load("{}/saved_model.pt".format(local_model))

    model.eval()

    test_transform = transforms.Compose(
        [
            transforms.Resize((150, 150)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.4812301, 0.4429657, 0.42894983],
                [0.23917997, 0.22995315, 0.22137189],
            ),
        ]
    )
    test_datasets = datasets.ImageFolder(
        os.path.join(test_path, "test"), test_transform
    )
    test_loader = torch.utils.data.DataLoader(
        test_datasets, batch_size=32, shuffle=True, num_workers=2
    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    correct = 0
    total = 0
    running_loss = 0
    # since we're not training, we don't need to calculate the gradients for our outputs
    was_training = model.training
    model.eval()
    images_so_far = 0
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for i, (inputs, labels) in enumerate(test_loader):
            print(inputs.shape)
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            total += labels.size(0)
            correct += (preds == labels).sum().item()
            running_loss += loss.item() * inputs.size(0)

        model.train(mode=was_training)
    acc = correct / total
    print(
        "Accuracy of the network on the {} test images: %d %%".format(
            len(test_datasets)
        )
        % (100 * acc)
    )
    print("Running loss: {}".format(running_loss))
    # Load model
    # Using CPU instead of GPU
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    # os.environ["CUDA_VISIBLE_DEVICES"] = ""

    print("Evaluating model " + model_name + " version " + str(model_version))

    # return loss, acc, local_model
    return running_loss, acc, model


def copy_local_directory_to_gcs(local_path, bucket, gcs_path):
    """Recursively copy a directory to GCS.

    local_path should be a directory and not have a trailing slash.
    """
    assert os.path.isdir(local_path)

    for local_file in glob.glob(local_path + "/**"):
        print(local_file)
        if not os.path.isfile(local_file):
            copy_local_directory_to_gcs(local_file, bucket, gcs_path)
        else:
            remote_path = os.path.join(gcs_path, local_file)
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def deploy(
    model_name,
    model_version,
    acc,
    loss,
    local_model_path,
    train_date,
    model_type,
    trainset,
    testset,
    staging_path,
    force=False,
):

    # Get list of prod models from cloud storage
    global gs_client
    bucket = gs_client.get_bucket("mek_models")
    blob = bucket.blob("PRODUCTION/prod.csv")
    model_file = "prod.csv"
    blob.download_to_filename(model_file)
    df_ori = pd.read_csv(model_file)
    df_ori.version = df_ori.version.astype(str)

    # Check current max accuracy.
    df = df_ori[df_ori.name == model_name].copy()
    df = df[df.version == str(model_version)]

    max_acc = 0
    # Get max accuracy
    if len(df) > 0:
        df = df.iloc[df.accuracy.argmax()]

        max_acc = df.accuracy

    if (acc > max_acc) or (args.force):
        # update CSV file

        line = [
            train_date,
            model_name,
            model_version,
            model_type,
            trainset,
            testset,
            acc,
            loss,
            staging_path,
        ]
        df_insert = df_ori[
            (df_ori.name != model_name) | (df_ori.version != str(model_version))
        ]

        a_series = pd.Series(line, index=df_insert.columns)
        df_insert = df_insert.append(a_series, ignore_index=True)

        tmp = "tmp.csv"
        df_insert.to_csv(tmp, index=False)

        blob = bucket.blob("PRODUCTION/prod.csv")
        # upload updated csv to cloud storage
        blob.upload_from_filename(tmp)
        os.remove(tmp)

        # copy model to PROD
        print("Start uploading model...")
        copy_local_directory_to_gcs(local_model_path, bucket, "PRODUCTION")
        print("End uploading model...")

    os.remove(model_file)
    # remove model
    shutil.rmtree(model_name)
    shutil.rmtree(testset)


def evaluate_and_deploy(args):
    df = retrieve(args.model_name, args.model_version)
    print("path",  df["path"])
    loss, acc, _ = eval_model(
        df["name"],
        df["version"],
        df["path"][0:len(df["path"]) - 15],
        df["testset"],
        df["required_accuracy"],
        args.batch_size,
        args.image_height,
        args.image_width,
    )
    print("Acc", acc, df["required_accuracy"], )
    # Only move to PROD if current accuracy is enough
    if acc >= df["required_accuracy"] or args.force:
        deploy(
            args.model_name,
            args.model_version,
            acc,
            loss,
            "{}/1".format(args.model_name),
            df["train date"],
            df["type"],
            df["trainset"],
            df["testset"],
            df["path"],
            args.force,
        )


def test_retrieve():
    retrieve("sunglasses", "1")


def test_evaluate():
    eval_model(
        "resnet_face_mask",
        "1",
        "gs://mek_models/STAGING/facemask_classifier/1/2021-09-22 11:14:03.901739",
        "FACE_MASK",
        0.95,
        32,
        150,
        150,
    )


def test_deploy():
    deploy(
        "sunglasses",
        "1",
        0.982,
        0.1,
        "sunglasses/1",
        "10:31",
        "classifier",
        "trainpath",
        "testpath",
        "staging_path",
        True,
    )


if __name__ == "__main__":
    init()
    args = get_args()
    # test_retrieve()
    # test_download()
    # test_evaluate()
    # test_deploy()
    evaluate_and_deploy(args)
