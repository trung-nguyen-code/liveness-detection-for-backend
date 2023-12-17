import os
import urllib.request
from google.cloud import storage
from pymongo import MongoClient
from decouple import config
from urllib.parse import urlparse

MONGO_URI = config("MONGO_MAIN_URI")
MONGO_DB_NAME = config("MONGO_MAIN_DB")
MONGO_PHOTOS_COLLECTION_NAME = config("MONGO_COLLECTION")

PHOTO_LIMIT = int(config("PHOTO_LIMIT"))
DEST_BUCKET = config("GS_BUCKET")
ACCEPT_PATH = config("ACCEPT_PATH")
REFUSE_PATH = config("REFUSE_PATH")


def copy_type(col, status, limit, bucket, gs_path):
    photos = col.find({"status": status}, sort=[("createdAt", -1)]).limit(limit)
    for photo in photos:
        url = photo["originUrl"]
        filename = os.path.basename(urlparse(url).path)

        filepath = "tmp/" + filename
        # save photo to tmp dir
        urllib.request.urlretrieve(url, filepath)

        bucket_path = gs_path + filename
        blob = bucket.blob(bucket_path)
        # upload photo to cloud storage
        blob.upload_from_filename(filepath)
        # remove photo from temp dir
        os.remove(filepath)


def copy_mek_to_gs():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB_NAME]
    photos_col = db[MONGO_PHOTOS_COLLECTION_NAME]

    gs_client = storage.Client.from_service_account_json("certs/mek_gs.json")

    gs_bucket = gs_client.get_bucket(DEST_BUCKET)

    # copy photos from Mek server to google storage
    copy_type(photos_col, "accepted_crop_done", PHOTO_LIMIT, gs_bucket, ACCEPT_PATH)
    copy_type(photos_col, "refused", PHOTO_LIMIT, gs_bucket, REFUSE_PATH)


if __name__ == "__main__":
    copy_mek_to_gs()
