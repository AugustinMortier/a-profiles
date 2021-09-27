#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Rayleigh Profile

import numpy as np
import math

class Rayleigh:
    """Class for computing a standard rayleigh profile (backscatter and extinction)

    Attributes:
        altitude (array): array of altitude to be used to compute rayleigh profile, in m
        T0 (float): Temperature at ground level, in K
        P0 (float): Pressure at ground level, in hPa
        wavelength (float): Wavelength of rayleigh profile to be computed

    """

    def __init__(self, altitude=None, T0=298, P0=1013, wavelength=1064):
        self.altitude = altitude
        self.T0 = T0
        self.P0 = P0
        self.wavelength = float(wavelength)
        
        #calls functions
        self.standard_atmosphere()
    
    def standard_atmosphere(self):
        """Function that returns Rayleigh backscatter and extinction profiles for a standar atmosphere at a given wavelength.

        Returns:
            self.bmol: Rayleigh backscatter coefficient (km-1.sr-1) at given wavelength for a standard atmosphere.
            self.amol: Rayleigh extinction coefficient (km-1) at given wavelength for a standard atmosphere.
        """        

        #standard values at sea level
        T0 = 298
        P0 = 1013
                
        #standard gradients & parameters
        atmo = {
            'tropo': {
                'zmin': 0,
                'zmax': 13,
                'dTdz': -6.5
            },
            'strato': {
                'zmin': 13,
                'zmax': 55,
                'dTdz': 1.4
            },
            'meso': {
                'zmin': 55,
                'zmax': 100,
                'dTdz': -2.4
            }
        }

        p_He = 8;

        #convert pressure from hPa to Pa
        p_z0 = P0*100;
        #convert altitude to km
        z = self.altitude/1000;

        #vertical resolution
        dz = min(z[1:]-z[0:-1])

        #temperature profile
        Tz = [T0]
        for layer in atmo.keys():
            ibottom = int(np.floor(atmo[layer]['zmin']/dz))
            itop = int(np.floor(atmo[layer]['zmax']/dz))
            for i in range(ibottom,itop):
                Tz.append(Tz[ibottom]+(i-ibottom)*atmo[layer]['dTdz']*dz)

        #vertical coordinates for temperature
        z_Tz = np.arange(0,100,dz)

        #pressure profile
        Pz=p_z0*np.exp(-z_Tz/p_He);

        #Number of molecules
        N_m=np.divide(Pz,(8.314/np.multiply(6.023e23,Tz)));
        #molecular section
        section_m=5.45*np.power(550/self.wavelength,4.09)*1e-32;

        #backscatter profile
        bmol=N_m*section_m;
        #extinction profile
        amol=8.0*math.pi*bmol/3.0;

        #colocate vertically to input altitude
        imin = np.argmin(np.abs(np.array(z_Tz)-z[0]))
        imax = imin+len(z)

        self.bmol = bmol[imin:imax]
        self.amol = amol[imin:imax]
        
        return self

def _main():
    import aprofiles as apro
    import matplotlib.pyplot as plt
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    altitude = profiles.data.altitude.data
    wavelength = profiles.data.l0_wavelength.data

    T0=298; p_z0=1013;
    rayleigh = Rayleigh(altitude,T0,p_z0,wavelength);
    plt.plot(rayleigh.amol,altitude)
    plt.show()
    
if __name__ == '__main__':
    _main()