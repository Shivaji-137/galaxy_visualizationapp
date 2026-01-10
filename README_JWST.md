# JWST Data Fetcher Module

## Overview

The JWST data fetcher is a **standalone module** (`jwst_fetcher.py`) designed parallel to the HST fetcher, providing complete access to James Webb Space Telescope observations through MAST.

## Module Structure

```
data_fetchers/
├── hst_fetcher.py      ← HST observations (separate)
├── jwst_fetcher.py     ← JWST observations (NEW, standalone)
├── gaia_fetcher.py     ← Gaia DR3
├── sdss_fetcher.py     ← SDSS
├── panstarrs_fetcher.py← Pan-STARRS
├── twomass_fetcher.py  ← 2MASS
├── eso_fetcher.py      ← ESO Archive
├── desi_fetcher.py     ← DESI
└── __init__.py         ← Exports all modules
```

## Features

### Core Functions (9)

1. **`fetch_jwst_observations(ra, dec, radius, ...)`**
   - Query JWST observations by sky coordinates
   - Filter by instrument (NIRCAM, MIRI, etc.)
   - Filter by specific filters (F277W, F200W, etc.)
   - Filter by proposal ID

2. **`get_jwst_preview_images(ra, dec, radius, ...)`**
   - Get preview images with download URLs
   - Returns list of dicts with metadata
   - Supports instrument filtering

3. **`query_jwst_by_proposal(proposal_id, ...)`**
   - Query by JWST proposal ID
   - Filter by instrument and filter
   - Useful for retrieving specific programs

4. **`get_jwst_instruments_info()`**
   - Get detailed specs for all JWST instruments
   - Returns wavelength ranges, FOV, pixel scales
   - Includes filter information

5. **`get_jwst_preview_from_obs_id(obs_id)`**
   - Get previews for specific observation ID
   - Returns preview URLs and metadata

6. **`list_jwst_instruments()`**
   - List all available instruments
   - Returns: ['NIRCAM', 'NIRSPEC', 'MIRI', 'NIRISS', 'FGS']

7. **`get_jwst_filters(instrument)`**
   - Get all filters for specific instrument
   - Example: `get_jwst_filters('NIRCAM')` returns 15+ filters

8. **`get_jwst_famous_targets()`**
   - Get coordinates of famous JWST targets
   - Includes Cartwheel Galaxy, Stephan's Quintet, etc.
   - Returns dict mapping names to (RA, Dec)

9. **`download_jwst_image(preview_url, save_path)`**
   - Download preview images from URLs
   - Save to file or return PIL Image object

## Quick Start

### Basic Import

```python
from data_fetchers.jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images,
    get_jwst_famous_targets
)
```

### Example 1: Query by Coordinates

```python
# Query Cartwheel Galaxy
df = fetch_jwst_observations(
    ra=9.4333,
    dec=-33.7128,
    radius=60.0,
    instrument='NIRCAM',
    filters='F277W'
)

print(f"Found {len(df)} observations")
```

### Example 2: Use Famous Targets

```python
# Get famous target coordinates
targets = get_jwst_famous_targets()
coords = targets['Cartwheel Galaxy']

# Query the target
df = fetch_jwst_observations(
    ra=coords[0],
    dec=coords[1],
    radius=60.0
)
```

### Example 3: Get Preview Images

```python
images = get_jwst_preview_images(
    ra=9.4333,
    dec=-33.7128,
    radius=60.0,
    max_images=5,
    instrument='NIRCAM'
)

for img in images:
    print(f"Obs ID: {img['obs_id']}")
    print(f"Instrument: {img['instrument']}")
    print(f"Filters: {img['filters']}")
    print(f"Preview URLs: {len(img['preview_urls'])}")
```

### Example 4: Query by Proposal ID

```python
# Query JWST ERO proposal 2727 (Cartwheel Galaxy)
df = query_jwst_by_proposal(
    proposal_id='2727',
    instrument='NIRCAM',
    filters='F277W'
)

print(f"Found {len(df)} observations")
```

## JWST Instruments

| Instrument | Type | Wavelength | Key Features |
|------------|------|------------|--------------|
| **NIRCAM** | Imager | 0.6-5.0 μm | Primary near-IR camera, 15+ filters |
| **NIRSPEC** | Spectrograph | 0.6-5.3 μm | Multi-object, IFU, fixed slit modes |
| **MIRI** | Imager/Spec | 5-28 μm | Mid-IR imaging & spectroscopy, 9 filters |
| **NIRISS** | Imager/Spec | 0.8-5.0 μm | Wide-field slitless spectroscopy, 12 filters |
| **FGS** | Guider | 0.6-5.0 μm | Precision pointing |

