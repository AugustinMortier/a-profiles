# @author Augustin Mortier
# @desc A-Profiles - Clouds detection

import numpy as np
from rich.progress import track

from aprofiles import utils


def detect_clouds(profiles, time_avg=1., zmin=0., thr_noise=5., thr_clouds=4., min_snr=0., verbose=False):
    """Module for *clouds detection*.
    The detection is performed on each individual profile. It is based on the analysis of the vertical gradient of the profile as respect to the level of noise measured in the profile.

    Args:
        - profiles (:class:`aprofiles.profiles.ProfilesData`): `ProfilesData` instance.
        - time_avg (float, optional): in minutes, the time during which we aggregates the profiles prior to the clouds detection. Defaults to `1`.
        - zmin (float, optional): altitude AGL, in m, above which we look for clouds. Defaults to `0`. We recommend using the same value as used in the extrapolation_low_layers method.
        - thr_noise (float, optional): threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z). Defaults to `5`.
        - thr_clouds (float, optional): threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds. Defaults to `4`.
        - min_snr (float, optional). Minimum SNR required at the clouds peak value to consider the cloud as valid. Defaults to `0`.
        - verbose (bool, optional): verbose mode. Defaults to `False`.

    Returns:
        :class:`aprofiles.profiles.ProfilesData` object with additional :class:`xarray.DataArray` in :attr:`aprofiles.profiles.ProfilesData.data`.
            - `'clouds_bases' (time, altitude)`: mask array corresponding to the bases of the clouds.
            - `'clouds_peaks' (time, altitude)`: mask array corresponding to the peaks (maximum signal measured) of the clouds.
            - `'clouds_tops' (time, altitude)`: mask array corresponding to the top of the cloud if the beam crosses the cloud. If not, the top corresponds to the first value where the signal becomes lower than the one measured at the base of the cloud.

    Example:
        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # clouds detection
        >>> profiles.clouds(zmin=300.)
        >>> # attenuated backscatter image with clouds
        >>> profiles.plot(show_clouds=True, vmin=1e-2, vmax=1e1, log=True)

        .. figure:: ../../examples/images/clouds.png
            :scale: 50 %
            :alt: clouds detection

            Clouds detection.
    """

    def _detect_clouds_from_rcs(data, zmin, thr_noise, thr_clouds, min_snr):
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

        def _find_tops2(data, i_bases, i_peaks):
            # function that finds the top of the layers by identifying the positive gradient above the peak
            tops = np.asarray([False for x in np.ones(len(data))])
            i_tops = []

            gradient = np.gradient(data)
            for i in range(len(i_bases)):
                mask_value = np.asarray(
                    [True if gradient[j] > 0 else False for j in range(len(data))]
                )
                mask_altitude = np.asarray(
                    [True if j > i_peaks[i] else False for j in range(len(data))]
                )
                # the top is the first value that corresponds to the intersection of the two masks
                cross_mask = np.logical_and(mask_value, mask_altitude)
                i_cross_mask = utils.get_true_indexes(cross_mask)
                if len(i_cross_mask) > 0:
                    if tops[i_cross_mask[0]]:
                        # print('top already found. remove current layer')
                        bases[i_bases[i]] = False
                        peaks[i_peaks[i]] = False
                    else:
                        tops[i_cross_mask[0]] = True
                        i_tops.append(i_cross_mask[0])
                else:
                    # print('no top found for base',i_bases[i])
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False
            # it is important to keep the tops in the same order, so not to use utils.get_true_indexes() function here
            return utils.get_true_indexes(bases), utils.get_true_indexes(peaks), i_tops

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

        # 11. rebuild masks from indexes
        bases, peaks, tops = _make_all_masks(data, i_bases, i_peaks, i_tops)

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

        return {
            "bases": bases,
            "peaks": peaks,
            "tops": tops,
        }

    # we work on profiles averaged in time to reduce the noise
    rcs = profiles.time_avg(
        time_avg, var="attenuated_backscatter_0"
    ).data.attenuated_backscatter_0

    clouds_bases, clouds_peaks, clouds_tops = [], [], []
    for i in (track(range(len(profiles.data.time.data)), description="clouds",disable=not verbose)):
        clouds = _detect_clouds_from_rcs(
            rcs.data[i, :], zmin, thr_noise, thr_clouds, min_snr
        )

        # store info in 2D array
        clouds_bases.append(clouds["bases"])
        clouds_peaks.append(clouds["peaks"])
        clouds_tops.append(clouds["tops"])

    # creates dataarrays
    profiles.data["clouds_bases"] = (("time", "altitude"), clouds_bases)
    profiles.data["clouds_bases"] = profiles.data.clouds_bases.assign_attrs({
        'long_name': 'Mask - Base height of clouds',
        'units': 'bool',
        'time_avg': time_avg,
        'thr_noise': thr_noise,
        'thr_clouds': thr_clouds,
    })

    profiles.data["clouds_peaks"] = (("time", "altitude"), clouds_peaks)
    profiles.data["clouds_peaks"] = profiles.data.clouds_peaks.assign_attrs({
        'long_name': 'Mask - Peak height of clouds',
        'units': 'bool',
        'time_avg': time_avg,
        'thr_noise': thr_noise,
        'thr_clouds': thr_clouds,
    })

    profiles.data["clouds_tops"] = (("time", "altitude"), clouds_tops)
    profiles.data["clouds_tops"] = profiles.data.clouds_tops.assign_attrs({
        'long_name': 'Mask - Top height of clouds',
        'units': 'bool',
        'time_avg': time_avg,
        'thr_noise': thr_noise,
        'thr_clouds': thr_clouds,
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
    profiles.clouds(zmin=300, thr_noise=4, thr_clouds=4, verbose=True)
    profiles.plot(show_clouds=True, log=True, vmin=1e-2, vmax=1e1)
    # plot single profile
    datetime = np.datetime64("2021-09-09T14:00:00")
    profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True)


if __name__ == "__main__":
    _main()
