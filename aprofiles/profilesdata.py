#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - ProfilesData class

import copy

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

import aprofiles as apro


class ProfilesData:
    """Base class representing profiles data.
    """

    def __init__(self, data):
        self.data = data

    @property 
    def data(self): 
        """Data attribute (instance of :class:`xarray.Dataset`)
        """
        return self._data 
    
    @data.setter 
    def data(self, data):
        if not isinstance(data, xr.Dataset):
            raise ValueError("Wrong data type: an xarray Dataset is expected.")
        self._data = data

    def _get_index_from_altitude_AGL(self, altitude):
        """Returns the closest index of the ProfilesData vertical dimension to a given AGL altitude

        Args:
            altitude (float): in m, altitude AGL to look for

        Returns:
            int: Closest index of the vertical dimension to the given altitude AGL
        """    
        altitude_asl = altitude + self.data.station_altitude.data
        return np.argmin(abs(self.data.altitude.data-altitude_asl))

    def _get_resolution(self, which):
        """Returns the resolution of a given dimension. Support 'altitude' and 'time'. The altitude resolution is given in meters, while the time resolution is given in seconds.

        Args:
            which ({'altitude','time'}): Defaults to `'altitude'`.

        Returns:
            float: resolution, in m (if which=='altitude') or in s (if which=='time')
        """
        if which == 'altitude':
            return min(np.diff(self.data.altitude.data))
        elif which == 'time':
            return min(np.diff(self.data.time.data)).astype('timedelta64[s]').astype(int)

    def _get_lowest_clouds(self):
        #returns an array of the altitude (in m, ASL) of the lowest cloud for each timestamp

        def get_true_indexes(mask):
        #mask: list of Bool
        #returns a list indexes where the mask is True
            return [i for i, x in enumerate(mask) if x]
            
        lowest_clouds = []
        for i in np.arange(len(self.data.time.data)):
            i_clouds = get_true_indexes(self.data.clouds_bases.data[i,:])
            if len(i_clouds)>0:
                lowest_clouds.append(self.data.altitude.data[i_clouds[0]])
            else:
                lowest_clouds.append(np.nan)

        return lowest_clouds


    def snr(self, var='attenuated_backscatter_0', step=4, verbose=False):
        """Method that calculates the Signal to Noise Ratio. 

        Args:
            - var (str, optional): Variable of the DataArray to calculate the SNR from. Defaults to 'attenuated_backscatter_0'.
            - step (int, optional): Number of steps around we calculate the SNR for a given altitude. Defaults to 4.
            - verbose (bool, optional): Verbose mode. Defaults to `False`.

        Returns:
            :class: :ref:`ProfilesData` object with additional :class:`xarray.DataArray` 'snr'.

        .. note::
            This calculation is relatively heavy in terms of calculation costs.
        """

        def _1D_snr(array, step):
            array = np.asarray(array)
            snr = []
            for i in np.arange(len(array)):
                gates = np.arange(i-step,i+step)
                indexes = [i for i in gates if i>0 and i<len(array)]
                mean = np.nanmean(array[indexes])
                std = np.nanstd(array[indexes])
                if std!=0:
                    snr.append(mean/std)
                else:
                    snr.append(0)
            return np.asarray(snr)
        
        snr = []
        if verbose:
            print('snr')
        
        for i in (tqdm(range(len(self.data.time.data))) if verbose else range(len(self.data.time.data))):
            snr.append(_1D_snr(self.data[var].data[i,:], step))

        
        #creates dataarrays
        self.data["snr"] = xr.DataArray(
            data=np.asarray(snr),
            dims=["time", "altitude"],
            coords=dict(
                time=self.data.time.data,
                altitude=self.data.altitude.data,
            ),
            attrs=dict(
                long_name="Signal to Noise Ratio",
                units=None,
                step=step
            )
        )
        
        return self


    def gaussian_filter(self, sigma=0.25, var='attenuated_backscatter_0', inplace=False):
        """Applies a 2D gaussian filter in order to reduce high frequency noise.

        Args:
            - sigma (scalar or sequence of scalars, optional): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Defaults to `0.25`.
            - var (str, optional): variable name of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the variable, else use a copy. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object.
        """
        import copy

        from scipy.ndimage import gaussian_filter

        #apply gaussian filter
        filtered_data = gaussian_filter(self.data[var].data, sigma=sigma)

        if inplace:
            self.data[var].data = filtered_data
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = filtered_data
            new_dataset = copied_dataset
        #add attribute
        new_dataset.data[var].attrs['gaussian filter']=sigma
        return new_dataset

        
    def time_avg(self, minutes, var='attenuated_backscatter_0',  inplace=False):
        """Rolling meadian on the time dimension.

        Args:
            - minutes (float): Number of minutes to average over.
            - var (str, optional): variable of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the variable, else use a copy. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object.
        """
        rcs = self.data[var].copy()
        #time conversion from minutes to seconds
        t_avg = minutes * 60
        #time resolution in profiles data in seconds
        dt_s = self._get_resolution('time')
        #number of timestamps to be to averaged
        nt_avg = max([1,round(t_avg/dt_s)])
        #rolling median
        filtered_data = rcs.rolling(time=nt_avg, min_periods=1, center=True).median().data

        if inplace:
            self.data[var].data = filtered_data
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = filtered_data
            new_dataset = copied_dataset
        #add attribute
        new_dataset.data[var].attrs['time averaged (minutes)']=minutes
        return new_dataset


    def extrapolate_below(self, var='attenuated_backscatter_0', zmin=0, method='cst', inplace=False):
        """Method for extrapolating lowest layers below a certain altitude. This is of particular intrest for instruments subject to After Pulse effect, with saturated signal in the lowest layers.
        We recommend to use a value of zmin=150m due to random values often found below that altitude which perturbs the clouds detection.

        Args:
            - var (str, optional): variable of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - zmin (float, optional): Altitude (in m, AGL) below which the signal is extrapolated. Defaults to `0`.
            - method ({'cst', 'lin'}, optional): Method to be used for extrapolation of lowest layers. Defaults to `'cst'`.
            - inplace (bool, optional): if True, replace the variable. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object.
        """

        #get index of zmin
        imin = self._get_index_from_altitude_AGL(zmin)
        
        nt = np.shape(self.data[var].data)[0]

        if method == 'cst':
            #get values at imin
            data_zmin = self.data[var].data[:,imin]
            #generates ones matrice with time/altitude dimension to fill up bottom
            ones = np.ones((nt,imin))
            #replace values
            filling_matrice = np.transpose(np.multiply(np.transpose(ones),data_zmin))
        elif method == 'lin':
            raise NotImplementedError('Linear extrapolation is not implemented yet')
        else:
            raise ValueError('Expected string: lin or cst')

        if inplace:
            self.data[var].data[:,0:imin] = filling_matrice
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data[:,0:imin] = filling_matrice
            new_dataset = copied_dataset
        
        #add attributes
        new_dataset.data[var].attrs['extrapolation_low_layers_altitude_agl']=zmin
        new_dataset.data[var].attrs['extrapolation_low_layers_method']=method
        return new_dataset


    
    def range_correction(self, var='attenuated_backscatter_0', inplace=False):
        """Method that corrects the solid angle effect (1/z2) which makes that the backscatter beam is more unlikely to be detected with the square of the altitude.

        Args:
            - var (str, optional): variable of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the variable. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object.
        
        .. warning::
            Make sure that the range correction is not already applied to the selected variable.
        """

        #for the altitude correction, must one use the altitude above the ground level
        z_agl = self.data.altitude.data - self.data.station_altitude.data
        
        data = self.data[var].data
        range_corrected_data = np.multiply(data,z_agl)

        if inplace:
            self.data[var].data = range_corrected_data
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = range_corrected_data
            new_profiles_data = copied_dataset

        #add attribute
        new_profiles_data.data[var].attrs['range correction']=True
        #remove units
        new_profiles_data.data[var].attrs['units']=None
        return new_profiles_data



    def foc(self, method='cloud_base', var='attenuated_backscatter_0', z_snr=2000., min_snr=2., zmin_cloud=200.,):
        """Detects fog or condensation.

        Args:
            - method ({'cloud_base', 'snr'}, optional): Defaults to `'cloud_base'`.
            - var (str, optional). Used for 'snr' method. Variable from ProfilesData to calculate SNR from. Defaults to `'attenuated_backscatter_0'`.
            - z_snr (float, optional): Used for 'snr' method. Altitude AGL (in m) at which we calculate the SNR. Defaults to `2000.`.
            - min_snr (float, optional): Used for 'snr' method. Minimum SNR under which the profile is considered as containing fog or condensation. Defaults to `2.`.
            - zmin_cloud (float, optional): Used for 'cloud_base' method. Altitude AGL (in m) below which a cloud base height is considered a fog or condensation situation. Defaults to `200.`.
        
        Returns:
            :class: :ref:`ProfilesData` object with additional :class:`xarray.DataArray` 'foc'.
        """

        def _detect_fog_from_cloud_base_height(self, zmin_cloud):
            #returns a bool list with True where fog/condensation cases
            #if the base of the first cloud (given by the constructor) is below 
            first_cloud_base_height = self.data.cloud_base_height.data[:,0]
            #condition
            foc = [True if x<=zmin_cloud else False for x in first_cloud_base_height]
            return foc
        
        def _detect_fog_from_snr(self, z_snr, var, min_snr):
            #returns a bool list with True where fog/condensation cases

            def _snr_at_iz(array, iz, step):
                #calculates the snr from array at iz around step points
                gates = np.arange(iz-step,iz+step)
                indexes = [i for i in gates if i>0 and i<len(array)]
                mean = np.nanmean(array[indexes])
                std = np.nanstd(array[indexes], ddof=0)
                if std!=0:
                    return mean/std
                else:
                    return 0

            #calculates snr at z_snr
            iz_snr = self._get_index_from_altitude_AGL(z_snr)
            #calculates snr at each timestamp
            snr = [_snr_at_iz(self.data[var].data[i,:], iz_snr, step=4) for i in range(len(self.data.time.data))]
            #condition
            foc = [True if x<=min_snr else False for x in snr]
            return foc


        if method=='cloud_base':
            foc = _detect_fog_from_cloud_base_height(self, zmin_cloud)
        elif method.upper() == 'SNR':
            foc = _detect_fog_from_snr(self, z_snr, var, min_snr)

        #creates dataarray
        self.data["foc"] = xr.DataArray(
            data=foc,
            dims=["time"],
            coords=dict(
                time=self.data.time.data,
            ),
            attrs=dict(
                long_name="Fog or condensation mask.",
            )
        )

        return self
    
    
    def clouds(self, time_avg=1, zmin=0, thr_noise=5.0, thr_clouds=4, min_snr=0., verbose=False):
        """Module for clouds detection.

        Args:
            - time_avg (int, optional): in minutes, the time during which we aggregates the profiles before detecting clouds. Defaults to `1`.
            - zmin (float, optional): altitude AGL, in m, above which we look for clouds. Defaults to `0`. We recommend using the same value as used in the extrapolation_low_layers method.
            - thr_noise (float, optional): threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z). Defaults to `5`.
            - thr_clouds (float, optional): threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds. Defaults to `4`.
            - min_snr (float, optional). Minimum SNR required at the clouds peak value to consider the cloud as valid. Defaults to `0`.
            - verbose (bool, optional): verbose mode. Defaults to `False`.

        Returns:
            :class: :ref:`ProfilesData` object with additional :class:`xarray.DataArray`: 'clouds_bases', 'clouds_peaks', and 'clouds_tops'. 'clouds_bases' correspond to the bases of the clouds. 'clouds_peaks' correspond to the maximum of backscatter signal measured in the clouds. 'clouds_tops' correspond to the top of the cloud if the beam crosses the cloud. If not, the top corresponds to the first value where the signal becomes lower than the one measured at the base of the cloud.
        """

        def _detect_clouds_from_rcs(data, zmin, thr_noise, thr_clouds, min_snr):
            #data: 1D range corrected signal (rcs)
            #zmin: altitude AGL, in m, above which we detect clouds
            #thr_noise: threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z)
            #thr_clouds: threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds
            #min_snr: minimum SNR required at the clouds peak value to consider the cloud as valid. Defaults to 2.
            
            from scipy import signal
            from scipy.ndimage.filters import uniform_filter1d

            #some useful functions:
            def get_indexes(mask):
                #mask: list of Bool
                #returns a list indexes where the mask is True
                return [i for i, x in enumerate(mask) if x]
            
            def make_mask(length, indexes_where_True):
                #length: int: length of the mask
                #indexes_where_true: list
                mask = np.asarray([False for x in np.ones(length)])
                mask[indexes_where_True] = len(indexes_where_True)*[True]
                return mask
            
            def _snr_at_iz(array, iz, step):
                #calculates the snr from array at iz around step points
                gates = np.arange(iz-step,iz+step)
                indexes = [i for i in gates if i>0 and i<len(array)]
                mean = np.nanmean(array[indexes])
                std = np.nanstd(array[indexes], ddof=0)
                if std!=0:
                    return mean/std
                else:
                    return 0

            #0. rolling average
            avg_data = uniform_filter1d(data, size=3)


            #1. first derivative
            ddata_dz = np.diff(data, prepend=0)


            #2. identifies peaks and base by checking the sign changes of the derivative
            sign_changes = np.diff(np.sign(ddata_dz), append=0)
            all_bases = sign_changes==2
            all_peaks = sign_changes==-2
            #limit to bases above zmin
            imin = self._get_index_from_altitude_AGL(zmin)
            all_bases[0:imin] = [False for i in range(len(all_bases[0:imin]))]
            all_peaks[0:imin] = [False for i in range(len(all_peaks[0:imin]))]
            
            #get indexes
            i_bases = get_indexes(all_bases)
            i_peaks = get_indexes(all_peaks)


            #3. the signal should start with a base
            if i_bases[0]>i_peaks[0] and i_peaks[0]>=1:
                #set base as the minimum between peak and n gates under
                gates = np.arange(i_peaks[0]-5,i_peaks[0])
                i_base = gates[np.argmin([data[gates[gates>=0]]])]
                if i_base>=imin:
                    all_bases[i_base]=True
                else:
                    i_peaks[0] = False
            #update indexes
            i_bases = get_indexes(all_bases)

            
            #4. keeps significant couples (base,peak)
            # a layer can be considered as a proper layer if the difference of signal between the peak and the base is significant (larger than the noise level)
            # noise evaluation (using a high passing frequency filter)
            b, a = signal.butter(1, 0.3, btype='high')
            noise = signal.filtfilt(b, a, data)
            #rolling average of the noise
            avg_abs_noise = uniform_filter1d(abs(noise), size=100)
            #make sure we have as many peaks as bases
            if len(i_peaks)!=len(i_bases):
                min_len = min([len(i_peaks),len(i_bases)])
                i_peaks = i_peaks[0:min_len]
                i_bases = i_bases[0:min_len]
                

            # data[peak(z)] - data[base(z)] >= thr_noise * noise(z)
            bases, peaks = all_bases, all_peaks
            for i in range(len(i_bases)):
                #data_around_peak = np.mean(data[i_peaks[i]-1:i_peaks[i]+1])
                #data_around_base = np.mean(data[i_bases[i]-1:i_bases[i]+1])
                data_around_peak = avg_data[i_peaks[i]]
                data_around_base = avg_data[i_bases[i]]
                if data_around_peak - data_around_base <= thr_noise * avg_abs_noise[i_bases[i]]:
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False
            #get indexes
            i_bases = get_indexes(bases)
            i_peaks = get_indexes(peaks)


            #5. make sure we finish by a peak: remove last base 
            if len(i_bases)>len(i_peaks):
                bases[i_bases[-1]] = False
                i_bases.pop()

            #6. distinction between aerosol and clouds
            for i in range(len(i_bases)):
                data_around_peak = data[i_peaks[i]]
                data_around_base = data[i_bases[i]]
                if abs((data_around_peak - data_around_base) / data_around_base) <= thr_clouds:
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False
            #get indexes
            i_bases = get_indexes(bases)
            i_peaks = get_indexes(peaks)
            

            #7. find tops of clouds layers
            tops = np.asarray([False for x in np.ones(len(data))])
            # conditions: look for bases above i_peaks[i], and data[top[i]] <= data[base[i]]
            for i in range(len(i_bases)):
                mask_value = np.asarray(data<data[i_bases[i]])
                mask_altitude = np.asarray([False for x in np.ones(len(data))])
                mask_altitude[i_bases[i]:] = True
                #the top is the first value that corresponds to the intersection of the two masks
                cross_mask = np.logical_and(mask_value, mask_altitude)
                i_cross_mask = get_indexes(cross_mask)
                if len(i_cross_mask)>0:
                    if tops[i_cross_mask[0]]:
                        #print('top already found. remove current layer')
                        bases[i_bases[i]] = False
                        peaks[i_peaks[i]] = False    
                    else:
                        #print('found top at ',i_cross_mask[0], 'for base ',i_bases[i])
                        tops[i_cross_mask[0]] = True
                else:
                    #print('no top found for base',i_bases[i])
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False

            #get indexes
            i_bases = get_indexes(bases)
            i_peaks = get_indexes(peaks)
            i_tops = get_indexes(tops)

            
            #8. merge layers: just focus on bases and tops
            #drop layer if base of next layer below top of current layer top of current layer
            for i in np.arange(len(i_bases)-1):
                if i<len(i_bases)-1 and i_bases[i+1]<=i_tops[i]:
                    i_bases.remove(i_bases[i+1])
                    i_tops.remove(i_tops[i])

            
            #9. finds peaks as maximum value between base and top
            i_peaks = [i_bases[i]+np.argmax(data[i_bases[i]:i_tops[i]]) for i in range(len(i_bases))]


            #10. check snr at peak levels
            remove_bases, remove_peaks, remove_tops = [], [], []
            for i in range(len(i_peaks)):
                if _snr_at_iz(data, i_peaks[i], step=4)<min_snr:
                    remove_bases.append(i_bases[i])
                    remove_peaks.append(i_peaks[i])
                    remove_tops.append(i_tops[i])
            # remove indexes
            i_bases = [i_base for i_base in i_bases if i_base not in remove_bases]
            i_peaks = [i_peak for i_peak in i_peaks if i_peak not in remove_peaks]
            i_tops = [i_top for i_top in i_tops if i_top not in remove_tops]


            #11. rebuild masks from indexes
            bases = make_mask(len(data), i_bases)
            peaks = make_mask(len(data), i_peaks)
            tops = make_mask(len(data), i_tops)
            
            
            """
            #some plotting
            fig, axs = plt.subplots(1,2,figsize=(10,10))
            
            ymin, ymax = 000, 15000
            altitude_agl = profiles.data.altitude.data - profiles.data.station_altitude.data
            
            #signal on the left
            axs[0].plot(data, altitude_agl, 'b', label='rcs')
            axs[0].plot(avg_data, altitude_agl, 'c', label='rcs')
            axs[0].plot(avg_abs_noise,altitude_agl,':b', label='noise level')
            axs[0].plot(avg_abs_noise*thr_noise,altitude_agl,':b', label='noise level * {}'.format(thr_noise))
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
                'bases': bases,
                'peaks': peaks,
                'tops': tops,
            }


        #make sure some corrections have been done before
        #if 'range correction' not in self.data.attenuated_backscatter_0.attrs or not self.data.attenuated_backscatter_0.attrs['range correction']:
        #    print('The range correction has not been applied to the backscatter profiles')
        #    pass

        if verbose:
            print('clouds')

        #we work on profiles averaged in time to reduce the noise
        rcs = self.time_avg(time_avg, var='attenuated_backscatter_0').data.attenuated_backscatter_0

        clouds_bases, clouds_peaks, clouds_tops = [], [], []
        for i in (tqdm(range(len(self.data.time.data))) if verbose else range(len(self.data.time.data))):
            clouds = _detect_clouds_from_rcs(rcs.data[i,:], zmin, thr_noise, thr_clouds, min_snr)
            
            #store info in 2D array
            clouds_bases.append(clouds['bases'])
            clouds_peaks.append(clouds['peaks'])
            clouds_tops.append(clouds['tops'])
        
        #creates dataarrays
        self.data["clouds_bases"] = xr.DataArray(
            data=clouds_bases,
            dims=["time", "altitude"],
            coords=dict(
                time=self.data.time.data,
                altitude=self.data.altitude.data,
            ),
            attrs=dict(
                long_name="Mask - Base height of clouds",
                units="bool",
                time_avg=time_avg,
                thr_noise=thr_noise,
                thr_clouds=thr_clouds
            )
        )
        self.data["clouds_peaks"] = xr.DataArray(
            data=clouds_peaks,
            dims=["time", "altitude"],
            coords=dict(
                time=self.data.time.data,
                altitude=self.data.altitude.data,
            ),
            attrs=dict(
                long_name="Mask - Peak height of clouds",
                units="bool",
                time_avg=time_avg,
                thr_noise=thr_noise,
                thr_clouds=thr_clouds
            )
        )
        self.data["clouds_tops"] = xr.DataArray(
            data=clouds_tops,
            dims=["time", "altitude"],
            coords=dict(
                time=self.data.time.data,
                altitude=self.data.altitude.data,
            ),
            attrs=dict(
                long_name="Mask - Top height of clouds",
                units="bool",
                time_avg=time_avg,
                thr_noise=thr_noise,
                thr_clouds=thr_clouds
            )
        )
        return self

    def pbl(self, time_avg=1, zmin=100., zmax=3000., wav_width=200., under_clouds=True, min_snr=2., verbose=False):
        """Detects Planetary Boundary Layer Height between zmin and zmax using convolution with a wavelet.

        Args:
            - time_avg (int, optional): in minutes, the time during which we aggregate the profiles before detecting the PBL. Defaults to `1`.
            - zmin (float, optional): maximum altitude AGL, in m, for retrieving the PBL. Defaults to `100`.
            - zmin (float, optional): minimum altitude AGL, in m, for retrieving the PBL. Defaults to `3000`.
            - wav_width (float, optional): Width of the wavelet used in the convolution, in m. Defaults to `200`.
            - under_clouds (bool, optional): If True, and if clouds detection have been called before, force the PBL to be found below the first cloud detected in the profile. Defaults to `True`.
            - min_snr (float, optional). Minimum SNR at the retrieved PBL height required to return a valid value. Defaults to `2.`.
            - verbose (bool, optional): verbose mode. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object with additional :class:`xarray.DataArray` 'pbl'.
        
        Todo:
            for now, returns strongets gradient. Must return the highest negative gradient!
        """        

        def _snr_at_iz(array, iz, step):
            #calculates the snr from array at iz around step points
            gates = np.arange(iz-step,iz+step)
            indexes = [i for i in gates if i>0 and i<len(array)]
            mean = np.nanmean(array[indexes])
            std = np.nanstd(array[indexes], ddof=0)
            if std!=0:
                return mean/std
            else:
                return 0


        def _detect_pbl_from_rcs(data, zmin, zmax, wav_width, min_snr):
            #detect pbl from range corrected signal between zmin and zmax using convolution with a wavelet..

            from scipy import signal

            #define wavelet with constant width
            npoints = len(data)
            width = wav_width #in meter
            wav = signal.ricker(npoints, width/self._get_resolution('altitude'))

            #simple convolution
            convolution = signal.convolve(data, wav, mode='same')

            #the PBL is the maximum of the convolution
            #sets to nan outside of PBL search range
            convolution[0:self._get_index_from_altitude_AGL(zmin):] = np.nan
            convolution[self._get_index_from_altitude_AGL(zmax):] = np.nan
            i_pbl = np.nanargmax(abs(convolution))
            #i_pbl = np.nanargmin(convolution)
            
            
            #calculates SNR
            snr =  _snr_at_iz(data, i_pbl, step=4)

            if snr>2:
                return self.data.altitude.data[i_pbl]
            else:
                return np.nan
        
        #we work on profiles averaged in time to reduce the noise
        rcs = self.time_avg(time_avg, var='attenuated_backscatter_0', inplace=False).data.attenuated_backscatter_0


        #if under_clouds, check if clouds_bases is available
        if under_clouds and 'clouds_bases' in list(self.data.data_vars):
            lowest_clouds = self._get_lowest_clouds()
        elif under_clouds and not 'clouds_bases' in list(self.data.data_vars):
            import warnings
            warnings.warn("under_clouds parameter sets to True (defaults value) when the clouds detection has not been applied to ProfileData object.")
            lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]
        else:
            lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]

        if verbose:
            print('pbl')

        pbl = []
        for i in (tqdm(range(len(self.data.time.data))) if verbose else range(len(self.data.time.data))):
            lowest_cloud_agl = lowest_clouds[i] - self.data.station_altitude.data
            pbl.append(_detect_pbl_from_rcs(rcs.data[i,:], zmin, np.nanmin([zmax, lowest_cloud_agl]), wav_width, min_snr))

         #creates dataarrays
        self.data["pbl"] = xr.DataArray(
            data=pbl,
            dims=["time"],
            coords=dict(
                time=self.data.time.data
            ),
            attrs=dict(
                long_name="Planetary Boundary Layer Height, ASL",
                units="m",
                time_avg=time_avg,
                zmin=zmin,
                zmax=zmax
            )
        )
    
    def klett_inversion(self, time_avg=1, zmin=4000., zmax=6000., min_snr=0., under_clouds=True, method='backward', apriori={'lr': 50.}, remove_outliers=False, verbose=False):
        """Klett inversion using an apriori.

        Args:
            - time_avg (int, optional): in minutes, the time during which we aggregate the profiles before detecting the PBL. Defaults to `1`.
            - zmin (float, optional): minimum altitude AGL, in m, for looking for the initialization altitude. Defaults to `4000.`.
            - zmax (float, optional): maximum altitude AGL, in m, for looking for the initialization altitude. Defaults to `6000.`.
            - min_snr (float, optional). Minimum SNR required at the reference altitude to be valid. Defaults to `0`.
            - under_clouds (bool, optional): If True, and if clouds detection have been called before, force the initialization altitude to be found below the first cloud detected in the profile. Defaults to `True`.
            - method ({'backward', 'forward'}, optional). Defaults to `'forward'`.
            - apriori (dict, optional). A Priori value to be used to constrain the inversion. Valid keys: 'lr' (Lidar Ratio, in sr) and 'aod' (unitless). Defaults to `{'lr': 50}`.
            - remove_outliers (bool, optional). Remove profiles considered as outliers based on aod calculation ([>0, <1]). Defaults to `False` (while development. to be changed afterwards).
            - verbose (bool, optional): verbose mode. Defaults to `False`.
        
        Returns:
            :class: :ref:`ProfilesData` object with additional :class:`xarray.DataArray` `ext`.
        """

        def _iref(data, imin, imax, min_snr):
            #function that returns best index to be used for initializing the Klett inversion

            def _snr_at_iz(array, iz, step):
                #calculates the snr from array at iz around step points
                gates = np.arange(iz-step,iz+step)
                indexes = [i for i in gates if i>0 and i<len(array)]
                mean = np.nanmean(array[indexes])
                std = np.nanstd(array[indexes], ddof=0)
                if std!=0:
                    return mean/std
                else:
                    return 0
    
            #it is important to copy the data not to modify it outside of the function
            import copy
            data = data.copy()

            #check if imin below imax
            if imin<imax:
                #limit from imin to imax
                maxdata = np.nanmax(data)
                data[0:imin] = maxdata
                data[imax:] = maxdata
                
                #running average
                from scipy.ndimage.filters import uniform_filter1d
                avg_data = uniform_filter1d(data, size=3)

                if not np.isnan( np.nanmin(avg_data)):
                    #get minimum from the averaged signal
                    ilow = np.nanargmin(avg_data)

                    #around minimum, get index of closest signal to average signal
                    n_around_min = 3
                    iclose = np.nanargmin(abs(data[ilow-n_around_min:ilow+n_around_min] - avg_data[ilow-n_around_min:ilow+n_around_min]))

                    if _snr_at_iz(data, iclose, step=4)<min_snr:
                        return None
                    else:
                        return ilow+iclose
                else :
                    return None
            else:
                return None

        def klett(data, iref, method, apriori, rayleigh):
            #returns array of extinction in km-1
            #rayleigh: aprofiles.rayleigh.Rayleigh object

            if iref!=None:
                if 'aod' in apriori:
                    #search by dichotomy the LR that matches the apriori aod
                    raise NotImplementedError('AOD apriori is not implemented yet')
                    lr_aer = 50
                else:
                    #if we assume the LR, no need to minimize for matching aod 
                    lr_aer = apriori['lr']
            
                import math
                lr_mol = 8.*math.pi/3.
                    
                #calculation
                if method=='backward':
                    
                    #vertical resolution
                    dz = min(np.diff(rayleigh.altitude))

                    int1_a = np.cumsum((lr_aer-lr_mol)*rayleigh.backscatter[:iref]*dz)
                    int1_b = [2*int1_a[-1] - 2*int1_a[i] for i in range(iref)]
                    phi = [np.log(abs(data[i]/data[iref])) + int1_b[i] for i in range(iref)]

                    int2_a = 2*np.nancumsum(lr_aer*np.exp(phi)*dz)
                    int2_b = [int2_a[-1] - int2_a[i] for i in range(iref)]

                    #initialize total backscatter
                    back_aer_iref = 0 #m-1
                    beta_tot_iref = rayleigh.backscatter[iref] + back_aer_iref

                    #total backscatter
                    beta_tot = [np.exp(phi[i])/((1/beta_tot_iref)+int2_b[i]) for i in range(iref)]
                    #aerosol backsatter (m-1.sr-1)
                    beta_aer = beta_tot - rayleigh.backscatter[:iref]
                    #aerosol extinction (m-1)
                    sigma_aer=lr_aer*beta_aer
                    #returns extinction in km-1 when valid, and np.nan elsewhere
                    ext = [sigma_aer[i]*1e3 if i<len(sigma_aer) else np.nan for i in range(len(data))]
            else:
                ext = [np.nan for i in range(len(data))]

            return ext
        """
        #we work on profiles averaged in time to reduce the noise
        rcs = self.data.attenuated_backscatter_0
        t_avg = time_avg * 60 #s
        #time resolution in profiles data
        dt_s = self._get_resolution('time')
        #number of timestamps to be averaged
        nt_avg = max([1,round(t_avg/dt_s)])

        #average profiles
        rcs_data = rcs.rolling(time=nt_avg, min_periods=1, center=True).median().data
        """
        
        #we work on profiles averaged in time to reduce the noise
        rcs = self.time_avg(time_avg, var='attenuated_backscatter_0', inplace=False).data.attenuated_backscatter_0

        """
        #if clouds detected, set to nan profiles where cloud is found below 4000m
        lowest_clouds = self._get_lowest_clouds()
        for i in range(len(self.data.time.data)):
            if lowest_clouds[i]<=4000:
                rcs.data[i,:] = [np.nan for _ in rcs.data[i,:]]
        """

        #if under_clouds, check if clouds_bases is available
        if under_clouds and 'clouds_bases' in list(self.data.data_vars):
            lowest_clouds = self._get_lowest_clouds()
        elif under_clouds and not 'clouds_bases' in list(self.data.data_vars):
            import warnings
            warnings.warn("under_clouds parameter sets to True (defaults value) when the clouds detection has not been applied to ProfileData object.")
            lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]
        else:
            lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]
        
        #aerosol retrieval requires a molecular profile
        altitude = self.data.altitude.data
        wavelength = self.data.l0_wavelength.data
        rayleigh = apro.rayleigh.Rayleigh(altitude, T0=298, P0=1013, wavelength=wavelength);

        if verbose:
            print('klett')

        #aerosol inversion
        ext, lr, aod = [], [], []
        aod_min, aod_max = 0, 1
        vertical_resolution = self._get_resolution('altitude')
        for i in (tqdm(range(len(self.data.time.data))) if verbose else range(len(self.data.time.data))):

            #reference altitude
            lowest_cloud_agl = lowest_clouds[i] - self.data.station_altitude.data
            imin = self._get_index_from_altitude_AGL(zmin)
            imax = self._get_index_from_altitude_AGL(np.nanmin([zmax, lowest_cloud_agl]))
            iref = _iref(rcs.data[i,:], imin, imax, min_snr)

            #klett inversion
            _ext = klett(rcs.data[i,:], iref, method, apriori, rayleigh)

            #add aod and lr
            if 'aod' in apriori:
                    #search by dichotomy the LR that matches the apriori aod
                    raise NotImplementedError('AOD apriori is not implemented yet')
            else:
                #if we assume the LR, no need to minimize for matching aod
                _lr = apriori['lr']
                _aod = np.nancumsum(np.asarray(_ext)*vertical_resolution)[-1]
                if remove_outliers and _aod<aod_min or remove_outliers and _aod>aod_max:
                    lr.append(np.nan)
                    aod.append(np.nan)
                    ext.append([np.nan for x in _ext])
                else:
                    lr.append(_lr)
                    aod.append(_aod)
                    ext.append(_ext)


        #creates dataarrays
        self.data["ext"] = xr.DataArray(
            data=ext,
            dims=["time", "altitude"],
            coords=dict(
                time=self.data.time.data,
                altitude=self.data.altitude.data
            ),
            attrs=dict(
                long_name="Extinction Coefficient at {} nm".format(int(wavelength)),
                method="{} Klett".format(method.capitalize()),
                units="km-1",
                time_avg=time_avg,
                zmin=zmin,
                zmax=zmax,
                apriori=apriori
            )
        )

        self.data["aod"] = xr.DataArray(
            data=aod,
            dims=["time"],
            coords=dict(
                time=self.data.time.data
            ),
            attrs=dict(
                long_name="Aerosol Optical Depth",
                units=None
            )
        )

        self.data["lr"] = xr.DataArray(
            data=lr,
            dims=["time"],
            coords=dict(
                time=self.data.time.data
            ),
            attrs=dict(
                long_name="Lidar Ratio",
                units="sr"
            )
        )


    def plot(self, var='attenuated_backscatter_0', datetime=None, zref='agl', zmin=None, zmax=None, vmin=None, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False, cmap='coolwarm', **kwargs):
        """Plotting method. Quicklook or single profile.

        Args:
            - var (str, optional): Variable of ProfilesData.data Dataset to be plotted. Defaults to `'attenuated_backscatter_0'`.
            - datetime (np.datetime64, optional): if provided, plot the profile for closest time. If not, plot an image constructed on all profiles.Defaults to `None`.
            - zref (str, optional): Reference altitude. Expected values: 'agl' (above ground level) or 'asl' (above ea level). Defaults to 'agl'
            - zmin (float, optional): Minimum altitude AGL (m). Defaults to `None`. If `None`, sets to minimum available altitude.
            - zmax (float, optional): Maximum altitude AGL (m). Defaults to `None`. If `None`, sets maximum available altitude.
            - vmin (float, optional): Minimum value. Defaults to `None`.
            - vmax (float, optional): Maximum value. Defaults to `None`. If `None`, calculates max from data.
            - log (bool, optional), Use logarithmic scale. Defaults to `False`.
            - show_fog (bool, optional): Add fog detection. Defaults to `False`.
            - show_pbl (bool, optional): Add PBL height. Defaults to `False`.
            - show_clouds (bool, optional): Add clouds detection. Defaults to `False`.
            - cmap (str, optional): Matplotlib colormap. Defaults to `'coolwarm'`.
        """

        #here, check the dimension. If the variable has only the time dimention, calls timeseries method
        if datetime==None:
            #check dimension of var
            if len(list(self.data[var].dims))==2:
                apro.plot.image.plot(self.data, var, zref, zmin, zmax, vmin, vmax, log, show_fog, show_pbl, show_clouds, cmap=cmap)
            else:
                apro.plot.timeseries.plot(self.data, var, **kwargs)
        else:
            apro.plot.profile.plot(self.data, datetime, var, zref, zmin, zmax, vmin, vmax, log, show_fog, show_pbl, show_clouds)
    


def _main():
    import aprofiles as apro
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    #profiles.quickplot('attenuated_backscatter_0', vmin=0, vmax=1, cmap='viridis')
    profiles.range_correction(inplace=True)
    profiles.gaussian_filter(sigma=0.25, inplace=True)
    profiles.plot(log=True, vmin=1e0, vmax=1e5)

    profiles.extrapolate_below(zmin=150, inplace=True)
    #profiles.plot(zmax=12000, vmin=1e1, vmax=1e5, log=True, cmap='viridis')

    profiles.foc(zmin=200)
    #profiles.quickplot(zmax=12000, vmin=1e1, vmax=1e5, log=True, add_fog=True, cmap='viridis')

    profiles.clouds(verbose=True)

if __name__ == '__main__':
    _main()

