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

import argparse

import experiment


def get_args():
    """Define the task arguments with the default values.
    Returns:
        experiment parameters
    """
    parser = argparse.ArgumentParser(description="PyTorch Resnet152")
    parser.add_argument("--job-dir", type=str, help="Where to save the model")
    parser.add_argument(
        "--model-name",
        type=str,
        default="nudenonude_classifier",
        help="What to name the saved model file",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="nude_nonude_v2",
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
        "--epochs", type=int, default=200, help="number of epochs to train (default: 30)"
    )
    parser.add_argument(
        "--version", type=str, default="1", help="version of model"
    )
    parser.add_argument(
        "--lr", type=float, default=0.001, help="learning rate (default: 0.01)"
    )
    parser.add_argument(
        "--env", type=str, default="STAGING", help="random seed (default: STAGING)"
    )
    parser.add_argument(
        "--momentum", type=float, default=0.9, help="momentum (default: 0.9)"
    )
    args = parser.parse_args()

    return args


def main():
    """Setup / Start the experiment"""
    args = get_args()
    experiment.run(args)


if __name__ == "__main__":
    main()
