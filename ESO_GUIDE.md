# ESO Archive Integration Guide

**Last Updated:** December 21, 2025

This comprehensive guide covers ESO (European Southern Observatory) archive integration in the Galaxy Visualization App, including VLTI/GRAVITY observations.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Available Instruments](#available-instruments)
3. [Using the Dashboard](#using-the-dashboard)
4. [Downloading FITS Images](#downloading-fits-images)
5. [GRAVITY Interferometry Data](#gravity-interferometry-data)
6. [Troubleshooting](#troubleshooting)
7. [Technical Details](#technical-details)

---

## Quick Start

### Prerequisites

```bash
pip install astroquery
```

### Basic Usage in Dashboard

1. Navigate to **🖼️ Thumbnails** page
2. Click on **ESO Archive** tab
3. Enter target coordinates or name
4. Select instruments (FORS2, HAWKI, MUSE, OMEGACAM, GRAVITY, etc.)
5. Click **🔍 Query by Position** or **🎯 Query by Name**
6. View results and download FITS files

### Example: Query M8 Lagoon Nebula

```
Target: M8 Lagoon Nebula
RA: 270.937°
Dec: -24.333°
Radius: 60 arcsec
Instruments: OMEGACAM, FORS2
```

---

## Available Instruments

### Optical Imagers
- **FORS2**: FOcal Reducer and low dispersion Spectrograph
  - Wavelength: 330-1100 nm
  - Field of view: 6.8' × 6.8'
  - Use for: Optical imaging and spectroscopy

- **OMEGACAM**: Wide-field optical imager
  - Wavelength: 330-1000 nm
  - Field of view: 1° × 1° (268 megapixels!)
  - Use for: Large-area surveys (VST surveys)

- **VIMOS**: VIsible MultiObject Spectrograph
  - Wavelength: 360-1000 nm
  - Field of view: 4 × 7' × 8'
  - Use for: Multi-object spectroscopy

### Near-Infrared Imagers
- **HAWKI**: High Acuity Wide field K-band Imager
  - Wavelength: 0.9-2.5 μm (JHK bands)
  - Field of view: 7.5' × 7.5'
  - Use for: Near-IR imaging

- **VIRCAM**: VISTA InfraRed CAMera
  - Wavelength: 0.9-2.5 μm
  - Field of view: 1.65° diameter
  - Use for: Large-area near-IR surveys

### Integral Field Spectrographs
- **MUSE**: Multi Unit Spectroscopic Explorer
  - Wavelength: 465-930 nm
  - Field of view: 1' × 1'
  - Spectral resolution: R~3000
  - Use for: 3D spectroscopy, mapping emission lines

### High-Angular Resolution
- **SPHERE**: Spectro-Polarimetric High-contrast Exoplanet REsearch
  - Use for: Direct imaging of exoplanets and disks
  - Features: Extreme AO, coronagraphs

- **ERIS**: Enhanced Resolution Imager and Spectrograph
  - Wavelength: 1-5 μm
  - Use for: High-resolution near-IR imaging/spectroscopy

### VLTI Interferometry
- **GRAVITY**: General Relativity Analysis via VLT InTerferometrY
  - Wavelength: K-band (2.0-2.4 μm)
  - Angular resolution: ~4 milliarcseconds
  - Use for: Astrometry, interferometric observations of compact objects

- **MATISSE**: Multi AperTure mid-Infrared SpectroScopic Experiment
  - Wavelength: 3-13 μm (L, M, N bands)
  - Use for: Mid-IR interferometry

---

## Using the Dashboard

### Method 1: Query by Position

1. **Enter Coordinates:**
   ```
   RA (degrees): 49.964523
   Dec (degrees): 41.573593
   ```

2. **Set Search Radius:**
   - Default: 30 arcsec
   - For wide-field (OMEGACAM, VIRCAM): 60-120 arcsec
   - For targeted observations: 10-30 arcsec

3. **Select Instruments:**
   - Choose from dropdown (multiple selection allowed)
   - Default: FORS2, HAWKI, MUSE

4. **Query:**
   - Click "🔍 Query by Position"
   - Wait 10-40 seconds depending on instruments
   - Results appear in expandable sections

### Method 2: Query by Name

1. **Enter Target Name:**
   ```
   Examples:
   - NGC 1277
   - M8
   - HD 85567
   - HIP 22059
   ```

2. **System will:**
   - Resolve name via Simbad
   - Convert to coordinates
   - Query ESO archive

3. **Results:**
   - Same format as position query
   - Shows resolved coordinates

### Understanding Results

Each observation shows:
- **Object**: Target name in ESO archive
- **Date**: Observation date (YYYY-MM-DD)
- **Filter/Mode**: Observing setup
- **Exposure Time**: Integration time (seconds)
- **Program ID**: ESO program identifier
- **DP.ID**: Data Product ID (for downloading)

---

## Downloading FITS Images

### Step-by-Step Process

1. **Select Observation:**
   - Choose DP.ID from dropdown menu
   - Shows first 10 observations per instrument

2. **Download:**
   - Click "🔬 Download & Display"
   - App downloads FITS file from ESO
   - Automatically decompresses if needed
   - Displays image with auto-scaling

3. **View Image:**
   - Image rendered inline
   - Scaling: 0.5-99.5 percentile
   - Color map: Gray (default)

4. **Inspect Header:**
   - Click "📋 FITS Header Information" expander
   - View full FITS header
   - Shows instrument settings, coordinates, etc.

### File Storage

Downloaded FITS files are saved to:
```
~/.astropy/cache/astroquery/Eso/
```

Files are:
- Named by DP.ID (e.g., `FORS2.2023-01-15T12:34:56.789.fits`)
- Automatically decompressed (.Z removed)
- Cached for future use
- Can be opened with astronomy tools (DS9, FITS viewers)

### FITS File Types

Different instruments produce different data:
- **FORS2, HAWKI, OMEGACAM**: 2D images (displayable)
- **MUSE**: 3D data cubes (displays first slice)
- **GRAVITY**: Interferometry data (not simple images)
- **Spectroscopy**: 2D spectra or 1D tables

---

## GRAVITY Interferometry Data

### About GRAVITY

GRAVITY is a VLTI (Very Large Telescope Interferometer) instrument providing:
- **Milliarcsecond angular resolution** (~4 mas at 2.2 μm)
- **Dual-field mode**: Observe science target + reference star
- **Astrometry**: Precise relative positions (10-100 μas precision)
- **Spectroscopy**: K-band (R~4000 or R~500)

### Data Products

GRAVITY produces specialized data products:
- **Interferometric visibilities**: Not simple images
- **Closure phases**: Phase information
- **Differential phases**: For astrometry
- **Spectra**: K-band science target + reference

### Querying GRAVITY Data

```python
# Example: Query GRAVITY observations of HIP 22059
Target: HIP 22059
RA: 71.173936°
Dec: -37.121383°
Radius: 30 arcsec
Instrument: GRAVITY
```

Expected observations:
- Binary star observations
- Dual-field interferometry data
- Science + calibrator observations

### Working with GRAVITY Data

GRAVITY FITS files contain:
- **HDU 0**: Primary header (metadata)
- **HDU 1**: OI_WAVELENGTH (wavelength table)
- **HDU 2**: OI_VIS (visibility amplitudes)
- **HDU 3**: OI_VIS2 (squared visibilities)
- **HDU 4**: OI_T3 (closure phases)
- **HDU 5**: OI_FLUX (photometry)

To analyze GRAVITY data:
```python
from astropy.io import fits
import numpy as np

# Open GRAVITY file
hdul = fits.open('GRAVI.2019-01-19T00:18:13.531.fits')

# Access visibility data
vis_data = hdul['OI_VIS'].data
vis_amp = vis_data['VISAMP']
vis_phi = vis_data['VISPHI']

# Access closure phases
t3_data = hdul['OI_T3'].data
clos_phase = t3_data['T3PHI']
```

**Recommended Tools:**
- GRAVITY Data Reduction Software (pipeline)
- `oifits` Python package
- JMMC tools (OIFitsExplorer, LITpro)

### Example Science Cases

**Binary Stars (HIP 22059, HIP 113201):**
- Measure separation and position angle
- Track orbital motion
- Determine masses

**Galactic Center:**
- Study stars orbiting Sgr A*
- Test general relativity
- Measure stellar orbits

**Active Galactic Nuclei:**
- Resolve broad-line region
- Measure size-luminosity relation
- Study accretion disk structure

---

## Troubleshooting

### No Data Found

**Problem:** Query returns no results

**Solutions:**
1. **Increase search radius:**
   - Try 60-120 arcsec for wide-field instruments
   - OMEGACAM/VIRCAM have large pixels

2. **Check instrument availability:**
   - Not all instruments observe all targets
   - Some instruments decommissioned (NACO, ISAAC)

3. **Verify coordinates:**
   - Use Simbad to resolve target name
   - Check coordinate epoch (J2000)

4. **Try ESO archive website directly:**
   - http://archive.eso.org/wdb/wdb/eso/eso_archive_main/query
   - Verify data exists

### Query Times Out

**Problem:** Query takes too long or fails

**Solutions:**
1. **Query fewer instruments:**
   - Try one at a time
   - Reduces server load

2. **Reduce search radius:**
   - Smaller radius = faster query
   - 10-30 arcsec usually sufficient

3. **Check network:**
   - ESO TAP service may be slow
   - Try during off-peak hours
   - Use VPN if blocked

4. **Increase timeout:**
   - Default: 60 seconds
   - May need longer for OMEGACAM

### Download Fails

**Problem:** "Access denied" or download error

**Solutions:**
1. **Proprietary data:**
   - Some data under proprietary period
   - Only PI and delegates can access
   - Wait for public release

2. **Network issues:**
   - Check internet connection
   - ESO data portal may be down
   - Try again later

3. **Invalid DP.ID:**
   - Verify DP.ID format correct
   - Try different observation

### No Image Displayed

**Problem:** FITS file downloads but no image shown

**Causes:**
1. **GRAVITY/Interferometry data:**
   - Not simple images
   - Contains visibility tables
   - Use specialized tools

2. **Spectroscopy:**
   - 1D or 2D spectra
   - Not 2D images
   - May show spectrum as "image"

3. **Corrupted file:**
   - Re-download
   - Check file size

**Solutions:**
- Check DPR.CATG and DPR.TYPE in table
- Select observations marked as "SCIENCE IMAGE"
- Avoid "SPECTRUM" or interferometry data types

### Recent Data Missing

**Problem:** Can't find recent observations

**Solutions:**
1. **ROW_LIMIT increased:**
   - Now shows last 100 observations
   - Previously was 50

2. **Proprietary period:**
   - Recent data may be restricted
   - ESO: typically 1 year proprietary

3. **Processing delay:**
   - Raw data archived immediately
   - Reduced data may take weeks

### Connection Issues

**Problem:** Can't connect to ESO

**Diagnostic:**
```python
from astroquery.eso import Eso
eso = Eso()
eso.ROW_LIMIT = 5
result = eso.query_instrument('fors2')
print(f"Success: {len(result)} results")
```

**Solutions:**
- Check firewall settings
- Try different network
- Contact ESO user support

---

## Technical Details

### Query Method: TAP/ADQL

ESO archive now uses **TAP (Table Access Protocol)** with **ADQL (Astronomical Data Query Language)**:

```python
# Example ADQL query format
column_filters = {
    'ra': 'between 270.9 and 271.0',
    'dec': 'between -24.4 and -24.3',
    'dp_cat': "= 'SCIENCE'"
}
```

### Important ADQL Syntax

**Date ranges:**
```python
'exp_start': "between '2020-01-01' and '2024-12-31'"
```

**Numeric comparisons:**
```python
'exptime': "> 30"
'seeing': "< 1.0"
```

**String matching:**
```python
'object': "like '%NGC%'"
'filter': "in ('r_SDSS', 'g_SDSS')"
```

### Column Names

Key columns in ESO archive:
- `ra`, `dec`: Coordinates (degrees)
- `object`: Target name
- `date_obs`, `exp_start`: Observation dates
- `dp_id`: Data product ID
- `prog_id`: Program ID
- `exptime`: Exposure time (seconds)
- `filter_path`, `ins.filt1.name`: Filter names
- `dp_cat`, `dpr.catg`: Data category
- `dp_tech`, `dpr.tech`: Technique
- `telescope`: Telescope name

### API Limits

- **ROW_LIMIT**: 100 observations per query
- **Timeout**: 60 seconds default
- **Rate limiting**: ESO may throttle requests
- **Cache**: Results cached in Astropy cache

### Data Rights

- **Public data**: Freely accessible after proprietary period
- **Proprietary data**: PI + delegates only (typically 1 year)
- **Calibration data**: Public immediately
- **Authentication**: Required for proprietary access

### Direct Download URL Format

```
https://dataportal.eso.org/dataPortal/file/{DP.ID}
```

Example:
```
https://dataportal.eso.org/dataPortal/file/FORS2.2023-01-15T12:34:56.789
```

---

## Additional Resources

### ESO Archive
- **Main Portal**: http://archive.eso.org/
- **TAP Interface**: https://archive.eso.org/programmatic/#TAP
- **User Manual**: http://archive.eso.org/cms/eso-data.html

### GRAVITY Resources
- **GRAVITY Homepage**: https://www.eso.org/sci/facilities/paranal/instruments/gravity.html
- **Pipeline**: https://www.eso.org/sci/software/pipelines/
- **Data Format**: OIFITS (Optical Interferometry FITS)

### Python Tools
- **Astroquery**: https://astroquery.readthedocs.io/
- **Astropy**: https://www.astropy.org/
- **OIFITS**: https://pypi.org/project/oifits/

### Support
- **ESO User Support**: usd-help@eso.org
- **Archive Issues**: archive-support@eso.org

---

## Changelog

**December 21, 2025:**
- Consolidated 5 separate ESO documentation files
- Added comprehensive GRAVITY section
- Updated with TAP/ADQL syntax
- Added troubleshooting for all common issues
- Increased ROW_LIMIT from 50 to 100
- Fixed Simbad name resolution
- Improved error handling

---

**Happy observing!** 🔭✨

For questions or issues, check the troubleshooting section or contact ESO user support.
