import tensorflow as tf
import numpy as np

import click
import gin
import time

from dataset import PositionDatabase


class PositionEncoder(tf.keras.Model):
    def __init__(self, input_dim, bottleneck, encoder_hidden, decoder_hidden=None, **kwargs):

        super().__init__(**kwargs)

        self.input_dim = input_dim
        self.bottleneck = bottleneck
        self.encoder_layers = []
        self.decoder_layers = []

        self.autoencoder = True

        if decoder_hidden is None:
            decoder_hidden = encoder_hidden[::-1] # same layer counts as encoder, but in reverse

        self.encoder_layers.append(tf.keras.layers.Input(self.input_dim))
        for hidden_dim in encoder_hidden:
            self.encoder_layers.append(tf.keras.layers.Dense(hidden_dim, activation="relu"))
        self.encoder_layers.append(tf.keras.layers.Dense(self.bottleneck))

        self._encoder = tf.keras.Sequential(layers=self.encoder_layers)

        self.decoder_layers.append(tf.keras.layers.Input(self.bottleneck))
        for hidden_dim in decoder_hidden:
            self.decoder_layers.append(tf.keras.layers.Dense(hidden_dim, activation="relu"))
        self.decoder_layers.append(tf.keras.layers.Dense(self.input_dim))

        self._decoder = tf.keras.Sequential(layers=self.decoder_layers)

    def __call__(self, position):
        z = self._encoder(position)
        if self.autoencoder:
            return self._decoder(z)
        return z

@gin.configurable()
def train_encoder(
    dataset,
    raw_dimension, 
    bottleneck_dimension,
    train_iters,
    batch_size,
    learning_rate
):

    encoder = PositionEncoder(input_dim=raw_dimension, bottleneck=bottleneck_dimension, encoder_hidden=[256, 128])

    optimizer = tf.keras.optimizers.Adam(learning_rate)

    # dataset = dataset.batch(batch_size)

    for b in range(train_iters):
        batch = []
        for i in range(batch_size):
            batch.append(dataset.next())
        pos, evl = zip(*batch)

        pos = tf.stack(pos)
        evl = tf.stack(evl)

        with tf.GradientTape() as tape:
            pos_reconstructed = encoder(pos)

            loss = tf.nn.compute_average_loss(
                tf.losses.mse(pos_reconstructed, pos)
            )

        grads = tape.gradient(loss, encoder.trainable_variables)
        optimizer.apply_gradients(zip(grads, encoder.trainable_variables))

        if b % 100 == 0:
            print(f"Loss at iteration {b}: {loss.numpy()}")

@click.command()
@click.option(
    "--data_file",
    type=click.Path(exists=True, file_okay=True),
    nargs=1,
    required=True,
    help="Path of the CSV containing the position and evaluation data.",
)
@click.option(
    "--config",
    type=click.Path(exists=True, file_okay=True),
    nargs=1,
    required=True,
    help="Path of the config file to use for training.",
)
@click.option(
    "--pos_array_format",
    type=click.STRING,
    nargs=1,
    required=False,
    default="zun",
    help="String specifying options for position array (see dataset.PositionDatabase.position_array() for details).",
)
def main(data_file, config, pos_array_format):

    gin.parse_config_file(config)
    gin.finalize()

    tf.config.run_functions_eagerly(True)
    tf.data.experimental.enable_debug_mode()

    expert_data = PositionDatabase(data_file, pos_array_format)

    example_position = expert_data.position_array("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    # print("Starting tensor conversion...")
    # start_time = time.time()
    # for i in range(1000):
    #     data_point = expert_data()
    # end_time = time.time()
    # print(f"Finished tensor conversion, time taken = {end_time-start_time}")

    raw_dimension = example_position.shape[-1]

    # dataset = tf.data.Dataset.from_generator(
    #     expert_data,
    #     output_signature=(
    #         tf.TensorSpec(shape=(raw_dimension), dtype=tf.float32),
    #         tf.TensorSpec(shape=(), dtype=tf.float32)
    #     )
    # )

    train_encoder(expert_data, raw_dimension)


if __name__ == "__main__":
    main()