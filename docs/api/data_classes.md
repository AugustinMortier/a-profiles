---
title: Data Classes
---

ProfilesData
============

The (aprofiles.profiles.ProfilesData):
class contains profiles data information. Most of the information can be
found in the [data]{.title-ref} attribute, which is a
(xarray.Dataset):. Detection and
retrieval methods might add information as :additional
(xarray.DataArray):).

::: aprofiles.profiles

Aeronet
=======

Not implemented yet.

::: aprofiles.aeronet

Rayleigh
========

The (aprofiles.rayleigh.RayleighData):
class is used for producing Rayleigh profiles in a standard atmosphere.

::: aprofiles.rayleigh

Size Distribution
=================

The size distribution module is used to produce volume and number size
distribution of a population of particles for a given type. The values
describing the size distribution for the different aerosol types are
taken from the literature:

-   `dust`, `biomass_burning`, and `urban` aerosols[^1]
-   `volcanic_ash`[^2]

Aerosol properties are defined in
[`config/aer_properties.json`](../../aprofiles/config/aer_properties.json){: .title-ref role="download"}


::: aprofiles.size_distribution

Extinction to Mass Coefficient
==============================

The (aprofiles.emc.EMCData): class is
used for computing an [Extinction to Mass Coefficient]{.title-ref} for a
given aerosol type.

::: aprofiles.emc

[^1]: Dubovik, O., Holben, B., Eck, T. F., Smirnov, A., Kaufman, Y. J.,
    King, M. D., \... & Slutsker, I. (2002). Variability of absorption
    and optical properties of key aerosol types observed in worldwide
    locations. Journal of the atmospheric sciences, 59(3), 590-608.

[^2]: Mortier, A., Goloub, P., Podvin, T., Deroo, C., Chaikovsky, A.,
    Ajtai, N., \... & Derimian, Y. (2013). Detection and
    characterization of volcanic ash plumes over Lille during the
    Eyjafjallajökull eruption. Atmospheric Chemistry and Physics, 13(7),
    3705-3720.
