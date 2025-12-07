"""
DESI data fetcher module
Queries DESI Early Data Release for spectroscopy
"""
from typing import Optional, Dict
import numpy as np
import requests
from astropy.io import fits
from io import BytesIO


def fetch_desi_spectrum(
    targetid: Optional[int] = None,
    ra: Optional[float] = None,
    dec: Optional[float] = None,
    radius: float = 3.0
) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch DESI spectrum by targetid or coordinates
    
    Parameters
    ----------
    targetid : int, optional
        DESI target ID
    ra : float, optional
        Right Ascension in degrees
    dec : float, optional
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds (for coordinate search)
    
    Returns
    -------
    dict or None
        Dictionary with 'wavelength', 'flux', 'ivar' arrays
    
    Notes
    -----
    DESI EDR access requires authentication. This is a placeholder implementation.
    For real data access, use the DESI spectroscopic database API or download
    spectra from https://data.desi.lbl.gov/
    """
    try:
        # This is a placeholder - actual DESI data access requires authentication
        # and proper API endpoints. Users should download DESI spectra manually
        # or use authenticated access.
        
        # For demonstration, return mock data structure
        print("DESI data access requires authentication and is not yet implemented.")
        print("Please download DESI spectra from https://data.desi.lbl.gov/")
        
        return None
        
    except Exception as e:
        print(f"Error fetching DESI spectrum: {e}")
        return None


def parse_desi_coadd(filepath: str) -> Optional[Dict[str, np.ndarray]]:
    """
    Parse a DESI coadd FITS file
    
    Parameters
    ----------
    filepath : str
        Path to DESI coadd FITS file
    
    Returns
    -------
    dict or None
        Dictionary with spectral data
    """
    try:
        with fits.open(filepath) as hdul:
            # DESI coadd structure
            # HDU 0: Primary header
            # HDU 1: FIBERMAP
            # HDU 2-4: B, R, Z camera spectra
            
            # Combine all cameras
            wave_b = hdul['B_WAVELENGTH'].data
            flux_b = hdul['B_FLUX'].data[0]  # First target
            ivar_b = hdul['B_IVAR'].data[0]
            
            wave_r = hdul['R_WAVELENGTH'].data
            flux_r = hdul['R_FLUX'].data[0]
            ivar_r = hdul['R_IVAR'].data[0]
            
            wave_z = hdul['Z_WAVELENGTH'].data
            flux_z = hdul['Z_FLUX'].data[0]
            ivar_z = hdul['Z_IVAR'].data[0]
            
            # Concatenate cameras
            wavelength = np.concatenate([wave_b, wave_r, wave_z])
            flux = np.concatenate([flux_b, flux_r, flux_z])
            ivar = np.concatenate([ivar_b, ivar_r, ivar_z])
            
            # Sort by wavelength
            sort_idx = np.argsort(wavelength)
            wavelength = wavelength[sort_idx]
            flux = flux[sort_idx]
            ivar = ivar[sort_idx]
            
            return {
                'wavelength': wavelength,
                'flux': flux,
                'ivar': ivar,
                'source': 'DESI'
            }
            
    except Exception as e:
        print(f"Error parsing DESI coadd file: {e}")
        return None
