import tensorflow as tf
import numpy as np
import time

from preprocessing import compute_all_features, load_all_features
from model_training import train_autoencoder, normalize_mfccs, train_autoencoder_conv
from visualization import visualize_encoded_data, visualize_melspectrogram, visualize_audio_length


def main():
    start_time = time.time()
    # Main-Directory of datasets. Structure needs to be: main_directory\fan\train for the train dataset of the
    # subset fan.
    audio_all = r'C:\Users\HABELS.COMPUTACENTER\Downloads\dcase_training_data'
    datasets = ['bearing', 'fan', 'gearbox', 'slider', 'ToyCar', 'ToyTrain', 'valve']
    # datasets = ['ToyCar', 'ToyTrain']
    subsets = ['train', 'test']

    feature_options = ["mfcc", "mel", "stft"]

    output_size = (128, 313)
    feature = feature_options[1]
    # compute_all_features(audio_all, feature_type=feature, augment=False, num_augmentations=5,
                   #     augmentation_factor=0.02, output_size=output_size)

    # Load the features data from the JSON file
    data_train, data_test = load_all_features(feature_type=feature, subsets=subsets,
                                              datasets=datasets, output_size=output_size)

    print(data_train.dtype)
    print(np.shape(data_train))
    print(data_test.dtype)
    print(np.shape(data_test))
    # autoencoder = tf.keras.models.load_model('autoencoder_model.h5')

    # Normalize the data
    normalized_train_data = normalize_mfccs(data_train)
    normalized_test_data = normalize_mfccs(data_test)

    # Train the autoencoder
    encoding_dim = 128
    autoencoder = train_autoencoder_conv(normalized_train_data, encoding_dim, epochs=10,
                                                            batch_size=16, l2_reg=0.00, dropout_rate=0.4)

    # Obtain the encoded representation of the input data
    print(np.shape(normalized_train_data))
    print(np.shape(normalized_test_data))
    encoded_train_data = autoencoder.predict(normalized_train_data)
    encoded_test_data = autoencoder.predict(normalized_test_data)

    # Calculate reconstruction errors for the encoded data
    train_reconstruction_errors = np.mean(np.square(normalized_train_data - encoded_train_data), axis=(1, 2))
    test_reconstruction_errors = np.mean(np.square(normalized_test_data - encoded_test_data), axis=(1, 2))

    print(train_reconstruction_errors)
    print(test_reconstruction_errors)

    # Classify anomalies/non-anomalies based on reconstruction errors
    threshold = 1.5  # Set your desired threshold value
    train_predictions = train_reconstruction_errors > threshold
    test_predictions = test_reconstruction_errors > threshold

    # Visualizations
    visualize_encoded_data(encoded_train_data, encoded_test_data, train_predictions, test_predictions)
    # visualize_melspectrogram(data_train[0])
    # visualize_audio_length(audio_all)

    # Save the model
    # autoencoder.save('autoencoder_model.h5')

    compilation_time = time.time() - start_time
    print(f"Compilation time: {compilation_time} seconds")


# Define a custom callback for logging
class LoggingCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"Epoch {epoch + 1}/{self.params['epochs']} - loss: {logs['loss']}")


if __name__ == '__main__':
    main()
