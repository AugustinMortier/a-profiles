# @author Augustin Mortier
# @desc A-Profiles - Clouds detection

from rich.progress import track
from typing import Literal

import aprofiles.profiles
from aprofiles import utils


def detect_clouds(profiles: aprofiles.profiles.ProfilesData, method: Literal["dec", "vg"]="dec", time_avg: float=1., zmin: float=0., thr_noise: float=5., thr_clouds: float=4., min_snr: float=0., verbose: bool=False):
    """Module for *clouds detection*.
    Two methods are available: 
    - "dec" (default): Deep Embedded Clustering (see [AI-Profiles](https://github.com/AugustinMortier/ai-profiles)).
    - "vg": Vertical Gradient.

    Args:
        profiles (aprofiles.profiles.ProfilesData): `ProfilesData` instance.
        method (Literal["dec", "vg"]): cloud detection method used.
        time_avg (float, optional): in minutes, the time during which we aggregates the profiles prior to the clouds detection.
        zmin (float, optional): altitude AGL, in m, above which we look for clouds. We recommend using the same value as used in the extrapolation_low_layers method (only for 'vg' method).
        thr_noise (float, optional): threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] data[base(z)] >= thr_noise * noise(z) (only for 'vg' method).
        thr_clouds (float, optional): threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds (only for 'vg' method).
        min_snr (float, optional): Minimum SNR required at the clouds peak value to consider the cloud as valid (only for 'vg' method).
        verbose (bool, optional): verbose mode. Defaults to `False`.

    Returns:
        (aprofiles.profiles.ProfilesData): 
            adds the following (xarray.DataArray) to existing (aprofiles.profiles.ProfilesData):
            - `'clouds' (time, altitude)`: Mask array corresponding to data flagged as a cloud.

    Example 1:
        ```python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # clouds detection
        profiles.clouds(method="dec")
        # attenuated backscatter image with clouds
        profiles.plot(show_clouds=True, vmin=1e-2, vmax=1e1, log=True)
        ```

        ![Clouds detection](../../assets/images/clouds_dec.png)
    
    Example 2:
        ```python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # clouds detection
        profiles.clouds(method="vg", zmin=300.)
        # attenuated backscatter image with clouds
        profiles.plot(show_clouds=True, vmin=1e-2, vmax=1e1, log=True)
        ```

        ![Clouds detection](../../assets/images/clouds_vg.png)
    """

    def _vg_clouds(data, zmin, thr_noise, thr_clouds, min_snr):
        # data: 1D range corrected signal (rcs)
        # zmin: altitude AGL, in m, above which we detect clouds
        # thr_noise: threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z)
        # thr_clouds: threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds
        # min_snr: minimum SNR required at the clouds peak value to consider the cloud as valid. Defaults to 2.

        from scipy import signal
        from scipy.ndimage.filters import uniform_filter1d

        # some useful functions:
        def _get_all_indexes(bases, peaks, tops=[]):
            # get True indexes of bases, peaks and tops, based on masks
            i_bases = utils.get_true_indexes(bases)
            i_peaks = utils.get_true_indexes(peaks)
            i_tops = utils.get_true_indexes(tops)
            return i_bases, i_peaks, i_tops

        def _make_all_masks(data, i_bases, i_peaks, i_tops=[]):
            # return masks for bases, peaks and tops based on input indexes
            bases = utils.make_mask(len(data), i_bases)
            peaks = utils.make_mask(len(data), i_peaks)
            tops = utils.make_mask(len(data), i_tops)
            return bases, peaks, tops

        def _merge_layers(data, i_bases, i_peaks, i_tops):
            # merge layers depending on the altitude of the bases and the tops
            remove_mode = True
            while remove_mode:
                remove_bases, remove_peaks, remove_tops = [], [], []
                for i in range(len(i_bases) - 1):
                    # filters based on the index
                    if i_bases[i + 1] <= i_tops[i]:
                        remove_bases.append(i_bases[i + 1])
                        # remove the weakest peak
                        imin = np.argmin([data[i_peaks[i]], data[i_peaks[i + 1]]])
                        remove_peaks.append(i_peaks[i + imin])
                        # remove lowest top
                        imin = np.argmin([i_tops[i], i_tops[i + 1]])
                        remove_tops.append(i_tops[i + imin])
                        # start again from the bottom
                        break

                i_bases = [i for i in i_bases if i not in remove_bases]
                i_peaks = [i for i in i_peaks if i not in remove_peaks]
                i_tops = [i for i in i_tops if i not in remove_tops]
                if len(remove_bases) == 0:
                    remove_mode = False

            return i_bases, i_peaks, i_tops

        def _find_tops(data, i_bases, i_peaks):
            # function that finds the top of the layers by identifying the first value above thepeak for which the signal is lower than the base
            # if no top is found, the layer is removed
            # retruns lists of indexes of the bases, peaks and tops
            tops = np.asarray([False for x in np.ones(len(data))])
            # conditions: look for bases above i_peaks[i], and data[top[i]] <= data[base[i]]

            i_tops = []
            for i in range(len(i_bases)):
                mask_value = np.asarray(
                    [
                        True if data[j] < data[i_bases[i]] else False
                        for j in range(len(data))
                    ]
                )
                mask_altitude = np.asarray(
                    [True if j > i_peaks[i] else False for j in range(len(data))]
                )
                # the top is the first value that corresponds to the intersection of the two masks
                cross_mask = np.logical_and(mask_value, mask_altitude)
                i_cross_mask = utils.get_true_indexes(cross_mask)
                if len(i_cross_mask) > 0:
                    if tops[i_cross_mask[0]]:
                        bases[i_bases[i]] = False
                        peaks[i_peaks[i]] = False
                    else:
                        tops[i_cross_mask[0]] = True
                        i_tops.append(i_cross_mask[0])
                else:
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False
            # it is important to keep the tops in the same order, so not to use utils.get_true_indexes() function here
            return utils.get_true_indexes(bases), utils.get_true_indexes(peaks), i_tops

        def _mask_cloud(profile: aprofiles.profiles, bases: list[int], tops: list[int]) -> np.ndarray:
            """Generate a boolean mask for cloud presence in a given profile.

            Args:
                profile (aprofiles.profiles): 1D array representing a single atmospheric profile.
                bases (list[int]): List of base indices where clouds start.
                tops (list[int]): List of top indices where clouds end.

            Returns:
                np.ndarray: Boolean mask of the same length as profile, where cloud regions are True.
            """
            mask = np.zeros_like(profile, dtype=bool)
            
            for base, top in zip(bases, tops):
                mask[base:top] = True
            
            return mask

        #-1. check if any valid data
        if np.isnan(data).all():
            bases, peaks, tops = _make_all_masks(data, [], [], [])
            return {
                "bases": bases,
                "peaks": peaks,
                "tops": tops,
            }

        # 0. rolling average
        avg_data = uniform_filter1d(data, size=10)

        # 1. first derivative
        gradient = np.gradient(avg_data)
        #remove zero values since np.sign(0) = 0
        gradient = [value if value != 0 else 1e-9 for value in gradient]

        # 2. identifies peaks and base by checking the sign changes of the derivative
        sign_changes = np.diff(np.sign(gradient), append=0)
        all_bases = sign_changes == 2
        all_peaks = sign_changes == -2
        # limit to bases above zmin
        imin = profiles._get_index_from_altitude_AGL(zmin)
        all_bases[0:imin] = np.full(imin, False)
        all_peaks[0:imin] = np.full(imin, False)
        # get indexes
        i_bases = utils.get_true_indexes(all_bases)
        i_peaks = utils.get_true_indexes(all_peaks)

        # 3. the signal should start with a base
        if (len(i_bases)>0): #this happens if the whole profile consists of nan
            if i_bases[0] > i_peaks[0] and i_peaks[0] >= 1:
                # set base as the minimum between peak and n gates under
                gates = np.arange(i_peaks[0] - 5, i_peaks[0])
                i_base = gates[np.argmin([data[gates[gates >= 0]]])]
                if i_base >= imin:
                    all_bases[i_base] = True
                else:
                    all_peaks[i_peaks[0]] = False
            # update indexes
            i_bases = utils.get_true_indexes(all_bases)
            i_peaks = utils.get_true_indexes(all_peaks)

        # 4. keeps significant couples (base,peak)
        # a layer can be considered as a proper layer if the difference of signal between the peak and the base is significant (larger than the noise level)
        # noise evaluation (using a high passing frequency filter)
        b, a = signal.butter(1, 0.3, btype="high")
        noise = signal.filtfilt(b, a, data)
        # rolling average of the noise
        avg_abs_noise = uniform_filter1d(abs(noise), size=100)
        # make sure we have as many peaks as bases
        if len(i_peaks) != len(i_bases):
            min_len = min([len(i_peaks), len(i_bases)])
            i_peaks = i_peaks[0:min_len]
            i_bases = i_bases[0:min_len]
        bases, peaks = all_bases, all_peaks
        for i in range(len(i_bases)):
            data_around_peak = avg_data[i_peaks[i]]
            data_around_base = avg_data[i_bases[i]]
            if (
                data_around_peak - data_around_base
                <= thr_noise * avg_abs_noise[i_bases[i]]
            ):
                bases[i_bases[i]] = False
                peaks[i_peaks[i]] = False
        # get indexes
        i_bases = utils.get_true_indexes(bases)
        i_peaks = utils.get_true_indexes(peaks)

        # 5. make sure we finish by a peak: remove last base if necessary
        if len(i_bases) > len(i_peaks):
            bases[i_bases[-1]] = False
            i_bases.pop()

        # 6. find tops of clouds layers
        i_bases, i_peaks, i_tops = _find_tops(avg_data, i_bases, i_peaks)

        # 7. merge layers: for a couple of base and peaks 1,2 if data(b2)>data(p1), then merge layers 1 and 2 by removing p1 and b2
        i_bases, i_peaks, i_tops = _merge_layers(avg_data, i_bases, i_peaks, i_tops)

        # 8. find peaks as maximum between base and top    
        i_peaks = [
            i_bases[i] + np.argmax(data[i_bases[i]: i_tops[i]])
            for i in range(len(i_bases))
        ]
        # reconstruct masks
        bases, peaks, tops = _make_all_masks(data, i_bases, i_peaks, i_tops)

        # 9. distinction between aerosol and clouds
        for i in range(len(i_bases)):
            data_around_peak = avg_data[i_peaks[i]]
            data_around_base = avg_data[i_bases[i]]
            if (
                abs((data_around_peak - data_around_base) / data_around_base)
                <= thr_clouds
            ):
                bases[i_bases[i]] = False
                peaks[i_peaks[i]] = False
                tops[i_tops[i]] = False
        # get indexes
        i_bases, i_peaks, i_tops = _get_all_indexes(bases, peaks, tops)

        """
        #10. set base a closest index
        for i, _ in enumerate(i_peaks):
            mask_value = np.asarray([True if gradient[j]<0 else False for j in range(len(data))])
            mask_altitude = np.asarray([True if j<i_peaks[i] else False for j in range(len(data))])
            #the top is the first value that corresponds to the intersection of the two masks
            cross_mask = np.logical_and(mask_value, mask_altitude)
            i_cross_mask = utils.get_true_indexes(cross_mask)
            i_bases[i] = i_cross_mask[-1]
        """

        # 11. check snr at peak levels
        remove_bases, remove_peaks, remove_tops = [], [], []
        for i in range(len(i_peaks)):
            if utils.snr_at_iz(data, i_peaks[i], step=10) < min_snr:
                remove_bases.append(i_bases[i])
                remove_peaks.append(i_peaks[i])
                remove_tops.append(i_tops[i])
        # remove indexes
        i_bases = [i for i in i_bases if i not in remove_bases]
        i_peaks = [i for i in i_peaks if i not in remove_peaks]
        i_tops = [i for i in i_tops if i not in remove_tops]

        # 11. build cloud mask from indexes
        clouds = _mask_cloud(data, i_bases, i_tops)

        """
        #some plotting
        fig, axs = plt.subplots(1,2,figsize=(10,10))

        ymin, ymax = 000, 15000
        altitude_agl = profiles.data.altitude.data - profiles.data.station_altitude.data

        #signal on the left
        axs[0].plot(data, altitude_agl, 'b', label='rcs')
        axs[0].plot(avg_data, altitude_agl, 'c', label='rcs')
        axs[0].plot(avg_abs_noise,altitude_agl,':b', label='noise level')
        axs[0].plot(avg_abs_noise*thr_noise,altitude_agl,':b', label=f'noise level * {thr_noise}')
        axs[0].plot(data[bases], altitude_agl[bases], '<g', label='bases')
        axs[0].plot(data[peaks], altitude_agl[peaks], '>r', label='peaks')
        axs[0].plot(data[tops], altitude_agl[tops], '^k', label='tops')

        #set axis
        axs[0].set_ylim([ymin, ymax])
        #axs[0].set_xlim([-20000,20000])
        axs[0].legend()

        #derivative on the right
        axs[1].plot(ddata_dz, altitude_agl, 'b', label='first derivative')
        axs[1].plot(ddata_dz[bases], altitude_agl[bases], '<g', label='bases')
        axs[1].plot(ddata_dz[peaks], altitude_agl[peaks], '>r', label='peaks')

        axs[1].set_ylim([ymin, ymax])
        axs[1].legend()
        #set title
        fig.suptitle(t,weight='bold')
        """

        return clouds

    
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

    # imports and check options
    if method == 'dec':
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
        
        # we split the rcs into subsets, so we artificially increase the time resolution of the cloud detection which is degraded by the DEC technique.
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
        clouds = _combine_matrices(split_ml_clouds)
        
        options = {
            'encoder': ML['paths']['encoder'],
            'kmeans': ML['paths']['kmeans']
        }
        
    elif method == 'vg':
        import numpy as np
        if None in (zmin, thr_noise, thr_clouds, min_snr):
            raise ValueError("For method 'vg', zmin, thr_noise, thr_clouds, and min_snr must be provided.")

        clouds = []
        for i in (track(range(len(profiles.data.time.data)), description="clouds",disable=not verbose)):
            i_clouds = _vg_clouds(
                rcs.data[i, :], zmin, thr_noise, thr_clouds, min_snr
            )

            # store info in 2D array
            clouds.append(i_clouds)
            
        options = {
            'zmin': zmin,
            'thr_noise': thr_noise,
            'thr_clouds': thr_clouds,
            'min_snr': min_snr
        }

    # creates dataarrays
    profiles.data["clouds"] = (("time", "altitude"), clouds)
    profiles.data["clouds"] = profiles.data.clouds.assign_attrs({
        'long_name': 'Clouds mask',
        'units': 'bool',
        'time_avg': time_avg,
        'method': method,
        'options': str(options)
    })
    return profiles


def _main():
    import numpy as np
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    #profiles.desaturate_below(z=4000., inplace=True)

    # detection
    profiles.clouds(method="vg", zmin=300, thr_noise=4, thr_clouds=4, verbose=True)
    profiles.plot(show_clouds=True, log=True, vmin=1e-2, vmax=1e1)
    # plot single profile
    #datetime = np.datetime64("2021-09-09T21:20:00")
    #profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True)


if __name__ == "__main__":
    _main()
