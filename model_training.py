import tensorflow as tf
import numpy as np
from keras.layers import Dense, Dropout, Conv1D, \
    Conv2D, MaxPooling1D, MaxPooling2D, Input, UpSampling1D, UpSampling2D, Reshape
from keras.regularizers import l2
from sklearn.utils import shuffle


def normalize_features(features_data):

    if features_data.shape[1] == 1:
        features_data = np.squeeze(features_data, axis=1)

    # Calculate the mean and standard deviation along the axis of each feature
    mean = np.mean(features_data, axis=(0, 2), keepdims=True)
    std = np.std(features_data, axis=(0, 2), keepdims=True)

    # Perform the normalization
    normalized_data = (features_data - mean) / std

    print(np.shape(normalized_data))
    return normalized_data


def shuffle_data_and_labels(data, labels=None, random_state=None):
    if labels is not None:
        shuffled_data, shuffled_labels = shuffle(data, labels, random_state=random_state)
        return shuffled_data, shuffled_labels
    else:
        shuffled_data = shuffle(data, random_state=random_state)
        return shuffled_data


def train_autoencoder(data, encoding_dim, epochs, batch_size, dropout_rate=0.0, l2_reg=0.00):
    input_data = Input(shape=(data.shape[1], data.shape[2]))

    # Encoder
    encoded = Dense(data.shape[2], activation='relu', kernel_regularizer=tf.keras.regularizers.l2(l2_reg))(input_data)

    encoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)
    encoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)
    encoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)
    encoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)
    encoded = Dense(encoding_dim, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)

    # Dropout layer
    encoded = Dropout(dropout_rate)(encoded)

    # Decoder
    decoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(encoded)
    decoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(decoded)
    decoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(decoded)
    decoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(decoded)
    decoded = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg))(decoded)

    decoded = Dense(data.shape[2], activation='sigmoid', kernel_regularizer=l2(l2_reg))(decoded)

    # Define the autoencoder model
    autoencoder = tf.keras.Model(inputs=input_data, outputs=decoded)

    # Compile the autoencoder
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')

    # Train the autoencoder
    for epoch in range(epochs):
        # Print the epoch number
        print(f"Epoch {epoch + 1}/{epochs}")

        # Fit the data to the autoencoder model
        autoencoder.fit(data, data, epochs=1, batch_size=batch_size, verbose=1)

    return autoencoder


def train_autoencoder_conv(data, encoding_dim, epochs, batch_size, dropout_rate=0.0, l2_reg=0.00):
    input_data = Input(shape=(data.shape[1], data.shape[2], 1))

    # Encoder
    encoded = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(input_data)
    encoded = MaxPooling2D(pool_size=(2, 2))(encoded)
    encoded = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(encoded)
    encoded = MaxPooling2D(pool_size=(2, 2))(encoded)
    encoded = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(encoded)
    encoded = MaxPooling2D(pool_size=(2, 2))(encoded)

    # Dropout layer
    encoded = Dropout(dropout_rate)(encoded)

    # Decoder
    decoded = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(encoded)
    decoded = UpSampling2D(size=(2, 2))(decoded)
    decoded = Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(decoded)
    decoded = UpSampling2D(size=(2, 2))(decoded)
    decoded = Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same',
                     kernel_regularizer=l2(l2_reg))(decoded)
    decoded = UpSampling2D(size=(2, 2))(decoded)

    decoded = Conv2D(filters=1, kernel_size=(3, 3), activation='sigmoid', padding='same')(decoded)
    decoded = Reshape(target_shape=(data.shape[1], data.shape[2]))(decoded)

    # Define the autoencoder model
    autoencoder = tf.keras.Model(inputs=input_data, outputs=decoded)

    # Compile the autoencoder
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')

    # Train the autoencoder
    autoencoder.fit(data, data, epochs=epochs, batch_size=batch_size, verbose=1)

    return autoencoder

