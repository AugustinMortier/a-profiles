# @author Augustin Mortier
# @desc A-Profiles - Extinction to Backscatter class

import random
from datetime import date, datetime, time

import numpy as np
import pandas as pd
import xarray as xr

from aprofiles.profiles import ProfilesData
from aprofiles.rayleigh import RayleighData


class ExtinctionToAttenuatedBackscatter:
    """Class for simulating measurements (attenuated backscatter profiles) for different models.

    Attributes:
        - `model` ({'rayleigh', 'standard', 'aloft'}): atmospheric model to be simulated.
        - `wavelength` (float): Wavelength of the Rayleigh profile to be computed, in nm.
        - `lidar_ratio` (float): Lidar Ratio, in sr.
        - `noise` (float): Noise level. The noise is normalized to the maximum extinction value in the profile.

    Example:
            >>> # some imports
            >>> import aprofiles as apro
            >>> # simulate rayleigh profiles with a random noise
            >>> simulator = apro.simulator.ExtinctionToAttenuatedBackscatter(model = 'rayleigh', wavelength = 1064., lidar_ratio = 50., noise = 0.5);
            # calls the to_profiles_data method
            sim_profiles = simulator.to_profiles_data()
            # plot modelled extinction
            sim_profiles.plot('extinction_model')

            .. figure:: ../../docs/_static/images/simulation_rayleigh.png
                :scale: 80 %
                :alt: rayleigh simulation

                Simulation of pure Rayleigh profiles.
    """    
    # get the right reading class
    def __init__(self, model, wavelength, lidar_ratio, noise):
        self.model = model
        self.wavelength = wavelength
        self.lidar_ratio = lidar_ratio
        self.noise = noise

        # workflow
        ds = self.model_extinction()
        ds = self.simulate_attenuated_backscatter(ds)
        self.data = ds
    
    def to_profiles_data(self: xr.DataArray):
        """Method which returns an instance of the :class:`aprofiles.profiles.ProfilesData` class.

        Returns:
            :class:`aprofiles.profiles.ProfilesData` object
        """  
        return ProfilesData(self.data)

    def model_extinction(self):
        """Calculates the extinction coefficient profiles for a given aerosol model (vertical distribution, lidar ratio) at a given wavelength and with a random noise.

        Returns:
            :class:`xr.Dataset`
        """        
        _time = pd.date_range(
            start=datetime.combine(date.today(), time(0, 0, 0)),
            end=datetime.combine(date.today(), time(23, 59, 59)),
            periods=24 * 60 / 5,
        ).tolist()
        altitude = np.arange(15, 15000, 15)

        # open molecular profile
        rayleigh = RayleighData(altitude, self.wavelength, T0=298, P0=1013)

        extinction = []
        # model clear: twice the molecular
        if self.model == "empty":
            extinction_profile = np.asarray([0 for z in altitude])
        if self.model == "step":
            extinction_profile = np.asarray([0.1e-3 if z<3000 else 0 for z in altitude])
        if self.model == "aloft":
            #TODO: gaussian in altitude (3 km)
            pass

        print(np.shape(extinction_profile), np.shape(altitude))

        # use profile over the whole day
        for t in _time:
            norm_noise = self.noise*np.nanmax(extinction_profile) / altitude[-1]**2
            noise_profile = [norm_noise * random.random() * z**2 for z in altitude]
            extinction.append(extinction_profile + noise_profile)

        ds = xr.Dataset(
            data_vars=dict(
                extinction_model=(["time", "altitude"], extinction),
                station_altitude=(0.0),
                station_latitude=(0.0),
                station_longitude=(0.0),
                l0_wavelength=(self.wavelength)
            ),
            coords=dict(time=_time, altitude=altitude),
            attrs=dict(site_location=f"Simulation - [{self.model}]"),
        )
        ds.extinction_model.attrs = {
            "long_name": f"Extinction Coefficient (model) @ {self.wavelength} nm",
            "units": "m-1",
        }
        ds.l0_wavelength.attrs = {
            "units": "nm"
        }
        return ds
    
    def simulate_attenuated_backscatter(self, ds: xr.Dataset):
        """Calculates the attenuated backscatter measurements for given extinction profiles
        
        Args:
            - ds (xr.Dataset): Dataset which contains extinction profiles (`time`, `altitude`)
        
        Returns:
            :class:`xr.Dataset`
        """
        # frequently used variables
        altitude = ds.altitude.data
        time = ds.time.data
        extinction = ds.extinction_model.data
        vertical_resolution = min(np.diff(altitude))

        # open molecular profile
        rayleigh = RayleighData(altitude, self.wavelength, T0=298, P0=1013)

        # attenuated_backscatter calculation
        attenuated_backscatter = []
        for i, t in enumerate(time):
            total_backscatter = rayleigh.backscatter + np.divide(extinction[i,:], self.lidar_ratio)
            total_extinction = rayleigh.extinction + extinction[i]
            optical_depth = np.cumsum(np.asarray(total_extinction) * vertical_resolution)
            transmission = np.exp(-optical_depth)
            attenuated_backscatter.append( [total_backscatter[j] * transmission[j]**2 for j, z in enumerate(altitude)])

        # add attenuated_backscatter as new dataarray
        ds["attenuated_backscatter_0"] = xr.DataArray(
            data=np.multiply(attenuated_backscatter, 1e-6), #conversion from m-1.s-1 to µm-1.sr-1
            dims=["time", "altitude"],
            attrs=dict(long_name=f"Attenuated Backscatter @ {self.wavelength}nm", units='µm-1.sr-1'),
        )
        return ds


def _main():
    simulator = ExtinctionToAttenuatedBackscatter(model="step", wavelength=1064.0, lidar_ratio = 50., noise=0.5)
    sim_profiles = simulator.to_profiles_data()
    sim_profiles.plot('extinction_model')

if __name__ == "__main__":
    _main()
