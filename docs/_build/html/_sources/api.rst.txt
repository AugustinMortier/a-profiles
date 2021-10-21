API
======================================

Documentation of the core API of aprofiles.

Reader
------

.. automodule:: aprofiles.reader
   :inherited-members:
   :members:
   :undoc-members:

Data Classes
------------

ProfilesData
^^^^^^^^^^^^
.. automodule:: aprofiles.profiles
   :members:
   :undoc-members:

Aeronet
^^^^^^^
.. automodule:: aprofiles.aeronet
   :members:
   :undoc-members:

Rayleigh
^^^^^^^^
.. automodule:: aprofiles.rayleigh
   :members:
   :undoc-members:

Size Distribution
^^^^^^^^^^^^^^^^^

The size distribution module reads an entry file to generate volume and number size distribution of a population of particles for a given type.
The values describing the size distribution are taken from the literature:

* `dust`, `biomass_burning`, and `urban` aerosols [#]_ 
* `volcanic_ash` [#]_

.. [#] Dubovik, O., Holben, B., Eck, T. F., Smirnov, A., Kaufman, Y. J., King, M. D., ... & Slutsker, I. (2002). Variability of absorption and optical properties of key aerosol types observed in worldwide locations. Journal of the atmospheric sciences, 59(3), 590-608.
.. [#] Mortier, A., Goloub, P., Podvin, T., Deroo, C., Chaikovsky, A., Ajtai, N., ... & Derimian, Y. (2013). Detection and characterization of volcanic ash plumes over Lille during the Eyjafjallajökull eruption. Atmospheric Chemistry and Physics, 13(7), 3705-3720.

Aerosol properties are defined in :download:`../aprofiles/config/aer_properties.json`

.. automodule:: aprofiles.size_distribution
   :members:
   :undoc-members:

Extinction to Mass Coefficient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: aprofiles.emc
   :members:
   :undoc-members:


Detection
------------

The following functions are methods from the class :class:`aprofiles.profiles.ProfilesData`.

Fog or Condensation
^^^^^^^^^^^^^^^^^^^
.. automodule:: aprofiles.detection.foc
   :members:
   :undoc-members:

Clouds
^^^^^^
.. automodule:: aprofiles.detection.clouds
   :members:
   :undoc-members:

Planetary Boundary Layer
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: aprofiles.detection.pbl
   :members:
   :undoc-members:

Retrieval
------------

The following functions are methods from the class :class:`aprofiles.profiles.ProfilesData`.

Aerosol Extinction
^^^^^^^^^^^^^^^^^^^
.. automodule:: aprofiles.retrieval.extinction
   :members:
   :undoc-members:

Plotting
------------

Image
^^^^^^^^^^^^

.. automodule:: aprofiles.plot.image
   :members:
   :undoc-members:

Profile
^^^^^^^^^^^^

.. automodule:: aprofiles.plot.profile
   :members:
   :undoc-members:

Time Series
^^^^^^^^^^^^

.. automodule:: aprofiles.plot.timeseries
   :members:
   :undoc-members: