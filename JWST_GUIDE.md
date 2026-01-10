# JWST Data Fetcher - Quick Guide

## Overview

The JWST data fetcher (`jwst_fetcher.py`) provides easy access to James Webb Space Telescope observations through the MAST (Mikulski Archive for Space Telescopes) archive. It's a standalone module similar to the HST fetcher, supporting querying by coordinates, proposal ID, instrument, and filter.

## Quick Start

### 1. Basic Import

```python
from data_fetchers.jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images,
    query_jwst_by_proposal,
    get_jwst_instruments_info,
    get_jwst_famous_targets
)
```

### 2. Query by Coordinates

```python
# Example: Cartwheel Galaxy
ra = 9.4333    # degrees
dec = -33.7128  # degrees
radius = 60.0   # arcseconds

# Get all JWST observations
df = fetch_jwst_observations(ra, dec, radius=radius)

# Filter by instrument
df_nircam = fetch_jwst_observations(
    ra, dec, 
    radius=radius,
    instrument='NIRCAM'
)

# Filter by instrument and filter
df_filtered = fetch_jwst_observations(
    ra, dec,
    radius=radius,
    instrument='NIRCAM',
    filters='F277W'
)
```

### 3. Query by Proposal ID

```python
# Example: JWST Early Release Observations
proposal_id = "2727"

# Get all observations from this proposal
df = query_jwst_by_proposal(proposal_id)

# Filter by instrument
df = query_jwst_by_proposal(
    proposal_id,
    instrument='NIRCAM',
    max_results=20
)
```

### 4. Get Preview Images

```python
# Get preview images with URLs
images = get_jwst_preview_images(
    ra=9.4333,
    dec=-33.7128,
    radius=60.0,
    max_images=5,
    instrument='NIRCAM'
)

# Access image information
for img in images:
    print(f"Obs ID: {img['obs_id']}")
    print(f"Instrument: {img['instrument']}")
    print(f"Filters: {img['filters']}")
    print(f"Preview URLs: {img['preview_urls']}")
```

### 5. Compare HST and JWST

```python
# JWST has its own dedicated module now!
from data_fetchers.jwst_fetcher import fetch_jwst_observations
from data_fetchers.hst_fetcher import fetch_hst_observations

# Query JWST
jwst_df = fetch_jwst_observations(
    ra=24.1739,
    dec=15.7839,
    radius=120.0
)

# Query HST
hst_df = fetch_hst_observations(
    ra=24.1739,
    dec=15.7839,
    radius=120.0
)

# Compare
if jwst_df is not None:
    print(f"JWST images: {len(jwst_df)}")
if hst_df is not None:
    print(f"HST images: {len(hst_df)}")
```

### 6. Use Famous Targets

```python
from data_fetchers.jwst_fetcher import get_jwst_famous_targets

# Get coordinates of famous JWST targets
targets = get_jwst_famous_targets()

# Query Cartwheel Galaxy
coords = targets['Cartwheel Galaxy']
df = fetch_jwst_observations(coords[0], coords[1], radius=60.0)
```

### 7. Get Available Filters

```python
from data_fetchers.jwst_fetcher import get_jwst_filters

# Get all NIRCam filters
nircam_filters = get_jwst_filters('NIRCAM')
print(f"NIRCam filters: {nircam_filters}")

# Get MIRI filters
miri_filters = get_jwst_filters('MIRI')
print(f"MIRI filters: {miri_filters}")
```

## JWST Instruments

### Available Instruments

| Instrument | Name | Type | Wavelength |
|------------|------|------|------------|
| **NIRCAM** | Near Infrared Camera | Imager | 0.6-5.0 μm |
| **NIRSPEC** | Near Infrared Spectrograph | Spectrograph | 0.6-5.3 μm |
| **MIRI** | Mid-Infrared Instrument | Imager & Spectrograph | 5-28 μm |
| **NIRISS** | Near Infrared Imager and Slitless Spectrograph | Imager & Spectrograph | 0.8-5.0 μm |
| **FGS** | Fine Guidance Sensor | Guider | 0.6-5.0 μm |

### Common Filters

**NIRCam:**
- Short wavelength: F070W, F090W, F115W, F150W, F200W
- Long wavelength: F277W, F356W, F444W

**MIRI:**
- F560W, F770W, F1000W, F1130W, F1280W, F1500W, F1800W, F2100W, F2550W

## Famous JWST Targets

### 1. Cartwheel Galaxy
```python
ra, dec = 9.4333, -33.7128
df = fetch_jwst_observations(ra, dec, radius=60)
```

