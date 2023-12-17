import argparse
import requests
import pandas as pd
import wandb
import util
import logging
import json

_photos_col = 0
_token = ""

headers = {
    'Authorization': 'Token EHxBDCcKi2GgnlUQRP5JDlVoBxH2zbBb',
}
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval-date-start",
        type=str,
        required=True,
        help="Date to be evaluated and uploaded",
    )

    parser.add_argument(
        "--eval-date-end",
        type=str,
        required=True,
        help="Date to be evaluated and uploaded",
    )

    args, _ = parser.parse_known_args()

    return args


def init():
    global _photos_col
    _photos_col = util.init_mongo()
    global _token
    with open(".token", "r") as f:
        _token = f.read()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    util.init_wandb()


def upload_wandb():
    logging.info(
        "Starting evaluation of photos"
    )

    photos = _photos_col.find().limit(2000)
    # print(list(urls))
    wan_daily_table = wandb.Table(
        columns=[
            "image",
            "label",
            "prediction",
        ]
    )
    count = 0
    COLUMN_NAMES=["image",
            "label",
            "prediction"]
    df = pd.DataFrame(columns=COLUMN_NAMES)

    for photo in list(photos):
        try:
            payload = {
                'image_url': photo['originUrl'],
            }
            response = requests.post('https://api.thehive.ai/api/v2/task/sync',
                                     headers=headers, data=payload)
            data = response.json()
            classes = data['status'][0]['response']['output'][0]['classes']
            pred_list = []
            for item in classes:
                if (item['score'] >= 0.8 and "no" not in item['class']):
                    pred_list.append(item)
            # print(json.dumps(label_list))
            pred_list = json.dumps(pred_list)
            img = util.get_image_from_url(photo['originUrl'])
            if photo["status"] == "accepted_crop_done":
                label = "ACCEPTED"
            else:
                label = "REFUSED"
            wan_daily_table.add_data(
                        wandb.Image(img),
                        label,
                        pred_list,
            )
            df.append({
                'image': photo['originUrl'],
                'label': label,
                'prediction': pred_list
            }, ignore_index=True)
            logging.info(
                "Number %s url %s label %s prediction %s",
                count,
                photo['originUrl'],
                label,
                pred_list,
            )
            count += 1
        except Exception as e:
            print(e)
            logging.error("Error getting prediction, continue,...")
            pass


    #
    df.to_csv("./eval_hive.csv")
    logging.info(
        "Done prediction 1000 photos, now uploading to wandb...",
    )
    # # Log your Table to W&B
    wandb.log(
        {
            "Photo classification 1000": wan_daily_table
        }
    )
    logging.info("Done uploading to wandb...")


def clean():
    logging.info("Cleaning, finish wandb...")
    util.finish_wandb()
    logging.info("Done cleaning, exiting...")


if __name__ == "__main__":
    # args = get_args()
    init()
    upload_wandb()
    clean()
