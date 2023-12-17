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

import pandas as pd

from google.cloud import storage
import tensorflow as tf
from tensorflow import keras

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
    # Load model
    # Using CPU instead of GPU
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    # os.environ["CUDA_VISIBLE_DEVICES"] = ""

    print("Evaluating model " + model_name + " version " + str(model_version))
    model = keras.models.load_model(local_model)
    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
        test_path,
        validation_split=0.2,
        subset="validation",
        seed=2412,
        image_size=(image_height, image_width),
        batch_size=batch_size,
    )

    loss, acc = model.evaluate(test_ds, batch_size=batch_size)
    print("Loss: ", loss, " Accuracy: ", acc)

    return loss, acc, local_model


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
    loss, acc, local_model = eval_model(
        df["name"],
        df["version"],
        df["path"],
        df["testset"],
        df["required_accuracy"],
        args.batch_size,
        args.image_height,
        args.image_width,
    )

    # Only move to PROD if current accuracy is enough
    if acc >= df["required_accuracy"] or args.force:
        deploy(
            args.model_name,
            args.model_version,
            acc,
            loss,
            local_model,
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
        "sunglasses",
        "1",
        "gs://mek_models/STAGING/sunglasses/1/2021-08-27 15:50:29.128994",
        "FACES_CLASSIFIED_224",
        0.98,
        32,
        224,
        224,
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
