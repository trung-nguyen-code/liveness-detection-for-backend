from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os

import datetime

from . import model
from . import util
from . import load

import tensorflow as tf

REQUIRED_ACCURACY = 0.98


def get_args():
    """Argument parser.

    Returns:
      Dictionary of arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--job-dir",
        type=str,
        required=True,
        help="local or GCS location for writing checkpoints",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        required=True,
        help="local or GCS location for exporting models",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="sunglasses",
        help="Name of the model, default=sunglasses",
    )
    parser.add_argument(
        "--model-version", type=int, default=1, help="Name of the model, default=1"
    )
    parser.add_argument(
        "--num-epochs",
        type=int,
        default=20,
        help="number of times to go through the data, default=20",
    )
    parser.add_argument(
        "--batch-size",
        default=64,
        type=int,
        help="number of records to read during each training step, default=64",
    )
    parser.add_argument(
        "--learning-rate",
        default=0.0001,
        type=float,
        help="learning rate for gradient descent, default=.0001",
    )
    parser.add_argument(
        "--image-height", default=224, type=int, help="image height, default=224"
    )
    parser.add_argument(
        "--image-width", default=224, type=int, help="image width, default=224"
    )
    parser.add_argument(
        "--validation-ratio",
        default=0.2,
        type=float,
        help="validation ratio, default=0.2",
    )
    parser.add_argument(
        "--bucket-name",
        type=str,
        default="mek_datasets",
        help="name of the GS bucket for download, default = mek_datasets",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="FACES_CLASSIFIED_224",
        help="name of the dataset ID, default = FACES_CLASSIFIED_224",
    )
    parser.add_argument(
        "--verbosity",
        choices=["DEBUG", "ERROR", "FATAL", "INFO", "WARN"],
        default="ERROR",
    )
    args, _ = parser.parse_known_args()
    return args


def train(args):
    """
    Train the efficientnet v3 models
    defined in model.py

    Args:
      args: dictionary of arguments - see get_args() for details
    """
    # Load datasets

    train_ds, val_ds, test_ds = load.load_data(args)

    # Create model
    eff_model = model.create_efficientnet_model(
        args.learning_rate, args.image_height, args.image_width
    )

    # Setup TensorBoard callback.
    tensorboard_cb = tf.keras.callbacks.TensorBoard(
        os.path.join(args.job_dir, "tensorboard"), histogram_freq=1
    )

    # Check point for max accuracy
    best_acc_checkpoint = "tmp/checkpoint"
    model_checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
        filepath=best_acc_checkpoint,
        save_weights_only=True,
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
    )

    # Train model
    eff_model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.num_epochs,
        callbacks=[tensorboard_cb, model_checkpoint_cb],
    )

    # Get the best accuracy weights
    eff_model.load_weights(best_acc_checkpoint)

    # Export model
    current_time = str(datetime.datetime.now())
    model_path = (
        args.model_dir
        + "/"
        + args.model_name
        + "/"
        + str(args.model_version)
        + "/"
        + current_time
    )
    eff_model.save(model_path)

    print("Model exported to: {}".format(model_path))

    # Evaluate model

    val_loss, val_acc = eff_model.evaluate(test_ds, batch_size=args.batch_size)

    # Append GS Metafile
    meta = [
        current_time,
        args.model_name,
        str(args.model_version),
        model_path,
        "classifier",
        args.dataset_name,
        args.dataset_name,
        str(val_acc),
        str(val_loss),
        str(REQUIRED_ACCURACY),
    ]

    util.append_to_gs("mek_models", "STAGING/models.csv", meta)


if __name__ == "__main__":
    util.init()
    args = get_args()
    train(args)
