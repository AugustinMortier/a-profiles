# @author Augustin Mortier
# @desc A-Profiles - Size Distribution

import json

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

from aprofiles import utils


class SizeDistributionData:
    """Class for computing *size distributions* for a given aerosol type.
    This class calls the :func:`get_sd()` method, which calculates VSD and NSD (Volume and Number Size Distributions).

    Attributes:
        - `aer_type` ({'dust', 'volcanic_ash', 'biomass_burning','urban'}): aerosol type.
        - `aer_properties` (dict): dictionnary describing the optical and microphophysical properties of the prescribed aerosol (read from *aer_properties.json*)

    Example:
        >>> # some imports
        >>> import aprofiles as apro
        >>> sd = apro.size_distribution.SizeDistributionData('urban')
        # checkout the instance attributes
        >>> apro.size_distribution.SizeDistributionData('dust').__dict__.keys()
        dict_keys(['aer_type', 'aer_properties', 'radius', 'vsd', 'nsd'])
    """

    def __init__(self, aer_type):
        self.aer_type = aer_type

        # read aer_properties.json files
        f = open(Path(Path(__file__).parent,'config','aer_properties.json'))
        aer_properties = json.load(f)
        f.close()
        # check if the aer_type exist in the json file
        if aer_type not in aer_properties.keys():
            raise ValueError(
                f"{aer_type} not found in aer_properties.json. `aer_type` must be one of the follwowing: {list(aer_properties.keys())}"
            )
        else:
            self.aer_properties = aer_properties[self.aer_type]
            self.get_sd()

    def _vsd_to_nsd(self):
        """Transforms Volume Size Distribution to Number Size Distribution"""
        self.nsd = [
            self.vsd[i] * 3 / (4 * np.pi * self.radius[i] ** 4)
            for i in range(len(self.radius))
        ]
        return self

    def get_sd(self):
        """Returns the Volume and Number Size Distributions arrays from an instance of the :class:`SizeDistributionData` class .

        Returns:
            :class:`SizeDistribData` object with additional attributes.
                - `radius` (:class:`numpy.ndarray`): radius (µm)
                - `vsd` (:class:`numpy.ndarray`): Volume Size Distribution (µm2.µm-3)
                - `nsd` (:class:`numpy.ndarray`): Number Size Distribution (µm-3.µm-1)
        """

        aer_properties = self.aer_properties
        radius = np.arange(1e-2, 2e1, 1e-3)  # radius in µm
        vsd = np.zeros(len(radius))

        # we loop though all the keys defining the different modes
        for mode in aer_properties["vsd"].keys():
            vsd += utils.gaussian(
                np.log(radius),
                np.log(aer_properties["vsd"][mode]["reff"]),
                aer_properties["vsd"][mode]["rstd"],
                aer_properties["vsd"][mode]["conc"],
            )

        self.radius = radius
        self.vsd = vsd
        self._vsd_to_nsd()

        return self

    def plot(self, show_fig=True):
        """Plot Size Distributions of an instance of the :class:`SizeDistributionData` class.

        Example:
            >>> # import aprofiles
            >>> import aprofiles as apro
            >>> # get size distribution for urban particles
            >>> sd = apro.size_distribution.SizeDistribData('urban');
            >>> # plot profile
            >>> sd.plot()

            .. figure:: ../../docs/_static/images/urban_sd.png
                :scale: 80 %
                :alt: urban size distribution

                Size distributions for urban particles.

        """
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))

        # plot Volume Size Distribution in 1st axis
        print(self.vsd)
        ax.plot(self.radius, self.vsd, label="VSD")
        ax.set_ylabel("V(r) (µm2.µm-3)")

        # plot Number Size Distribution in 2nd axis
        if "nsd" in self.__dict__:
            # add secondary yaxis
            ax2 = ax.twinx()
            ax2.plot(self.radius, self.nsd, "orange", label="NSD")
            ax2.set_ylabel("N(r) (µm-3.µm-1)")
            # ax2.set_ylim([0,10])

        ax.set_xlabel("Radius (µm)")
        ax.set_xscale("log")
        fig.legend(
            loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes
        )
        plt.title(
            f"Size Distribution for {self.aer_type.capitalize().replace('_', ' ')} Particles",
            weight="bold",
        )
        plt.tight_layout()
        if show_fig:
            plt.show()


def _main():
    import aprofiles as apro
    sd_data = SizeDistributionData("urban")
    sd_data.plot()


if __name__ == "__main__":
    _main()
