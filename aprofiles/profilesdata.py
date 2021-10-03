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



    def gaussian_filter(self, var='attenuated_backscatter_0', sigma=0.5, inplace=False):
        """Function that applies a 2D gaussian filter in order to reduce high frequency noise.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            sigma (scalar or sequence of scalars, optional): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Defaults to 0.
            inplace (bool, optional): if True, replace the variable, else use a copy. Defaults to False.
        
        Returns:
            ProfilesData object
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



    def extrapolation_lowest_layers(self, var='attenuated_backscatter_0', zmin=0, method='cst', inplace=False):
        """Method for extrapolating lowest layers below a certain altitude. This is of particular intrest for instruments subject to After Pulse effect, with saturated signal in the lowest layers.
        We recommend to use a value of zmin=150m due to random values often found below that altitude which perturbs the clouds detection.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            zmin (float, optional): Altitude (in m, AGL) below which the signal is extrapolated. Defaults to 0.
            method (str, optional): 'cst' or 'lin' Method to be used for extrapolation of lowest layers. Defaults to 'cst'.
            inplace (bool, optional): if True, replace the variable. Defaults to False.
        
        Returns:
            ProfilesData object
        """

        #get index of zmin
        zmin_asl = zmin + self.data.station_altitude.data
        imin = np.argmin(abs(self.data.altitude.data-zmin_asl))
        
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
        """Method that corrects the solid angle effect (1/z2) which makes that the backscatter beam more unlikely to be detected with the square of the altitude.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            inplace (bool, optional): if True, replace the variable. Defaults to False.
        
        Returns:
            ProfilesData object
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
        return new_profiles_data



    def detect_fog_or_condensation(self, zmin):
        """Detects fog or condensation relying on the cloud base height 'cloud_base_height' given by the constructor.
        Adds DataArray to DataSet

        Args:
            zmin (float): Altitude AGL (in m) below which a cloud base height is considered a fog or condensation situation. Note: 200 m seems to give good results.
            add_dataarray (bool, optional): Add dataset to datarray if True. Defaults to True.
        
        Returns:
            :class: `ProfilesData object` with additional data array 'fog_or_condensation'.
        """

        first_cloud_base_height = self.data.cloud_base_height.data[:,0]
        fog_or_condensation = [True if x<=zmin else False for x in first_cloud_base_height]

        #creates dataarray
        self.data["fog_or_condensation"] = xr.DataArray(
            data=fog_or_condensation,
            dims=["time"],
            coords=dict(
                time=self.data.time.data,
            ),
            attrs=dict(
                description="Fog or condensation mask.",
            )
        )

        return self
    
    
    def detect_clouds(self, time_avg=1, zmin=0, thr_noise=5.0, thr_clouds=4, verbose=False):
        """Module for clouds detection.

        Args:
            time_avg (int, optional): in minutes, the time during which we aggregates the profiles before detecting clouds. Defaults to 1.
            zmin (float, optional): altitude AGL, in m, above which we look for clouds. Defaults to 0. We recommend using the same value as used in the extrapolation_low_layers method.
            thr_noise (float, optional): threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z). Defaults to 5.
            thr_clouds (float, optional): threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds. Defaults to 4.
            verbose (bool, optional): verbose mode. Defaults to False.

        Returns:
            :class: `ProfilesData object` with additional data arrays 'clouds_bases', 'clouds_peaks', and 'clouds_tops'. 'clouds_bases' correspond to the bases of the clouds. 'clouds_peaks' correspond to the maximum of backscatter signal measured in the clouds. 'clouds_tops' correspond to the top of the cloud if the beam crosses the cloud. If not, the top corresponds to the first value where the signal becomes lower than the one measured at the base of the cloud.
        """

        def _detect_clouds_from_rcs(data, zmin, thr_noise, thr_clouds):
            #data: 1D range corrected signal (rcs)
            #zmin: altitude AGL, in m, above which we detect clouds
            #thr_noise = 10 #threshold used in the test to determine if a couple (base,peak) is significant: data[peak(z)] - data[base(z)] >= thr_noise * noise(z)
            #thr_clouds = 1.5 #threshold used to discriminate aerosol from clouds: data[peak(z)] / data[base(z)] >= thr_clouds
            
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
                mask = np.array([False for x in np.ones(length)])
                mask[indexes_where_True] = len(indexes_where_True)*[True]
                return mask

            #0. rolling average
            avg_data = uniform_filter1d(data, size=3)


            #1. first derivative
            ddata_dz = np.diff(data, prepend=0)


            #2. identifies peaks and base by checking the sign changes of the derivative
            sign_changes = np.diff(np.sign(ddata_dz), append=0)
            all_bases = sign_changes==2
            all_peaks = sign_changes==-2
            #limit to bases above zmin
            zmin_asl = zmin + self.data.station_altitude.data
            imin = np.argmin(abs(self.data.altitude.data-zmin_asl))
            all_bases[0:imin] = [False for i in range(len(all_bases[0:imin]))]
            all_peaks[0:imin] = [False for i in range(len(all_peaks[0:imin]))]
            
            #get indexes
            i_bases = get_indexes(all_bases)
            i_peaks = get_indexes(all_peaks)


            #3. the signal should start with a base
            if i_bases[0]>i_peaks[0] and i_peaks[0]>=1:
                #set base as the minimum between peak and n gates under
                gates = np.arange(i_peaks[0]-5,i_peaks[0])
                i_base = np.argmin([data[gates[gates>=0]]])
                all_bases[i_base]=True
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
            for i, _ in enumerate(i_bases):
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
            for i, _ in enumerate(i_bases):
                data_around_peak = data[i_peaks[i]]
                data_around_base = data[i_bases[i]]
                if abs((data_around_peak - data_around_base) / data_around_base) <= thr_clouds:
                    bases[i_bases[i]] = False
                    peaks[i_peaks[i]] = False
            #get indexes
            i_bases = get_indexes(bases)
            i_peaks = get_indexes(peaks)
            

            #7. find tops of clouds layers
            tops = np.array([False for x in np.ones(len(data))])
            # conditions: look for bases above i_peaks[i], and data[top[i]] <= data[base[i]]
            for i, _ in enumerate(i_bases):
                mask_value = np.array(data<data[i_bases[i]])
                mask_altitude = np.array([False for x in np.ones(len(data))])
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

            
            #9. rebuild base and top masks
            bases = make_mask(len(data), i_bases)
            peaks = make_mask(len(data), [])
            tops = make_mask(len(data), i_tops)
            #find peaks between bases and tops
            for i in np.arange(len(i_bases)):
                peaks[i_bases[i]+np.argmax(data[i_bases[i]:i_tops[i]])] = True
            #get new indexes
            i_peaks = get_indexes(peaks)
            
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

        #we work on profiles averaged in time to reduce the noise
        rcs = self.data.attenuated_backscatter_0
        t_avg = time_avg * 60 #s
        #time resolution in profiles data
        dt_s = min(np.diff(self.data.time.data)).astype('timedelta64[s]').astype(int)
        #number of timestamps to be to averaged
        nt_avg = max([1,round(t_avg/dt_s)])
        rcs = rcs.rolling(time=nt_avg, min_periods=1, center=True).median()

        clouds_bases, clouds_peaks, clouds_tops = [], [], []
        for i in (tqdm(range(len(self.data.time.data))) if verbose else range(len(self.data.time.data))):
            data = rcs.data[i,:]
            clouds = _detect_clouds_from_rcs(data, zmin, thr_noise, thr_clouds)
            
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
                description="Mask - Base height of clouds",
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
                description="Mask - Peak height of clouds",
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
                description="Mask - Top height of clouds",
                units="bool",
                time_avg=time_avg,
                thr_noise=thr_noise,
                thr_clouds=thr_clouds
            )
        )
        return self


    def plot(self, var='attenuated_backscatter_0', datetime=None, zmin=None, zmax=None, vmin=0, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False, cmap='coolwarm'):
        """Plot 2D Quicklook

        Args:
            var (str, optional): Variable of ProfilesData.data Dataset to be plotted. Defaults to 'attenuated_backscatter_0'.
            datetime (np.datetime64, optional): if provided, plot the profile for closest time. If not, plot an image constructed on all profiles.Defaults to None
            zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
            zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
            vmin (float, optional): Minimum value. Defaults to 0.
            vmax (float, optional): Maximum value. If None, calculates max from data.
            log (bool, optional), Use logarithmic scale. Defaults to None.
            show_fog (bool, optional): Add fog detection. Defaults to False.
            show_pbl (bool, optional): Add PBL height. Defaults to False.
            show_clouds (bool, optional): Add clouds detection. Defaults to False.
            cmap (str, optional): Matplotlib colormap. Defaults to 'coolwarm'.
        """
        if datetime==None:
            apro.plot.image.plot(self.data, var, zmin, zmax, vmin, vmax, log, show_fog, show_pbl, show_clouds, cmap=cmap)
        else:
            apro.plot.profile.plot(self.data, datetime, var, zmin, zmax, vmin, vmax, log, show_fog, show_pbl, show_clouds) 
    


def _main():
    import aprofiles as apro
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    #profiles.quickplot('attenuated_backscatter_0', vmin=0, vmax=1, cmap='viridis')
    profiles.range_correction(inplace=True)
    profiles.gaussian_filter(sigma=0.5, inplace=True)
    profiles.plot(log=True, vmin=1e0, vmax=1e5)

    profiles.extrapolation_lowest_layers(zmin=150, inplace=True)
    #profiles.plot(zmax=12000, vmin=1e1, vmax=1e5, log=True, cmap='viridis')

    profiles.detect_fog_or_condensation(zmin=200)
    #profiles.quickplot(zmax=12000, vmin=1e1, vmax=1e5, log=True, add_fog=True, cmap='viridis')

    profiles.detect_clouds(verbose=True)

if __name__ == '__main__':
    _main()

