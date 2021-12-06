# @author Augustin Mortier
# @desc A-Profiles - Extinction to Mass Coefficient
import json

import matplotlib.pyplot as plt
import miepython
import numpy as np

from aprofiles import size_distribution


class EMCData:
    """Class for computing the *Extinction to Mass Coefficient* for a given aerosol type.
    This class calls the :func:`get_emc()` method.

    Attributes:
        - `aer_type` ({'dust', 'volcanic_ash', 'biomass_burning', 'urban'}): aerosol type.
        - `wavelength` (int or float): wavelength, in mm.
        - `method` ({'mortier_2013', 'literature'}): method to retrieve or compute `EMC`.
        - `aer_properties` (dict): dictionnary describing the optical and microphophysical properties of the prescribed aerosol (read from *aer_properties.json*)

    Example:
        >>> #some imports
        >>> import aprofiles as apro
        >>> emc_data = EMCData('volcanic_ash', 532.)
        >>> emc_data.__dict__.keys()
        dict_keys(['aer_type', 'wavelength', 'aer_properties', 'nsd', 'vsd', 'radius', 'qext', 'conv_factor', 'emc'])
        >>> print(f'{emc_data.conv_factor:.2e} m {emc_data.emc):.2e} m2.g-1')
        6.21e-07 m 0.62 m2.g-1

    """

    def __init__(self, aer_type: str, wavelength: float, method: str = "mortier_2013"):

        # check parameters type
        if not isinstance(aer_type, str):
            raise TypeError(
                "`aer_type` is expected to be a string. Got {} instead.".format(
                    type(aer_type)
                )
            )
        if not isinstance(wavelength, (int, float)):
            raise TypeError(
                "`wavelength` is expected to be an int or a float. Got {} instead".format(
                    type(wavelength)
                )
            )
        available_methods = ["mortier_2013", "literature"]
        if method not in available_methods:
            raise ValueError(
                "Invalid `method`. AAvailable methods are {}".format(available_methods)
            )

        self.aer_type = aer_type
        self.wavelength = wavelength
        self.method = method

        if self.method == "mortier_2013":
            # read aer_properties.json files
            f = open("aprofiles/config/aer_properties.json")
            aer_properties = json.load(f)
            f.close()
            # check if the aer_type exist in the json file
            if aer_type not in aer_properties.keys():
                raise ValueError(
                    "{} not found in aer_properties.json. `aer_type` must be one of the follwowing: {}".format(
                        aer_type, list(aer_properties.keys())
                    )
                )
            else:
                self.aer_properties = aer_properties[self.aer_type]
                self.get_emc()
        elif self.method == "literature":
            self.emc = 3.33  # CHECK V-PROFILES VALUES. CHECK CODE IN LAPTOP?
            self.conv_factor = -99

    def get_emc(self):
        """Calculates the Extinction to Mass Coefficient for a given type of particles assuming with prescribed size distribution shape (the amplitude is unknown), density, and using the `Mie theory <https://miepython.readthedocs.io>`_ to calculate the extinction efficiency.

        Returns:
            :class:`EMCData` with additional attributes:
                - `nsd` (1D Array): Number Size Distribution
                - `vsd` (1D Array): Volume Size Distribution
                - `radius` (1D Array): Radius, in µm
                - `x` (1D Array): Size parameter (unitless)
                - `conv_factor` (float): Conversion factor, in m
                - `emc` (float): Extinction to Mass Coefficient, in m2.g-1

        .. note::
            For a population of particles, the extinction coefficient :math:`\sigma_{ext}` (m-1) can be written as follwowing:

            :math:`\sigma_{ext} = \int_{r_{min}}^{r_{max}}N(r)Q_{ext}(m,r,\lambda) \pi r^2 dr`

            with :math:`Q_{ext}`, the `extinction efficiency` and :math:`N(r)` the `Number Size Distribution` (NSD).

            :math:`Q_{ext}` varies with the refractive index, :math:`m`, the wavelength, :math:`\lambda` and can be calculated for spherical particles with the Mie therory.

            Total aerosol mass concentration :math:`M_0` (µg.m-3) can be written as:

            :math:`M_0 = \int_{r_{min}}^{r_{max}}{M(r)dr}` where :math:`M(r)` is the mass size distribution (MSD).

            This equation can be written, using the relation between NSD and MSD, as:

            :math:`M_0 = \int_{r_{min}}^{r_{max}}{\\frac{4\pi r^3}{3} \\rho N(r) dr}`

            where :math:`\\rho` is the particles `density` (kg.m-3).

            By normalizing the NSD with respect to the fine mode (:math:`N(r) = N_0 N_1(r)`), the combination of the previous equations leads to:

            :math:`M_0 = \sigma_{ext} \\rho \\frac{4}{3} \\frac{\int_{r_{min}}^{r_{max}} N_1(r) r^3 dr}{\int_{r_{min}}^{r_{max}} N_1(r) Q_{ext}(m,r,\lambda) r^2 dr}`

            By commodity, we define the `conversion factor` (in m) as :math:`c_v = \\frac{4}{3} \\frac{\int_{r_{min}}^{r_{max}} N_1(r) r^3 dr}{\int_{r_{min}}^{r_{max}} N_1(r) Q_{ext}(m,r,\lambda) r^2 dr}`

            so the previous equation can be simplified: :math:`M_0 = \sigma_{ext} \\rho c_v`

            Finally, the `Extinction to Mass Coefficient` (EMC, also called `mass extinction cross section`, usually provided in m2.g-1) is defined as the ratio between :math:`\sigma_{ext}` and :math:`M_0`:

            :math:`EMC = \\frac{\sigma_{ext}}{M_0} = \\frac{1}{\\rho c_v}`

            with :math:`\\rho` being expressed in (g.m-3).

            
            .. table:: Conversion Factors and EMC calculated for the main aerosol types
                :widths: auto

                +-----------------+------------------------+------------------+
                | Aerosol Type    | Conversion Factor (µm) | EMC (m2.g-1)     |
                |                 +-----------+------------+--------+---------+
                |                 | 532 nm    | 1064 nm    | 532 nm | 1064 nm |
                +=================+===========+============+========+=========+
                | Urban           | 0.31      | 1.92       | 1.86   | 0.31    |
                +-----------------+-----------+------------+--------+---------+
                | Desert dust     | 0.68      | 1.04       | 0.58   | 0.38    |
                +-----------------+-----------+------------+--------+---------+
                | Biomass burning | 0.26      | 1.28       | 3.30   | 0.68    |
                +-----------------+-----------+------------+--------+---------+
                | Volcanic ash    | 0.62      | 0.56       | 0.62   | 0.68    |
                +-----------------+-----------+------------+--------+---------+

        """

        def _compute_conv_factor(nsd, qext, radius):
            """Compute Conversion Factor for a given Size Distribution and Efficiency

            Args:
                - nsd (1D Array): Number Size Distribution (µm-3.µm-1)
                - qext (1D Array): Extinction Efficiency (unitless)
                - radius (1D Array): Radius, in µm

            Returns:
                [float]: Conversion factor (m)

            """
            # radius resolution
            dr = min(np.diff(radius))

            # integrals
            numerator = [nsd[i] * (radius[i] ** 3) for i in range(len(radius))]
            denominator = [
                nsd[i] * qext[i] * (radius[i] ** 2) for i in range(len(radius))
            ]
            int1 = np.nancumsum(np.asarray(numerator) * dr)[-1]
            int2 = np.nancumsum(np.asarray(denominator) * dr)[-1]

            conv_factor = (4 / 3) * (int1 / int2)

            # conversion form µm to m
            conv_factor = conv_factor * 1e-6
            return conv_factor

        # generate a size distribution for given aer_type
        sd = size_distribution.SizeDistributionData(self.aer_type)

        # calculate efficiency extinction qext
        # size parameter
        # as the radius is in µm and the wavelength is in nm, one must convert the wavelength to µm
        x = [2 * np.pi * r / (self.wavelength * 1e-3) for r in sd.radius]
        # refractive index
        m = complex(
            self.aer_properties["ref_index"]["real"],
            -abs(self.aer_properties["ref_index"]["imag"]),
        )
        # mie calculation
        qext, _qsca, _qback, _g = miepython.mie(m, x)

        # output
        self.nsd = sd.nsd
        self.vsd = sd.vsd
        self.radius = sd.radius
        self.x = x
        self.qext = qext
        self.conv_factor = _compute_conv_factor(sd.nsd, qext, sd.radius)
        self.emc = 1 / (
            self.conv_factor * self.aer_properties["density"] * 1e6
        )  # convert density from g.cm-3 to g.m-3
        return self

    def plot(self):
        """Plot main information of an instance of the :class:`EMCData` class.

        Example:
            >>> #import aprofiles
            >>> import aprofiles as apro
            >>> #compute emc for biomas burning particles at 532 nm
            >>> emc = apro.emc.EMCData('volcanic_ash', 532.);
            >>> #plot information
            >>> emc.plot()

            .. figure:: ../../docs/_static/images/volcanic_ash-emc.png
                :scale: 80 %
                :alt: volcanic ash properties

                Volcanic Ash particles properties used for EMC calculation.
        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))

        # plot Volume Size Distribution in 1st axis
        ax.plot(self.radius, self.vsd, label="VSD")
        ax.set_ylabel("V(r) (µm2.µm-3)")

        # plot Number Size Distribution in 2nd axis
        if "nsd" in self.__dict__:
            # add secondary yaxis
            ax2 = ax.twinx()
            ax2.plot(self.radius, self.qext, "orange", label="Qext", color="gray")
            ax2.set_ylabel("Qext (unitless)")
            # ax2.set_ylim([0,10])

        # add additional information
        plt.text(
            0.975,
            0.85,
            f"$at\ \lambda={self.wavelength:.0f}\ nm$",
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )
        plt.text(
            0.975,
            0.80,
            f"$c_v: {self.conv_factor * 1e6:.2f}\ \mu m$",
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )
        plt.text(
            0.975,
            0.75,
            f"$EMC: {self.emc:.2f}\ m^2/g$",
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )

        ax.set_xlabel("Radius (µm)")
        ax.set_xscale("log")
        fig.legend(
            loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes
        )
        plt.title(
            f"{self.aer_type.capitalize().replace('_', ' ')} particles properties for EMC calculation",
            weight="bold",
        )
        plt.tight_layout()
        plt.show()


def _main():
    import aprofiles as aprofiles

    emc_data = EMCData("urban", 1064.0)
    print(f"{emc_data.conv_factor:.2e} m {emc_data.emc:.2f} m2.g-1")
    emc_data.plot()


if __name__ == "__main__":
    _main()
