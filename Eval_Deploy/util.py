import os
import zipfile
import wandb
from PIL import Image, UnidentifiedImageError
import requests
import logging
from pymongo import MongoClient
from datetime import datetime
from dateutil.relativedelta import relativedelta

from dotenv import load_dotenv

load_dotenv()

CLASSIFIER_ENDPOINT = "https://ai.mektou.be/classify"
FACE_CLASSIFIER_ENDPOINT = "https://ai.mektou.be/classify_face_with_classifier"
FACE_MASK_CLASSIFIER_ENDPOINT = "https://ai.mektou.be/classify_face_mask"


MONGO_URI = os.environ["MONGO_MAIN_URI"]
MONGO_DB_NAME = os.environ["MONGO_MAIN_DB"]
MONGO_PHOTOS_COLLECTION_NAME = os.environ["MONGO_COLLECTION"]


def get_image_from_url(url):
    """Fetch image from an url.

    :param url: url address of the image
    :return : PIL image of the url
    """
    try:
        img = Image.open(requests.get(url, stream=True).raw)
    except UnidentifiedImageError as e:
        logging.error("URL invalid %s", url)
        raise UnidentifiedImageError(
            "Unable to decode image from the url %s %s", url, e
        )
    return img


def download(gs_client, model_name, model_version, model_path, test_set):

    # download test set
    print("Start downloading test set...")
    mek_datasets_bucket = gs_client.get_bucket("mek_datasets")
    blob = mek_datasets_bucket.blob("{}.zip".format(test_set))
    blob.download_to_filename(test_set + ".zip")

    with zipfile.ZipFile(test_set + ".zip", "r") as zip_ref:
        zip_ref.extractall(".")
    os.remove(test_set + ".zip")
    print("Downloaded test set to : ", test_set)

    # download model
    # tensorflow saved model contains some folder so a little complicated
    model_bucket = gs_client.get_bucket("mek_models")
    path = model_path.split("gs://mek_models/")[1]
    blobs = list(model_bucket.list_blobs(prefix=path))

    # create local folder model_name/model_version
    if not os.path.exists(model_name):
        os.mkdir(model_name)
    if not os.path.exists(model_name + "/" + model_version):
        os.mkdir(model_name + "/" + model_version)

    # copy the model folders to local model_name/model_version
    print("Start downloading model...")
    new_path = model_name + "/" + model_version
    for blob in blobs:
        if not blob.name.endswith("/"):
            file = blob.name.split(path)[1]
            merge_path = new_path + file
            new_merge_path = os.path.dirname(merge_path)
            if not os.path.exists(new_merge_path):
                os.mkdir(new_merge_path)
            blob.download_to_filename(merge_path)

    print("Downloaded model to : ", new_path)
    return new_path, test_set


def test_download():
    download(
        "sunglasses",
        "1",
        "gs://mek_models/STAGING/sunglasses/1/2021-08-27 15:50:29.128994",
        "FACES_CLASSIFIED_224",
    )


def init_wandb():
    os.environ["WANDB_API_KEY"] = "cd20efb68bd680d685d5db7470891abd2d748522"
    wandb.init(project="sunglasses", entity="techiz_data")


def finish_wandb():
    wandb.finish()


def get_urls_list(mongo_col, eval_date_start, eval_date_end):
    start_time = datetime.strptime(eval_date_start, "%Y-%m-%d")

    end_time = datetime.strptime(eval_date_end, "%Y-%m-%d") + relativedelta(
        days=1, microseconds=-1
    )
    photos = mongo_col.find({"createdAt": {"$gte": start_time, "$lt": end_time}})
    urls = []
    for photo in photos:
        url = photo["originUrl"]

        if photo["status"] == "accepted_crop_done":
            label = "ACCEPTED"
        else:
            label = "REFUSED"
        date_created = photo["createdAt"].strftime("%Y-%m-%d")
        urls.append((url, label, date_created))
    return urls


def get_prediction(token, url):
    params = {"url": url}
    headers = {"Authorization": "Bearer " + token}
    json_res = requests.get(CLASSIFIER_ENDPOINT, params=params, headers=headers).json()
    prediction = json_res["predict"]
    prob = json_res["probability"]
    return prediction, prob


def get_prediction_face(token, url):
    params = {"url": url}
    headers = {"Authorization": "Bearer " + token}
    json_res = requests.get(
        FACE_CLASSIFIER_ENDPOINT, params=params, headers=headers
    ).json()
    prediction = json_res["predict"]
    prob = json_res["probability"]
    return prediction, prob


def get_prediction_face_mask(token, url):
    params = {"url": url}
    headers = {"Authorization": "Bearer " + token}
    json_res = requests.get(
        FACE_MASK_CLASSIFIER_ENDPOINT, params=params, headers=headers
    ).json()
    prediction = json_res["predict"]
    prob = json_res["probability"]
    return prediction, prob


def init_mongo():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB_NAME]
    photos_col = db[MONGO_PHOTOS_COLLECTION_NAME]
    return photos_col
