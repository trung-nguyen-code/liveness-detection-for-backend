import argparse
import os
import shutil

from google.cloud import storage
import tensorflow as tf
from tensorflow import keras
import numpy as np

import wandb
import util

IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
BATCH_SIZE = 32


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name", type=str, required=True, help="Model name to be evaluated"
    )
    parser.add_argument(
        "--model-version", type=str, required=True, help="Model version to be evaluated"
    )

    parser.add_argument(
        "--model-path", type=str, required=True, help="Model path to be evaluated"
    )
    parser.add_argument("--test-set", type=str, required=True, help="test set path")

    args, _ = parser.parse_known_args()

    return args


def init(args):
    gs_client = storage.Client.from_service_account_json("mek_gs.json")

    util.download(
        gs_client, args.model_name, args.model_version, args.model_path, args.test_set
    )

    util.init_wandb()


def upload_wandb(args):
    print("Evaluating model " + args.model_name + " version " + str(args.model_version))
    model = keras.models.load_model(args.model_name + "/" + str(args.model_version))

    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
        args.test_set,
        validation_split=0.2,
        subset="validation",
        seed=2412,
        image_size=(IMAGE_HEIGHT, IMAGE_WIDTH),
        batch_size=BATCH_SIZE,
    )

    wan_all_table = wandb.Table(
        columns=["id", "image", "image_path", "label", "prediction"]
    )

    total = 0
    class_names = test_ds.class_names
    file_paths = test_ds.file_paths

    for images, labels in test_ds:
        predictions = np.argmax(model.predict(images), axis=-1)
        for i in range(len(images)):
            label = class_names[labels[i]]
            predict = class_names[predictions[i]]
            path = file_paths[total]
            wan_all_table.add_data(total, wandb.Image(images[i]), path, label, predict)
            total += 1
            print("Total: ", total)

    print("Done prediction, now uploading to wandb...")
    # Log your Table to W&B
    wandb.log(
        {
            "Predictions model "
            + args.model_name
            + " version "
            + str(args.model_version): wan_all_table
        }
    )
    print("Done uploading to wandb...")


def clean(args):
    print("Cleaning...")
    util.finish_wandb()
    shutil.rmtree(args.model_name)
    shutil.rmtree(args.test_set)
    print("Done cleaning")


if __name__ == "__main__":
    args = get_args()
    init(args)
    upload_wandb(args)
    clean(args)
