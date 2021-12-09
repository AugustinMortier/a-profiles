# @author Augustin Mortier
# @desc A-Profiles Rayleigh Profile

import matplotlib.pyplot as plt
import numpy as np


class RayleighData:
    """Class for computing *rayleigh profile* in a standard atmosphere.
    This class calls the :func:`get_optics_in_std_atmo()` method, which produces profiles of `backscatter` and `extinction` coefficients.

    Attributes:
        - altitude (array-like): array of altitude ASL to be used to compute the rayleigh profile, in m.
        - wavelength (float): Wavelength of the Rayleigh profile to be computed, in nm.
        - T0 (float): Temperature at ground level, in K.
        - P0 (float): Pressure at ground level, in hPa.

    Example:
        >>> # some imports
        >>> import aprofiles as apro
        >>> import numpy as np
        >>> # creates altitude array
        >>> altitude = np.arange(15,15000,15)
        >>> wavelength = 1064.
        >>> # produce rayleigh profile
        >>> rayleigh = apro.rayleigh.RayleighData(altitude, wavelength, T0=298, P0=1013);
        # checkout the instance attributes
        >>> rayleigh.__dict__.keys()
        dict_keys(['altitude', 'T0', 'P0', 'wavelength', 'cross_section', 'backscatter', 'extinction'])
    """

    def __init__(self, altitude: list, wavelength: float, T0=298, P0=1013):
        self.altitude = altitude
        self.T0 = T0
        self.P0 = P0
        self.wavelength = wavelength

        # calls functions
        self.get_optics_in_std_atmo()

    def get_optics_in_std_atmo(self):
        """Function that returns *backscatter* and *extinction* profiles [#]_ for an instance of a :class:`RayleighData` class.

        .. [#] Bucholtz, A. (1995). Rayleigh-scattering calculations for the terrestrial atmosphere. Applied optics, 34(15), 2765-2773.

        Returns:
            :class:`aprofiles.rayleigh.RayleighData` object with additional attributes.
                - `extinction` (:class:`numpy.ndarray`): extinction coefficient (m-1)
                - `backscatter` (:class:`numpy.ndarray`): backscatter coefficient (m-1.sr-1)
                - `cross_section` (:class:`numpy.ndarray`): cross section (cm-2)
        """

        def _refi_air(wavelength):
            """Function that calculates the refractive index of the air at a given wavelength in a standard atmosphere [#]_.

            .. [#] Peck, E. R., & Reeder, K. (1972). Dispersion of air. JOSA, 62(8), 958-962.

            Args:
                wavelength (float): wavelength, in µm.

            Returns:
                refractive index of the air.
            """
            # wav (float): wavelength in µm
            # returns refractive index of the air in standard atmosphere (Peck and Reeder)
            var = (
                8060.51
                + 2480990 / (132.274 - wavelength ** -2)
                + 17455.7 / (39.32957 - wavelength ** -2)
            )
            return var * 1e-8 + 1

        # standard values at sea level
        T0 = 298  # K
        P0 = 1013 * 1e2  # Pa
        p_He = 8

        # standard gradients & parameters
        atmo = {
            "tropo": {"zmin": 0, "zmax": 13, "dTdz": -6.5},
            "strato": {"zmin": 13, "zmax": 55, "dTdz": 1.4},
            "meso": {"zmin": 55, "zmax": 100, "dTdz": -2.4},
        }

        # convert altitude to km
        z = self.altitude / 1000

        # vertical resolution
        dz = min(z[1:] - z[0:-1])

        # temperature profile
        Tz = [T0]
        for layer in atmo.keys():
            ibottom = int(np.floor(atmo[layer]["zmin"] / dz))
            itop = int(np.floor(atmo[layer]["zmax"] / dz))
            for i in range(ibottom, itop):
                Tz.append(Tz[ibottom] + (i - ibottom) * atmo[layer]["dTdz"] * dz)

        # vertical coordinates for temperature
        z_Tz = np.arange(0, 100, dz)

        # pressure profile
        Pz = P0 * np.exp(-z_Tz / p_He)

        # molecules density and cross section
        Ns = (6.02214e23 / 22.4141) / 1000  # molecules.cm-3
        # density (cm-3)
        N_m = [Ns * (T0 / P0) * (Pz[i] / Tz[i]) for i in range(len(Pz))]

        # cross section, in cm2 (adapted from Bodhaine et al., 1999)
        king_factor = 1.05  # tomasi et al., 2005
        num = 24 * (np.pi ** 3) * ((_refi_air(self.wavelength * 1e-3) ** 2 - 1) ** 2)
        denum = (
            ((self.wavelength * 1e-7) ** 4)
            * (Ns ** 2)
            * ((_refi_air(self.wavelength * 1e-3) ** 2 + 2) ** 2)
        )
        section_m = (num / denum) * king_factor

        # extinction profile
        amol = N_m * np.array(section_m)
        # backscatter profile
        lr_mol = 8 * np.pi / 3
        bmol = amol / lr_mol

        # colocate vertically to input altitude
        imin = np.argmin(np.abs(np.array(z_Tz) - z[0]))
        imax = imin + len(z)

        # output
        self.cross_section = section_m  # in cm2
        self.backscatter = bmol[imin:imax] * 1e2  # from cm-1 to m-1
        self.extinction = amol[imin:imax] * 1e2  # from cm-1 to m-1
        self.tau = np.cumsum(self.extinction*(dz*1000))[-1]

        return self

    def plot(self):
        """Plot extinction profile of an instance of the :class:`RayleighData` class.

        Example:
            >>> # some imports
            >>> import aprofiles as apro
            >>> import numpy as np
            >>> # creates altitude array
            >>> altitude = np.arange(15,15000,15)
            >>> wavelength = 1064.
            >>> # produce rayleigh profile
            >>> rayleigh = apro.rayleigh.RayleighData(altitude, wavelength, T0=298, P0=1013);
            >>> # plot profile
            >>> rayleigh.plot()

            .. figure:: ../../docs/_static/images/rayleigh.png
                :scale: 80 %
                :alt: rayleigh profile

                Rayleigh extinction profile for a standard atmosphere.
        """

        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        plt.plot(self.extinction, self.altitude)
        plt.text(
            0.97,
            0.94,
            f"$\sigma_m: {self.cross_section:.2e} cm2$",
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )
        plt.text(
            0.97,
            0.88,
            f"$\u03C4_m: {self.tau:.2e}$",
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )
        
        plt.title(
            f"Rayleigh Profile in a Standard Atmosphere ({self.P0}hPa, {self.T0}K)",
            weight="bold",
        )
        plt.xlabel(f"Extinction coefficient @ {self.wavelength} nm (m-1)")
        plt.ylabel("Altitude ASL (m)")
        plt.tight_layout()
        plt.show()


def _main():
    import aprofiles as apro

    altitude = np.arange(15, 15000, 15)
    wavelength = 1064.0
    rayleigh = RayleighData(altitude, wavelength)
    # plot
    rayleigh.plot()


if __name__ == "__main__":
    _main()