## Famous JWST Targets

The module includes a built-in database of famous JWST targets:

1. **Cartwheel Galaxy** (RA: 9.4333°, Dec: -33.7128°)
2. **Stephan's Quintet** (RA: 339.0129°, Dec: 33.9589°)
3. **Carina Nebula** (RA: 161.265°, Dec: -59.866°)
4. **Southern Ring Nebula** (RA: 151.761°, Dec: -40.444°)
5. **SMACS 0723 Deep Field** (RA: 110.841°, Dec: -73.453°)
6. **Tarantula Nebula** (RA: 84.678°, Dec: -69.103°)
7. **NGC 628 / Phantom Galaxy** (RA: 24.1739°, Dec: 15.7839°)
8. **NGC 7496** (RA: 348.3542°, Dec: -43.4269°)

## Filter Information

### NIRCam Filters
**Short wavelength:** F070W, F090W, F115W, F150W, F200W  
**Long wavelength:** F277W, F356W, F444W  
**Medium band:** F140M, F162M, F182M, F210M  
**Narrow band:** F164N, F187N, F212N

### MIRI Filters
F560W, F770W, F1000W, F1130W, F1280W, F1500W, F1800W, F2100W, F2550W

### NIRISS Filters
F090W, F115W, F140M, F150W, F158M, F200W, F277W, F356W, F380M, F430M, F444W, F480M

## Comparison: HST vs JWST

Both modules follow the same design pattern but are completely independent:

```python
# HST observations
from data_fetchers.hst_fetcher import fetch_hst_observations
hst_df = fetch_hst_observations(ra=24.1739, dec=15.7839, radius=60)

# JWST observations
from data_fetchers.jwst_fetcher import fetch_jwst_observations
jwst_df = fetch_jwst_observations(ra=24.1739, dec=15.7839, radius=60)

# Compare
print(f"HST: {len(hst_df)} observations")
print(f"JWST: {len(jwst_df)} observations")
```

## Testing

### Run Test Suite
```bash
python test_jwst.py
```

Tests include:
- ✓ Instrument information (offline)
- ✓ Query by proposal ID
- ✓ Query by coordinates
- ✓ Fetch preview images
- ✓ Famous targets and filters

### Run Examples
```bash
python examples_jwst_usage.py
```

Examples demonstrate:
1. Query by coordinates (Cartwheel Galaxy)
2. Query by proposal ID (ERO Proposal 2727)
3. Get preview images (Stephan's Quintet)
4. Use famous targets and filters

## Documentation

- **`JWST_GUIDE.md`** - Complete user guide with all functions
- **`JWST_INTEGRATION_SUMMARY.md`** - Technical integration details
- **`README_JWST.md`** - This file

## Integration with Streamlit App

To add JWST data to your Streamlit pages:

```python
import streamlit as st
from data_fetchers.jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images
)

# Add JWST section
st.header("🛰️ JWST Observations")

# Query JWST
jwst_df = fetch_jwst_observations(ra, dec, radius=60)

if jwst_df is not None:
    st.write(f"Found {len(jwst_df)} JWST observations")
    st.dataframe(jwst_df)
    
    # Show preview images
    images = get_jwst_preview_images(ra, dec, radius=60)
    if images:
        for img in images:
            st.image(img['preview_urls'][0])
```

## Requirements

No new dependencies! Uses existing packages:
- `astroquery` (already installed)
- `astropy` (already installed)
- `pandas` (already installed)
- `numpy` (already installed)
- `PIL` (already installed)

## Resources

- **MAST JWST Archive:** https://mast.stsci.edu/
- **JWST Science:** https://jwst.nasa.gov/
- **Astroquery Docs:** https://astroquery.readthedocs.io/
- **JWST Proposals:** https://www.stsci.edu/jwst/science-execution/approved-programs

## Support

For issues with the JWST module:
1. Check internet connection to MAST
2. Verify coordinates/proposal IDs are correct
3. Ensure instrument/filter names are uppercase
4. Increase timeout for slow connections

For MAST/JWST data issues:
- Email: archive@stsci.edu
- MAST Help Desk: https://stsci.service-now.com/mast

## Version

**Version:** 1.0.0  
**Date:** January 10, 2026  
**Status:** ✅ Production Ready

## License

Same as main project license.

---

**Happy JWST Data Exploring! 🚀🔭**
