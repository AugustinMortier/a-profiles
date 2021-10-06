#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Rayleigh Profile

import numpy as np
import math

class Rayleigh:
    """Class for computing a standard rayleigh profile (backscatter and extinction)

    Attributes:
        altitude (array): array of altitude ASL to be used to compute the rayleigh profile, in m.
        wavelength (float): Wavelength of the Rayleigh profile to be computed, in nm.
        T0 (float): Temperature at ground level, in K.
        P0 (float): Pressure at ground level, in hPa.
    """

    def __init__(self, altitude, wavelength, T0=298, P0=1013):
        self.altitude = altitude
        self.T0 = T0
        self.P0 = P0
        self.wavelength = float(wavelength)
        
        #calls functions
        self._standard_atmosphere()
    
    def _standard_atmosphere(self):
        """Function that returns Rayleigh backscatter and extinction profiles for a standar atmosphere at a given wavelength.

        Returns:
            self.backscatter: Rayleigh backscatter coefficient (m-1.sr-1) at given wavelength for a standard atmosphere.
            self.extinction: Rayleigh extinction coefficient (m-1) at given wavelength for a standard atmosphere.
        """

        def _refi_air(wavelength):
            """Function that calculates the refractive index of the air at a given wavelength in a standard atmosphere.
            This is adapted from Peek and Reeder, 1972.

            Args:
                wavelength (float): wavelength, in µm.

            Returns:
                refractive index of the air.
            """            
            #wav (float): wavelength in µm
            #returns refractive index of the air in standard atmosphere (Peck and Reeder)
            var = 8060.51 + 2480990/(132.274-wavelength**-2) + 17455.7/(39.32957-wavelength**-2)
            return var*1e-8+1

        #standard values at sea level
        T0 = 298 #K
        P0 = 1013 *1e2 #Pa
        p_He = 8;
                
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

        #convert altitude to km
        z = self.altitude/1000

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
        Pz=P0*np.exp(-z_Tz/p_He);

        #molecules density and cross section
        Ns = (6.02214e23/22.4141)/1000 #molecules.cm-3
        #density (cm-3)
        N_m = [Ns * (T0/P0)* (Pz[i]/Tz[i]) for i in range(len(Pz))]

        #cross section, in cm-2 (adapted from Bodhaine et al., 1999)
        king_factor = 1.05 #tomasi et al., 2005
        num = 24*(math.pi**3)*((_refi_air(self.wavelength*1e-3)**2-1)**2)
        denum = ((self.wavelength*1e-7)**4)*(Ns**2)*((_refi_air(self.wavelength*1e-3)**2+2)**2)
        section_m = (num/denum)*king_factor

        #extinction profile
        amol = N_m*np.array(section_m)
        #backscatter profile
        lr_mol = 8*math.pi/3;
        bmol = amol / lr_mol

        #colocate vertically to input altitude
        imin = np.argmin(np.abs(np.array(z_Tz)-z[0]))
        imax = imin+len(z)

        #output
        self.cross_section = section_m # in cm-2
        self.backscatter = bmol[imin:imax]*1e2 #from cm-1 to m-1
        self.extinction = amol[imin:imax]*1e2 # from cm-1 to m-1
        
        return self

def _main():
    import aprofiles as apro
    import matplotlib.pyplot as plt
    
    #path = "examples/data/L2_0-20000-006735_A20210908.nc"
    path = "examples/data/L2_0-20000-001492_A20210909.nc"
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    altitude = profiles.data.altitude.data
    wavelength = profiles.data.l0_wavelength.data

    rayleigh = Rayleigh(altitude,wavelength);

    #plot
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    plt.plot(rayleigh.extinction,altitude)
    plt.text(0.95, 0.94, r'$\sigma_m: {:.2e} cm-2$'.format(rayleigh.cross_section), horizontalalignment='right', verticalalignment='center', transform=ax.transAxes)
    plt.title('Rayleigh Profile in a Standard Atmosphere ({}hPa, {}K)'.format(rayleigh.P0, rayleigh.T0), weight='bold')
    plt.xlabel('Extinction coefficient @ {}nm (m-1)'.format(rayleigh.wavelength))
    plt.ylabel('Altitude ASL (m)')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    _main()