### 2. Stephan's Quintet
```python
ra, dec = 339.0129, 33.9589
df = fetch_jwst_observations(ra, dec, radius=120)
```

### 3. Carina Nebula
```python
ra, dec = 161.265, -59.866
df = fetch_jwst_observations(ra, dec, radius=180)
```

### 4. Southern Ring Nebula
```python
ra, dec = 151.761, -40.444
df = fetch_jwst_observations(ra, dec, radius=30)
```

### 5. SMACS 0723 (Deep Field)
```python
ra, dec = 110.841, -73.453
df = fetch_jwst_observations(ra, dec, radius=120)
```

## Function Reference

### `fetch_jwst_observations(ra, dec, radius, instrument, filters, proposal_id, timeout)`

Query JWST observations by position.

**Parameters:**
- `ra` (float): Right Ascension in degrees
- `dec` (float): Declination in degrees
- `radius` (float): Search radius in arcseconds (default: 5.0)
- `instrument` (str, optional): Filter by instrument (NIRCAM, NIRSPEC, MIRI, NIRISS)
- `filters` (str, optional): Filter by specific filter (F277W, F200W, etc.)
- `proposal_id` (str, optional): Filter by proposal ID
- `timeout` (int): Query timeout in seconds (default: 30)

**Returns:** pandas DataFrame with observation metadata

### `get_jwst_preview_images(ra, dec, radius, max_images, instrument)`

Get JWST preview images with download URLs.

**Parameters:**
- `ra` (float): Right Ascension in degrees
- `dec` (float): Declination in degrees
- `radius` (float): Search radius in arcseconds (default: 5.0)
- `max_images` (int): Maximum number of images to return (default: 5)
- `instrument` (str, optional): Filter by instrument

**Returns:** List of dictionaries with image info and preview URLs

### `query_jwst_by_proposal(proposal_id, instrument, filters, max_results)`

Query JWST observations by proposal ID.

**Parameters:**
- `proposal_id` (str): JWST proposal ID (e.g., '2727', '1073')
- `instrument` (str, optional): Filter by instrument
- `filters` (str, optional): Filter by specific filter
- `max_results` (int): Maximum results (default: 100)

**Returns:** pandas DataFrame with observations

### `get_jwst_instruments_info()`

Get information about JWST instruments.

**Returns:** Dictionary with instrument specifications

## Error Handling

```python
try:
    df = fetch_jwst_observations(ra, dec, radius=30)
    if df is None or len(df) == 0:
        print("No observations found")
    else:
        print(f"Found {len(df)} observations")
except Exception as e:
    print(f"Error querying JWST: {e}")
```

## Tips & Best Practices

1. **Use appropriate search radius:**
   - Point sources: 5-30 arcsec
   - Extended sources: 60-180 arcsec
   - Wide fields: 300+ arcsec

2. **Filter by instrument:** Speeds up queries and focuses results
   ```python
   df = fetch_jwst_observations(ra, dec, instrument='NIRCAM')
   ```

3. **Check for preview images:** Not all observations have previews yet
   ```python
   images = get_jwst_preview_images(ra, dec)
   if images:
       print(f"Found {len(images)} images with previews")
   ```

4. **Handle timeouts:** Increase timeout for slow connections
   ```python
   df = fetch_jwst_observations(ra, dec, timeout=60)
   ```

5. **Save results:** Export data for later analysis
   ```python
   df.to_csv('jwst_observations.csv', index=False)
   ```

## Examples

See `examples_jwst_usage.py` for complete working examples including:
- Querying by coordinates
- Querying by proposal ID
- Fetching preview images
- Comparing HST and JWST observations

Run tests with:
```bash
python test_jwst.py
```

Run examples with:
```bash
python examples_jwst_usage.py
```

## Resources

- **MAST Portal:** https://mast.stsci.edu/
- **JWST Science:** https://jwst.nasa.gov/
- **Astroquery Docs:** https://astroquery.readthedocs.io/
- **JWST Proposal Search:** https://www.stsci.edu/jwst/science-execution/approved-programs

## Support

For issues with the JWST data fetcher, check:
1. Internet connection to MAST
2. Valid coordinates/proposal IDs
3. Instrument/filter names are correct
4. Query timeout is sufficient

For MAST/JWST data issues:
- Email: archive@stsci.edu
- MAST Help Desk: https://stsci.service-now.com/mast

---

**Last Updated:** January 10, 2026

**Version:** 1.0.0
