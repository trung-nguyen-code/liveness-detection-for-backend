import argparse

import wandb
import util
import logging

LABELS = ["ACCEPTED", "NOFACE", "SUNGLASSES", "MULTI_FACES", "FACE_MASK", "NUDE"]
_photos_col = 0
_token = ""


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


def upload_wandb(eval_date_start, eval_date_end):
    logging.info(
        "Starting evaluation of photos from date: %s to date %s",
        eval_date_start,
        eval_date_end,
    )

    urls = util.get_urls_list(_photos_col, eval_date_start, eval_date_end)

    wan_daily_table = wandb.Table(
        columns=[
            "date",
            "image",
            "label",
            "prediction",
            "probability",
        ]
    )

    count = 0
    for url in urls:
        try:
            link = url[0]
            img = util.get_image_from_url(link)
            label = url[1]
            # change prediction API to evaluate
            prediction, prob = util.get_prediction(_token, link)

            prob = float("{:.4f}".format(float(prob)))

            prediction_cls = LABELS[int(prediction)]

            logging.info(
                "Number %s url %s label %s prediction %s probability %s",
                count,
                link,
                label,
                prediction_cls,
                prob,
            )
            wan_daily_table.add_data(
                url[2],
                wandb.Image(img),
                label,
                prediction_cls,
                prob,
            )
            count += 1
        except Exception:
            logging.error("Error getting prediction, continue,...")
            pass

    logging.info(
        "Done prediction from date %s to %s, now uploading to wandb...",
        eval_date_start,
        eval_date_end,
    )
    # Log your Table to W&B
    wandb.log(
        {
            "Photo classification from date "
            + str(eval_date_start)
            + " to "
            + str(eval_date_end): wan_daily_table
        }
    )
    logging.info("Done uploading to wandb...")


def clean():
    logging.info("Cleaning, finish wandb...")
    util.finish_wandb()
    logging.info("Done cleaning, exiting...")


if __name__ == "__main__":
    args = get_args()
    init()
    upload_wandb(args.eval_date_start, args.eval_date_end)
    clean()
