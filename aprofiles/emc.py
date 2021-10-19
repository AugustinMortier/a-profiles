#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Extinction to Mass Coefficient
import json

import miepython
import numpy as np
from tqdm import tqdm

import aprofiles as apro
from aprofiles import size_distribution
import matplotlib.pyplot as plt


class EMCData:
    """Class for computing *Extinction to Mass Coefficient* for a given aerosol type.
    This class calls the :func:`get_emc()` method.

    Attributes:
        - `aer_type` ({'dust','volcanic_ash','biomass_burning','urban'}): aerosol type.
        - `wavelength` (float): wavelength, in m.
        - `aer_properties` (dict): dictionnary describing the optical and microphophysical properties of the prescribed aerosol (read from *aer_properties.json*)
    
    Example:
        >>> #some imports
        >>> import aprofiles as apro
        >>> emc_data = EMCData('volcanic_ash', 1064-9)
        >>> print(emc_data.emc)
        blabla
    """

    def __init__(self, aer_type, wavelength):
        self.aer_type = aer_type
        self.wavelength = wavelength

        #read aer_properties.json files
        f = open('aprofiles/config/aer_properties.json')
        aer_properties = json.load(f)
        f.close()
        #check if the aer_type exist in the json file
        if not aer_type in aer_properties.keys():
            raise ValueError('{} not found in aer_properties.json. `aer_type` must be one of the follwowing: {}'.format(aer_type, list(aer_properties.keys())))
        else:
            self.aer_properties = aer_properties[self.aer_type]
            self.get_emc()



    def get_emc(self):
        """Calculates the Extinction to Mass Coefficient for a given type of particles assuming with prescribed VSD, density, and using the `Mie theory <https://miepython.readthedocs.io>`_ to calculate the extinction efficiency.

        Returns:
            :class:`EMCData` with additionnal attributes:
                - `vsd` (1D Array): Volume Size Distribution
                - `radius` (1D Array): Radius, in µm
                - `emc` (float): Extinction to Mass Coefficient (m2.g-1)
        
        .. note::
            For a population of particles, the extinction coefficient :math:`\sigma_{ext}` can be written as follwowing
            
            :math:`\sigma_{ext} = \int_{r_{min}}^{r_{max}}N(r)Q_{ext}(m,r,\lambda) \pi r^2 dr`

            And the total aerosol concentration :math:`M_0` can be written as
            
            :math:`M_0 = \int_{r_{min}}^{r_{max}}{M(r)dr}`

            where :math:`M(r)` is the Mass distribution.
            
            With respect to Mass and Number distributions relation, one can write

            :math:`M_0 = \int_{r_{min}}^{r_{max}}{\\frac{4\pi r^3}{3} \\rho N(r) dr}`

            where :math:`rho` is the particles `density` (kg.m-3) and :math:`N(r)` the `Number Size Distribution`.
            
            By normalizing the Number Size Distribution on the fine mode (:math:`N(r) = N_0 N_1(r)`), the combination of the previous equations leads to
            
            :math:`M_0 = \sigma_{ext} \\rho c_v`

            where the `conversion factor` (m) equals to
        
            :math:`c_v = \\frac{4\int_{r_{min}}^{r_{max}} N_1(r) r^3 dr}{3\int_{r_{min}}^{r_{max}} N_1(r) Q_{ext}(m,r,\lambda) r^2 dr}`

            Finally, we define the `Extinction to Mass Coefficient (EMC, in m2/g)` as the ratio between the total `extinction` and `mass`:
            :math:`EMC = \\frac{\sigma_{ext}}{M_0} = \\frac{1}{\\rho c_v}`

        """

        def _compute_conv_factor(nsd, qext, radius):
            """Compute Conversion Factor for a given Size Distribution and Efficiency

            Args:
                - nsd (1D Array): Number Size Distribution
                - qext (1D Array): Extinction Efficiency (unitless)
                - radius (1D Array): Radius, in m

            Returns:
                [float]: Conversion factor (m)

            """            
            #radius step
            dr = min(np.diff(radius))

            #integrals
            numerator = [nsd[i]*(radius[i]**3) for i in range(len(radius))]
            denominator = [nsd[i]*qext[i]*(radius[i]**2) for i in range(len(radius))]
            int1 = np.cumsum(np.multiply(numerator,dr))[-1]
            int2 = np.cumsum(np.multiply(denominator,dr))[-1]
            
            conv_factor = (4/3)*(int1/int2)
            return conv_factor

        sd = apro.size_distribution.SizeDistributionData(self.aer_type)

        #compute emc
        nsd = sd.nsd
        radius = sd.radius*1E-6 #from µm to m

        #size parameter
        x = 2*np.pi*radius/self.wavelength
        #refractive index
        m = complex(self.aer_properties['ref_index']['real'],self.aer_properties['ref_index']['imag'])
        #mie calculation
        qext, _qsca, _qback, _g = miepython.mie(m, x)

        #output
        self.nsd = nsd
        self.radius = radius
        self.qext = qext
        self.conv_factor = _compute_conv_factor(nsd, qext, radius)
        emc = self.conv_factor * self.aer_properties['density']
        self.emc = emc*1e-3 #conversion from m2.kg-1 to m2.g-1
        return self
    

def _main():
    import aprofiles as apro
    emc_data = EMCData('volcanic_ash', 532E-9)
    print('{} m {} m2.g-1'.format(emc_data.conv_factor, emc_data.emc))

    #fig, ax = plt.subplots(1,1, figsize=(6,6))
    #plt.plot(emc_data.radius, emc_data.qext)
    #plt.show()

if __name__ == '__main__':
    _main()
