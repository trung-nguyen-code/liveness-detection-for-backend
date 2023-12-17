"""Download models from GCS."""

import os
from google.cloud import storage
import argparse


def download(gs_cred_path, model_name, model_version, models_path):
    """Download model_name with version to location_model"""
    gs_client = storage.Client.from_service_account_json(gs_cred_path)

    path = "Recommendation/" + model_name + "/" + model_version

    model_bucket = gs_client.get_bucket("mek_models")
    blobs = list(model_bucket.list_blobs(prefix=path))

    # create local folder model_name/model_version
    if not os.path.exists(models_path):
        os.mkdir(models_path)
    if not os.path.exists(models_path + model_name):
        os.mkdir(models_path + model_name)
    if not os.path.exists("models/" + model_name + "/" + model_version):
        os.mkdir(models_path + model_name + "/" + model_version)

    # copy the model folders to local model_name/model_version
    print("Start downloading model...")
    new_path = "models/" + model_name + "/" + model_version
    for blob in blobs:
        if not blob.name.endswith("/"):
            file = blob.name.split(path)[1]
            merge_path = new_path + file
            new_merge_path = os.path.dirname(merge_path)
            if not os.path.exists(new_merge_path):
                os.mkdir(new_merge_path)
            blob.download_to_filename(merge_path)

    print("Downloaded model to : ", new_path)


def get_args():
    """Define the task arguments with the default values.
    Returns:
        experiment parameters
    """
    parser = argparse.ArgumentParser(description="PyTorch Resnet152")
    parser.add_argument(
        "--credential-path", type=str, help="Where to have credential path"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="retrieval",
        help="What to name the saved model file",
    )
    parser.add_argument(
        "--model-version",
        type=str,
        default="retrieval",
        help="Which version for the saved model file",
    )

    args = parser.parse_args()

    return args


def main():
    """Setup / Start the experiment"""
    args = get_args()
    print("args", args)
    download(
        args.credential_path,
        args.model_name,
        args.model_version,
        "./models/",
    )


if __name__ == "__main__":
    main()
