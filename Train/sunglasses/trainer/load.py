import tensorflow as tf
from . import util


def load_data(args):

    util.check_and_download(args.bucket_name, args.dataset_name)

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        args.dataset_name,
        validation_split=args.validation_ratio,
        subset="training",
        seed=2412,
        image_size=(args.image_height, args.image_width),
        batch_size=args.batch_size,
    )

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        args.dataset_name,
        validation_split=args.validation_ratio,
        subset="validation",
        seed=2412,
        image_size=(args.image_height, args.image_width),
        batch_size=args.batch_size,
    )

    # Prefetch for performance and shuffle
    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # Get the same val_ds as test_ds
    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
        args.dataset_name,
        validation_split=args.validation_ratio,
        subset="validation",
        seed=2412,
        image_size=(args.image_height, args.image_width),
        batch_size=args.batch_size,
    )

    return train_ds, val_ds, test_ds
