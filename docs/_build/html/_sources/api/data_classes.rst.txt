Data Classes
============

ProfilesData
------------

The :class:`aprofiles.profiles.ProfilesData` class contains profiles data information. Most of the information can be found in the data attribute, which is a :class:`xarray.Dataset`.
Detection and retrieval methods might add information as additional :class:`xarray.DataArray`.

.. automodule:: aprofiles.profiles
   :members:
   :undoc-members:

Aeronet
-------
Not implemented yet.

.. automodule:: aprofiles.aeronet
   :members:
   :undoc-members:


Rayleigh
--------

The :class:`aprofiles.rayleigh.RayleighData` class is used for producing Rayleigh profiles in a standard atmosphere.

.. automodule:: aprofiles.rayleigh
   :members:
   :undoc-members:

Size Distribution
-----------------

The size distribution module is used to produce volume and number size distribution of a population of particles for a given type.
The values describing the size distribution for the different aerosol types are taken from the literature:

* `dust`, `biomass_burning`, and `urban` aerosols [#]_ 
* `volcanic_ash` [#]_

.. [#] Dubovik, O., Holben, B., Eck, T. F., Smirnov, A., Kaufman, Y. J., King, M. D., ... & Slutsker, I. (2002). Variability of absorption and optical properties of key aerosol types observed in worldwide locations. Journal of the atmospheric sciences, 59(3), 590-608.
.. [#] Mortier, A., Goloub, P., Podvin, T., Deroo, C., Chaikovsky, A., Ajtai, N., ... & Derimian, Y. (2013). Detection and characterization of volcanic ash plumes over Lille during the Eyjafjallajökull eruption. Atmospheric Chemistry and Physics, 13(7), 3705-3720.

Aerosol properties are defined in :download:`../../aprofiles/config/aer_properties.json`

.. automodule:: aprofiles.size_distribution
   :members:
   :undoc-members:

Extinction to Mass Coefficient
------------------------------

The :class:`aprofiles.emc.EMCData` class is used for computing an `Extinction to Mass Coefficient` for a given aerosol type.

.. automodule:: aprofiles.emc
   :members:
   :undoc-members:
