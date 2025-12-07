"""
MAST (Mikulski Archive for Space Telescopes) data fetcher
Query HST, JWST, and other space telescope archives
"""
from typing import Optional, Dict, List
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u


def fetch_mast_observations(
    ra: float,
    dec: float,
    radius: float = 5.0,
    missions: Optional[List[str]] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch MAST observations by coordinates
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    missions : list of str, optional
        List of missions to query (e.g., ['HST', 'JWST', 'GALEX'])
        If None, queries all missions
    
    Returns
    -------
    pd.DataFrame or None
        MAST observations as DataFrame, or None if query fails
    """
    try:
        from astroquery.mast import Observations
        
        # Create coordinate object
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query MAST
        obs_table = Observations.query_region(
            coord,
            radius=radius*u.arcsec
        )
        
        if obs_table is None or len(obs_table) == 0:
            print("No MAST observations found")
            return None
        
        # Convert to pandas DataFrame
        df = obs_table.to_pandas()
        
        # Filter by missions if specified
        if missions is not None:
            mission_filter = df['obs_collection'].isin(missions)
            df = df[mission_filter]
        
        if len(df) == 0:
            print(f"No observations found for missions: {missions}")
            return None
        
        # Select useful columns
        useful_cols = [
            'obs_id', 'obs_collection', 'instrument_name',
            'target_name', 'filters', 'exposure_time',
            's_ra', 's_dec', 't_obs_release', 'dataproduct_type'
        ]
        
        # Keep only columns that exist
        cols_to_keep = [col for col in useful_cols if col in df.columns]
        df = df[cols_to_keep]
        
        return df
        
    except Exception as e:
        print(f"Error fetching MAST data: {e}")
        return None


def fetch_hst_images(
    ra: float,
    dec: float,
    radius: float = 5.0,
    filters: Optional[List[str]] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch HST imaging observations
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    filters : list of str, optional
        Specific filters to query (e.g., ['F814W', 'F606W'])
    
    Returns
    -------
    pd.DataFrame or None
        HST observations
    """
    try:
        df = fetch_mast_observations(ra, dec, radius, missions=['HST'])
        
        if df is None:
            return None
        
        # Filter for imaging data
        if 'dataproduct_type' in df.columns:
            df = df[df['dataproduct_type'] == 'image']
        
        # Filter by specific filters if requested
        if filters is not None and 'filters' in df.columns:
            filter_mask = df['filters'].apply(
                lambda x: any(f in str(x) for f in filters) if pd.notna(x) else False
            )
            df = df[filter_mask]
        
        return df
        
    except Exception as e:
        print(f"Error fetching HST images: {e}")
        return None


def fetch_jwst_data(
    ra: float,
    dec: float,
    radius: float = 5.0
) -> Optional[pd.DataFrame]:
    """
    Fetch JWST observations
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    
    Returns
    -------
    pd.DataFrame or None
        JWST observations
    """
    try:
        df = fetch_mast_observations(ra, dec, radius, missions=['JWST'])
        return df
        
    except Exception as e:
        print(f"Error fetching JWST data: {e}")
        return None


def fetch_galex_data(
    ra: float,
    dec: float,
    radius: float = 10.0
) -> Optional[pd.DataFrame]:
    """
    Fetch GALEX UV observations
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    
    Returns
    -------
    pd.DataFrame or None
        GALEX observations
    """
    try:
        df = fetch_mast_observations(ra, dec, radius, missions=['GALEX'])
        return df
        
    except Exception as e:
        print(f"Error fetching GALEX data: {e}")
        return None
