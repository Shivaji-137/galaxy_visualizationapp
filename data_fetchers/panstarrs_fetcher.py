"""
Pan-STARRS data fetcher module
Queries Pan-STARRS DR2 for imaging and photometry
"""
from typing import Optional, Dict, Tuple
import numpy as np
import pandas as pd
import requests
from io import BytesIO
from PIL import Image


def fetch_panstarrs_data(
    ra: float,
    dec: float,
    radius: float = 5.0,
    max_results: int = 100
) -> Optional[pd.DataFrame]:
    """
    Fetch Pan-STARRS photometric data using MAST catalog query
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    max_results : int, optional
        Maximum number of results
    
    Returns
    -------
    pd.DataFrame or None
        Pan-STARRS photometric data
    """
    try:
        # MAST PS1 catalog query
        radius_deg = radius / 3600.0
        
        url = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv"
        params = {
            'ra': ra,
            'dec': dec,
            'radius': radius_deg,
            'nDetections.gte': 1,
            'pagesize': max_results,
            'columns': [
                'objID', 'raMean', 'decMean', 'nDetections',
                'gMeanPSFMag', 'gMeanPSFMagErr',
                'rMeanPSFMag', 'rMeanPSFMagErr',
                'iMeanPSFMag', 'iMeanPSFMagErr',
                'zMeanPSFMag', 'zMeanPSFMagErr',
                'yMeanPSFMag', 'yMeanPSFMagErr'
            ].join(',')
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            return None
        
        # Parse CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        if len(df) == 0:
            return None
        
        return df
        
    except Exception as e:
        print(f"Error fetching Pan-STARRS data: {e}")
        return None


def fetch_panstarrs_image(
    ra: float,
    dec: float,
    size: int = 240,
    filters: str = "grizy",
    color: bool = True
) -> Optional[Dict[str, Image.Image]]:
    """
    Fetch Pan-STARRS cutout images
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    size : int, optional
        Image size in pixels (default: 240)
    filters : str, optional
        Filter string (default: "grizy")
    color : bool, optional
        If True, fetch color composite; if False, fetch individual filters
    
    Returns
    -------
    dict or None
        Dictionary mapping filter names to PIL Image objects
    """
    try:
        images = {}
        
        if color:
            # Fetch color composite (gri)
            url = (
                f"https://ps1images.stsci.edu/cgi-bin/ps1filenames.py?"
                f"ra={ra}&dec={dec}&size={size}&format=fits&filters=gri"
            )
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # For simplicity, use the fitscut service
                fits_url = (
                    f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
                    f"ra={ra}&dec={dec}&size={size}&format=jpg&color=true"
                )
                img_response = requests.get(fits_url, timeout=30)
                if img_response.status_code == 200:
                    images['color'] = Image.open(BytesIO(img_response.content))
        
        # Fetch individual filter images
        for filt in filters:
            url = (
                f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
                f"ra={ra}&dec={dec}&size={size}&format=jpg&filter={filt}"
            )
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                images[filt] = Image.open(BytesIO(response.content))
        
        return images if images else None
        
    except Exception as e:
        print(f"Error fetching Pan-STARRS images: {e}")
        return None


def get_ps1_url(ra: float, dec: float, size: int = 240, filters: str = "grizy") -> str:
    """
    Generate Pan-STARRS image URL
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    size : int, optional
        Image size in pixels
    filters : str, optional
        Filter string
    
    Returns
    -------
    str
        Image URL
    """
    return (
        f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
        f"ra={ra}&dec={dec}&size={size}&format=jpg&filter={filters}"
    )
