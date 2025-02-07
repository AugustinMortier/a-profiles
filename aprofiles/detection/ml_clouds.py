# @author Augustin Mortier
# @desc A-Profiles - Clouds detection using trained Machine Learning algorithm (Deep Embedded Clustering)

import os
import warnings
import absl.logging
from sklearn.exceptions import InconsistentVersionWarning

# Suppress TensorFlow CUDA messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['XLA_FLAGS'] = '--xla_gpu_cuda_data_dir='  # Prevents unnecessary CUDA checks
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "false"  # Avoids some GPU-related logs

# Suppress Abseil warnings
absl.logging.set_verbosity(absl.logging.ERROR)

# Suppress scikit-learn version warnings
warnings.simplefilter("ignore", InconsistentVersionWarning)

# Suppress TensorFlow progress bar
import tensorflow as tf
tf.keras.utils.disable_interactive_logging()

import numpy as np
from tensorflow.keras.models import load_model
from skimage.transform import resize
from pathlib import Path
import joblib


def detect_clouds(profiles, time_avg=1., verbose=False):
    """Module for *clouds detection*.
    The detection is performed using AI-Profiles (See: https://github.com/AugustinMortier/ai-profiles), 
    a pre-trained ML model using Deep Embedded Clustering.

    Args:
        profiles (aprofiles.profiles.ProfilesData): `ProfilesData` instance.
        time_avg (float, optional): in minutes, the time during which we aggregates the profiles prior to the clouds detection.
        verbose (bool, optional): verbose mode. Defaults to `False`.

    Returns:
        (aprofiles.profiles.ProfilesData): 
            adds the following (xarray.DataArray) to existing (aprofiles.profiles.ProfilesData):

            - `'is_cloud' (time, altitude)`: Mask array.

    Example:
        ```python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # clouds detection
        profiles.ml_clouds()
        # attenuated backscatter image with clouds
        profiles.plot(show_ml_clouds=True, vmin=1e-2, vmax=1e1, log=True)
        ```

        ![Clouds detection](../../assets/images/ml_clouds.png)
    """
    
    # ML parameters
    ML = {
        'paths': {
            'encoder': Path(Path(__file__).parent,'ml_models','encoder.keras'),
            'kmeans': Path(Path(__file__).parent,'ml_models','kmeans.pkl')    
        },
        'params': {
            'vmin': -2,
            'vmax': 2,
            'target_size': (256, 512)    
        }
    }

    def _prepare_data(data, vmin, vmax, target_size):
        # Log transform
        #data = np.log(data)

        # Clip data to the range [vmin, vmax] and then scale it
        data_clipped = np.clip(data, vmin, vmax)

        # Replace NaNs with minimum values
        np.nan_to_num(data_clipped, copy=False, nan=vmin)

        # Invert the normalized data to reflect the 'gray_r' colormap
        data_normalized = (data_clipped - vmin) / (vmax - vmin)
        data_inverted = 1 - data_normalized  # Invert the grayscale values
        
        # Resize the inverted data to the target size
        resized_data = resize(
            data_inverted,
            output_shape=target_size,
            order=0,  # Nearest-neighbor interpolation to avoid smoothing
            anti_aliasing=False
        )
        return resized_data
    
    
    def _ml_clouds(prepared_data, encoder, cluster, target_size, output_shape):
        # Add batch and channel dimensions for further processing
        data_array = np.expand_dims(np.expand_dims(prepared_data, axis=0), axis=-1)

        # Encode the image to get feature representation
        encoded_img = encoder.predict(data_array)[0]  # Remove batch dimension

        # Step 1: Aggregate Encoded Features
        aggregated_encoded_img = np.mean(encoded_img, axis=-1)  # Aggregated to single-channel (16, 32)

        # Optional: Normalize for better visualization
        aggregated_encoded_img = (aggregated_encoded_img - aggregated_encoded_img.min()) / (aggregated_encoded_img.max() - aggregated_encoded_img.min())

        # Step 2: Flatten Encoded Features and Cluster
        encoded_img_flat = encoded_img.reshape(-1, encoded_img.shape[-1])  # Flatten spatial dimensions for clustering
        pixel_labels = cluster.predict(encoded_img_flat)  # Get cluster labels for each pixel

        # Step 3: Map clusters to categories
        category_mapping = {
            1: False,  # molecules
            3: False,  # molecules
            5: False,  # noise
            4: False,  # aerosols
            2: True,  # clouds
            6: True,  # clouds
            0: False,  # other
            7: False   # other
        }
        pixel_labels = np.vectorize(category_mapping.get)(pixel_labels)

        # Reshape the cluster labels back to the spatial dimensions
        pixel_labels_image_shape = pixel_labels.reshape(encoded_img.shape[0], encoded_img.shape[1])

        # Step 4: Upsample the cluster labels to match the original image size
        upsampled_pixel_labels = resize(
            pixel_labels_image_shape,
            (target_size[0], target_size[1]),
            order=0,  # Nearest-neighbor interpolation
            preserve_range=True,
            anti_aliasing=False
        )
        #upsampled_pixel_labels = upsampled_pixel_labels.astype(int)  # Ensure the labels are integers
        
        # resize upsampled_pixel_labels to original size
        resized_upsampled_pixel_labels = resize(
                upsampled_pixel_labels,
                output_shape=output_shape,
                order=0,  # Nearest-neighbor interpolation to avoid smoothing
                anti_aliasing=False
            )
        
        return resized_upsampled_pixel_labels
    
    def _split_matrix(matrix, max_size):
        return [matrix[i:i+max_size] for i in range(0, matrix.shape[0], max_size)]

    def _combine_matrices(matrices):
        return np.vstack(matrices)
    
    # we work on profiles averaged in time to reduce the noise
    rcs = profiles.time_avg(
        time_avg, var="attenuated_backscatter_0"
    ).data.attenuated_backscatter_0
    
    split_rcs_list = _split_matrix(rcs, 100)
    
    # Load the encoder and kmeans model
    encoder = load_model(ML['paths']['encoder'])
    cluster = joblib.load(ML['paths']['kmeans'])
    
    # prepare data
    split_ml_clouds = []
    for split_rcs in split_rcs_list:
        prepared_data = _prepare_data(split_rcs, ML['params']['vmin'], ML['params']['vmax'], ML['params']['target_size'])
        split_ml_clouds.append(_ml_clouds(prepared_data, encoder, cluster, ML['params']['target_size'], output_shape=np.shape(split_rcs)))
    
    # aggregate split_ml_clouds
    ml_clouds = _combine_matrices(split_ml_clouds)
    
    # creates dataarrays
    profiles.data["ml_clouds"] = (("time", "altitude"), ml_clouds)
    profiles.data["ml_clouds"] = profiles.data.ml_clouds.assign_attrs({
        'long_name': 'Mask - ML clouds',
        'units': 'bool',
        'time_avg': time_avg
    })
    
    return profiles


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    # profiles.desaturate_below(z=4000., inplace=True)

    # detection
    profiles.ml_clouds(time_avg=1, verbose=True)
    print(profiles.data['ml_clouds'])
    profiles.plot(var='ml_clouds', cmap='Greys')
    #profiles.plot(show_clouds=True, log=True, vmin=1e-2, vmax=1e1)
    # plot single profile
    #datetime = np.datetime64("2021-09-09T14:00:00")
    #profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True)


if __name__ == "__main__":
    _main()
