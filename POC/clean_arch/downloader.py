from google.cloud import storage
import os


def download_folder(
    bucket_name="mek_models",
    folder_name="LivenessDetection/anti_spoof_models",
    destination_dir="./resources/anti_spoof_models",
):
    client = storage.Client.from_service_account_json("key.json")

    # Get bucket and list of blobs in the folder
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name)

    # Create destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Download each blob to the destination directory
    for blob in blobs:
        blob_path = blob.name
        file_name = os.path.basename(blob_path)
        destination_path = os.path.join(destination_dir, file_name)
        blob.download_to_filename(destination_path)
        print(f"Downloaded {blob_path} to {destination_path}")
    print("Download completed.")


if __name__ == "__main__":
    download_folder(
        # folder_name="LivenessDetection/detection_model/",
        # destination_dir="./resources/detection_model",
    )
