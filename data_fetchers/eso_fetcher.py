"""
ESO Archive Data Fetcher
Query and retrieve images from ESO instruments using astroquery.eso
"""

from astroquery.eso import Eso
from astropy.coordinates import SkyCoord
import astropy.units as u
from io import BytesIO
from PIL import Image
import requests
import numpy as np


def download_and_display_eso_fits(dp_id, cache_dir=None):
    """
    Download ESO FITS file and prepare for display
    
    Parameters:
    -----------
    dp_id : str
        ESO Data Product ID
    cache_dir : str, optional
        Directory to cache downloaded files
        
    Returns:
    --------
    dict : Contains 'image' (PIL Image), 'header' (dict), 'filepath' (str)
    """
    from astropy.io import fits
    import tempfile
    import os
    
    try:
        eso = Eso()
        
        # Set cache directory
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        
        # Download the file
        print(f"Downloading {dp_id}...")
        files = eso.retrieve_data([dp_id], destination=cache_dir)
        
        if not files or len(files) == 0:
            return None
        
        filepath = files[0]
        print(f"Downloaded to: {filepath}")
        
        # Open FITS file
        with fits.open(filepath) as hdul:
            # Find the first image extension
            img_data = None
            header = None
            
            for hdu in hdul:
                if hdu.data is not None and len(hdu.data.shape) >= 2:
                    img_data = hdu.data
                    header = dict(hdu.header)
                    break
            
            if img_data is None:
                return {'error': 'No image data found in FITS file'}
            
            # Handle different data dimensions
            if len(img_data.shape) == 3:
                # Take middle slice for 3D data
                img_data = img_data[img_data.shape[0]//2, :, :]
            elif len(img_data.shape) == 4:
                # Take middle slices for 4D data
                img_data = img_data[0, 0, :, :]
            
            # Normalize and convert to image
            # Remove NaN and Inf values
            valid_data = img_data[np.isfinite(img_data)]
            
            if len(valid_data) == 0:
                return {'error': 'No valid pixel data in FITS file'}
            
            # Percentile scaling for better visualization
            vmin, vmax = np.percentile(valid_data, [0.5, 99.5])
            
            # Clip and normalize
            img_norm = np.clip((img_data - vmin) / (vmax - vmin), 0, 1)
            img_norm = np.nan_to_num(img_norm, nan=0.0)
            
            # Convert to 8-bit
            img_8bit = (img_norm * 255).astype(np.uint8)
            
            # Create PIL Image
            img = Image.fromarray(img_8bit, mode='L')
            
            # Extract key header info
            key_info = {}
            important_keys = ['OBJECT', 'TELESCOP', 'INSTRUME', 'EXPTIME', 
                            'DATE-OBS', 'FILTER', 'NAXIS1', 'NAXIS2']
            
            for key in important_keys:
                if key in header:
                    key_info[key] = header[key]
            
            return {
                'image': img,
                'header': key_info,
                'filepath': filepath,
                'shape': img_data.shape,
                'instrument': header.get('INSTRUME', 'Unknown')
            }
    
    except Exception as e:
        return {'error': str(e)}


def get_skyview_image(ra, dec, fov_arcmin=5, survey='DSS2 Red'):
    """
    Get cutout image from NASA SkyView service
    Uses astroquery.skyview for reliable image retrieval
    
    Parameters:
    -----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    fov_arcmin : float
        Field of view in arcminutes
    survey : str
        Survey name (e.g., 'DSS2 Red', '2MASS-K')
        
    Returns:
    --------
    PIL.Image or None : Retrieved image
    """
    try:
        from astroquery.skyview import SkyView
        
        # Create coordinate
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query SkyView
        image_list = SkyView.get_images(
            position=coord,
            survey=[survey],
            radius=fov_arcmin*u.arcmin,
            pixels=512  # Fixed size for display
        )
        
        if image_list and len(image_list) > 0:
            # Get the FITS data
            hdu = image_list[0][0]
            data = hdu.data
            
            # Normalize for display
            vmin, vmax = np.percentile(data[np.isfinite(data)], [1, 99])
            data_norm = np.clip((data - vmin) / (vmax - vmin), 0, 1)
            
            # Convert to 8-bit image
            data_8bit = (data_norm * 255).astype(np.uint8)
            
            # Create PIL Image
            img = Image.fromarray(data_8bit, mode='L')
            
            return img
        
        return None
        
    except Exception as e:
        print(f"Error getting SkyView image: {e}")
        return None

def query_eso_images(ra, dec, radius_arcsec=30, instruments=None, max_results=100):
    """
    Query ESO archive for images at given coordinates
    
    Parameters:
    -----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius_arcsec : float
        Search radius in arcseconds
    instruments : list
        List of instruments to query (e.g., ['fors2', 'hawki', 'muse'])
        If None, queries major imaging instruments
    max_results : int
        Maximum number of results per instrument (default: 100)
        
    Returns:
    --------
    dict : Dictionary with instrument names as keys and results tables as values
    """
    eso = Eso()
    eso.ROW_LIMIT = max_results  # Increased from 50 to get more recent data
    
    if instruments is None:
        instruments = [
            'fors2',    # Optical imager
            'hawki',    # Near-IR imager
            'vimos',    # Optical imager/spectrograph
            'omegacam', # Wide-field optical
            'vircam',   # Near-IR wide-field
            'muse',     # Integral field spectrograph
            'eris',     # Adaptive optics imager
            'sphere',   # High-contrast imager
            'gravity',  # Interferometer
        ]
    
    results = {}
    
    # Calculate RA/Dec bounds
    radius_deg = radius_arcsec / 3600.0
    ra_min = ra - radius_deg
    ra_max = ra + radius_deg
    dec_min = dec - radius_deg
    dec_max = dec + radius_deg
    
    for instrument in instruments:
        try:
            print(f"Querying {instrument}...")
            
            # Use simpler query without dp_cat filter for better compatibility
            # The dp_cat field may not work the same way across all instruments
            table = eso.query_instrument(
                instrument,
                column_filters={
                    'ra': f"between {ra_min} and {ra_max}",
                    'dec': f"between {dec_min} and {dec_max}"
                }
            )
            
            if table is not None and len(table) > 0:
                # Filter for SCIENCE observations if dp_cat column exists
                if 'dp_cat' in table.colnames:
                    science_mask = [('SCIENCE' in str(cat)) if cat else False 
                                   for cat in table['dp_cat']]
                    table = table[science_mask]
                
                if len(table) > 0:
                    print(f"  Found {len(table)} observations for {instrument}")
                    results[instrument.upper()] = table
                else:
                    print(f"  No SCIENCE observations for {instrument}")
            else:
                print(f"  No data found for {instrument}")
                
        except Exception as e:
            # Print error for debugging but continue
            print(f"Error querying {instrument}: {e}")
            continue
    
    return results


def query_eso_by_target(target_name, instruments=None, max_results=100):
    """
    Query ESO archive by target name
    
    Parameters:
    -----------
    target_name : str
        Name of astronomical object
    instruments : list
        List of instruments to query
    max_results : int
        Maximum number of results per instrument (default: 100)
        
    Returns:
    --------
    dict : Dictionary with instrument names as keys and results tables as values
    """
    from astroquery.simbad import Simbad
    
    eso = Eso()
    eso.ROW_LIMIT = max_results  # Increased from 50
    
    if instruments is None:
        instruments = ['fors2', 'hawki', 'vimos', 'omegacam', 'vircam', 
                      'muse', 'eris', 'sphere', 'gravity']
    
    # First, resolve the target name via Simbad to get coordinates
    print(f"Querying Simbad for '{target_name}'...")
    try:
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('ra(d)', 'dec(d)')
        custom_simbad.TIMEOUT = 20  # Set timeout
        result_table = custom_simbad.query_object(target_name)
        
        if result_table is not None and len(result_table) > 0:
            # Get RA/Dec in degrees
            ra = float(result_table['RA_d'][0])
            dec = float(result_table['DEC_d'][0])
            
            print(f"✓ Resolved '{target_name}' via Simbad to RA={ra:.6f}, Dec={dec:.6f}")
            print(f"  Now querying ESO archive at these coordinates...")
            
            # Use coordinate-based search with larger radius (60 arcsec)
            return query_eso_images(ra, dec, radius_arcsec=60, instruments=instruments, max_results=max_results)
        else:
            print(f"✗ Could not resolve '{target_name}' via Simbad")
            print(f"  Simbad returned no results. Check object name spelling.")
            return {}
    except Exception as e:
        print(f"✗ Error resolving target '{target_name}': {e}")
        print(f"  This could be due to:")
        print(f"  - Incorrect object name spelling")
        print(f"  - Network connection issues")
        print(f"  - Simbad service temporarily unavailable")
        return {}


def get_eso_skyview_url(ra, dec, fov_arcmin=5, survey='DSS2 Red'):
    """
    Get SkyView cutout URL (NASA's service, includes many surveys)
    Returns direct link to FITS image that can be converted
    
    Parameters:
    -----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    fov_arcmin : float
        Field of view in arcminutes
    survey : str
        Survey name
        
    Returns:
    --------
    str : URL to cutout image
    """
    # Use SkyView JPEG output for direct display
    # Format position as decimal degrees for simplicity
    url = (
        f"https://skyview.gsfc.nasa.gov/current/cgi/basicform.pl?"
        f"Position={ra},{dec}&"
        f"Survey={survey.replace(' ', '+')}&"
        f"Coordinates=J2000&"
        f"Projection=Tan&"
        f"Scaling=Linear&"
        f"Return=JPEG&"
        f"Size={fov_arcmin/60.0:.4f}"  # Size in degrees
    )
    return url


def get_eso_preview_url(dp_id):
    """
    Construct ESO preview/quicklook URL for a data product
    
    Parameters:
    -----------
    dp_id : str
        Data product ID from ESO archive
        
    Returns:
    --------
    str : URL to preview image (may not exist for all products)
    """
    # ESO provides preview images for some instruments
    # Format: https://archive.eso.org/wdb/wdb/eso/[instrument]/DPID.jpg
    
    instrument = dp_id.split('.')[0].lower()
    
    # Try direct preview URL
    preview_url = f"https://archive.eso.org/datalink/links?ID=ivo://eso.org/ID?{dp_id}"
    
    return preview_url


def list_eso_instruments():
    """
    List all available ESO instruments
    
    Returns:
    --------
    list : Available instrument names
    """
    try:
        eso = Eso()
        return eso.list_instruments()
    except Exception as e:
        print(f"Error listing instruments: {e}")
        return []


def get_eso_instrument_info():
    """
    Get information about major ESO imaging instruments
    
    Returns:
    --------
    dict : Information about each instrument
    """
    info = {
        'FORS2': {
            'name': 'FOcal Reducer and low dispersion Spectrograph',
            'type': 'Optical Imager/Spectrograph',
            'telescope': 'VLT UT1 (Antu)',
            'wavelength': '330-1100 nm',
            'fov': '6.8 × 6.8 arcmin',
            'pixel_scale': '0.25 arcsec/pixel',
            'status': 'Active'
        },
        'HAWKI': {
            'name': 'High Acuity Wide field K-band Imager',
            'type': 'Near-IR Imager',
            'telescope': 'VLT UT4 (Yepun)',
            'wavelength': '0.9-2.5 μm (JHK bands)',
            'fov': '7.5 × 7.5 arcmin',
            'pixel_scale': '0.106 arcsec/pixel',
            'status': 'Active'
        },
        'VIMOS': {
            'name': 'VIsible MultiObject Spectrograph',
            'type': 'Optical Imager/Spectrograph',
            'telescope': 'VLT UT3 (Melipal)',
            'wavelength': '360-1000 nm',
            'fov': '4 × (7 × 8) arcmin (4 quadrants)',
            'pixel_scale': '0.205 arcsec/pixel',
            'status': 'Decommissioned 2018'
        },
        'OMEGACAM': {
            'name': 'OmegaCAM',
            'type': 'Wide-field Optical Imager',
            'telescope': 'VST (VLT Survey Telescope)',
            'wavelength': '330-1000 nm',
            'fov': '1 × 1 degree',
            'pixel_scale': '0.213 arcsec/pixel',
            'status': 'Active'
        },
        'VIRCAM': {
            'name': 'VISTA InfraRed CAMera',
            'type': 'Wide-field Near-IR Imager',
            'telescope': 'VISTA',
            'wavelength': '0.9-2.4 μm',
            'fov': '1.65 × 1.65 degree',
            'pixel_scale': '0.339 arcsec/pixel',
            'status': 'Active'
        },
        'MUSE': {
            'name': 'Multi Unit Spectroscopic Explorer',
            'type': 'Integral Field Spectrograph',
            'telescope': 'VLT UT4 (Yepun)',
            'wavelength': '465-930 nm',
            'fov': '1 × 1 arcmin',
            'pixel_scale': '0.2 arcsec/pixel',
            'status': 'Active'
        },
        'ERIS': {
            'name': 'Enhanced Resolution Imager and Spectrograph',
            'type': 'Adaptive Optics Imager/Spectrograph',
            'telescope': 'VLT UT4 (Yepun)',
            'wavelength': '1-5 μm',
            'fov': '27 × 27 arcsec',
            'pixel_scale': '0.013 arcsec/pixel',
            'status': 'Active (since 2022)'
        },
        'SPHERE': {
            'name': 'Spectro-Polarimetric High-contrast Exoplanet REsearch',
            'type': 'High-contrast Imager',
            'telescope': 'VLT UT3 (Melipal)',
            'wavelength': '0.5-2.3 μm',
            'fov': 'Various modes',
            'pixel_scale': '0.0025-0.123 arcsec/pixel',
            'status': 'Active'
        },
        'GRAVITY': {
            'name': 'GRAVITY',
            'type': 'Interferometric Beam Combiner',
            'telescope': 'VLTI (VLT Interferometer)',
            'wavelength': '2.0-2.4 μm (K-band)',
            'fov': '~4 arcsec (single-field), 2×2 arcsec (dual-field)',
            'resolution': '4 milliarcsec (mas) angular resolution',
            'status': 'Active'
        },
        'NACO': {
            'name': 'NAOS-CONICA',
            'type': 'Adaptive Optics Imager',
            'telescope': 'VLT UT4 (Yepun)',
            'wavelength': '1-5 μm',
            'fov': '54 × 54 arcsec',
            'pixel_scale': '0.013-0.054 arcsec/pixel',
            'status': 'Decommissioned 2019'
        },
        'ISAAC': {
            'name': 'Infrared Spectrometer And Array Camera',
            'type': 'Near-IR Imager/Spectrograph',
            'telescope': 'VLT UT1 (Antu)',
            'wavelength': '1-5 μm',
            'fov': '2.5 × 2.5 arcmin',
            'pixel_scale': '0.148 arcsec/pixel',
            'status': 'Decommissioned 2013'
        }
    }
    return info


def download_eso_quicklook(dp_id, output_dir=None):
    """
    Download ESO quicklook/preview image if available
    
    Parameters:
    -----------
    dp_id : str
        Data product ID
    output_dir : str
        Directory to save file (optional)
        
    Returns:
    --------
    str : Path to downloaded file or None
    """
    try:
        eso = Eso()
        files = eso.retrieve_data([dp_id], destination=output_dir)
        return files[0] if files else None
    except Exception as e:
        print(f"Error downloading {dp_id}: {e}")
        return None
