# Data Classes

:material-database:{ style="text-align: center; font-size: xx-large; display: block" }

## ProfilesData

The [`ProfilesData`](#profilesdata) class contains profile data information. Most of the information can be found in the `data` attribute, which is an [`xarray.Dataset`](https://xarray.pydata.org/en/stable/generated/xarray.Dataset.html). Detection and retrieval methods might add information as additional [`xarray.DataArray`](https://xarray.pydata.org/en/stable/generated/xarray.DataArray.html).

::: aprofiles.profiles

## Aeronet

Not implemented yet.

::: aprofiles.aeronet

## Rayleigh

The [`RayleighData`](#rayleighdata) class is used for producing Rayleigh profiles in a standard atmosphere.

::: aprofiles.rayleigh

## Size Distribution

The size distribution module is used to produce volume and number size distributions of a population of particles for a given type. The values describing the size distribution for different aerosol types are taken from the literature:

- `dust`, `biomass_burning`, and `urban` aerosols[^1]
- `volcanic_ash`[^2]

Aerosol properties are defined in [`config/aer_properties.json`](../../aprofiles/config/aer_properties.json){: .title-ref role="download"}

::: aprofiles.size_distribution

## Mass to Extinction Coefficient

The [`MECData`](#mecdata) class is used for computing a *Mass to Extinction Coefficient* for a given aerosol type.

::: aprofiles.mec

[^1]: Dubovik, O., Holben, B., Eck, T. F., Smirnov, A., Kaufman, Y. J., King, M. D., ... & Slutsker, I. (2002). Variability of absorption and optical properties of key aerosol types observed in worldwide locations. *Journal of the Atmospheric Sciences*, 59(3), 590-608.

[^2]: Mortier, A., Goloub, P., Podvin, T., Deroo, C., Chaikovsky, A., Ajtai, N., ... & Derimian, Y. (2013). Detection and characterization of volcanic ash plumes over Lille during the Eyjafjallajökull eruption. *Atmospheric Chemistry and Physics*, 13(7), 3705-3720.
