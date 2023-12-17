import tensorflow as tf


def create_efficientnet_model(learning_rate, img_height, img_width):
    from tensorflow.keras.applications import EfficientNetB3

    efficient_net = EfficientNetB3(
        weights="imagenet",
        include_top=False,
        input_shape=(img_height, img_width, 3),
        pooling="max",
    )

    NUMBER_OF_CLASSES = 2
    model = tf.keras.models.Sequential(
        [
            tf.keras.layers.InputLayer(input_shape=[img_height, img_width, 3]),
            efficient_net,
            tf.keras.layers.Dropout(rate=0.2, name="drop_out"),
            tf.keras.layers.Dense(
                NUMBER_OF_CLASSES, activation="softmax", name="fc_out"
            ),
        ]
    )

    opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=opt,
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=["accuracy"],
    )

    return model
