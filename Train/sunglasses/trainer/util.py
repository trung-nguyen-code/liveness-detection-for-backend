import os
from google.cloud import storage
import zipfile
import csv

gs_client = 0


def init():
    global gs_client
    gs_client = storage.Client.from_service_account_json("mek_gs.json")


def download_unzip(dataset_bucket, dataset_name):
    global gs_client
    mek_datasets_bucket = gs_client.get_bucket(dataset_bucket)
    blob = mek_datasets_bucket.blob("{}.zip".format(dataset_name))
    blob.download_to_filename(dataset_name + ".zip")
    # unzip
    with zipfile.ZipFile(dataset_name + ".zip", "r") as zip_ref:
        zip_ref.extractall(".")


def check_and_download(dataset_bucket, dataset_name):
    # check if folder exists
    if not os.path.isdir(dataset_name):
        # if not exist then download and unpack
        download_unzip(dataset_bucket, dataset_name)


def append_to_gs(bucket, filename, line):
    global gs_client
    bucket = gs_client.get_bucket(bucket)
    blob = bucket.blob(filename)
    tmp = "tmp.csv"
    blob.download_to_filename(tmp)
    with open(tmp, "a") as meta:
        writer = csv.writer(meta)
        writer.writerow(line)

    blob = bucket.blob(filename)
    blob.upload_from_filename(tmp)
    os.remove(tmp)


def test_download():
    check_and_download("mek_datasets", "FACES_CLASSIFIED_224")


def test_meta():
    line = [
        "1",
        "sunglasses",
        str(1),
        "test",
        "classifier",
        "test",
        "test",
        str(0.9),
        str(0.9),
        str(0.5),
    ]

    append_to_gs("mek_models", "STAGING/models.csv", line)


if __name__ == "__main__":
    init()
    test_meta()
