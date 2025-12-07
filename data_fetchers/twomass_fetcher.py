"""
2MASS data fetcher module
Queries 2MASS All-Sky Point Source Catalog
"""
from typing import Optional
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.vizier import Vizier


def fetch_2mass_data(
    ra: float,
    dec: float,
    radius: float = 5.0,
    max_results: int = 100
) -> Optional[pd.DataFrame]:
    """
    Fetch 2MASS photometric data
    
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
        2MASS photometric data (J, H, K bands)
    """
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query Vizier for 2MASS All-Sky Point Source Catalog
        v = Vizier(
            columns=['*'],
            row_limit=max_results,
            catalog='II/246/out'  # 2MASS All-Sky Point Source Catalog
        )
        
        result = v.query_region(coord, radius=radius*u.arcsec)
        
        if result is None or len(result) == 0:
            return None
        
        # Extract main table
        table = result[0]
        
        # Convert to pandas
        df = table.to_pandas()
        
        # Rename columns for clarity
        column_mapping = {
            'RAJ2000': 'ra',
            'DEJ2000': 'dec',
            'Jmag': 'J',
            'Hmag': 'H',
            'Kmag': 'K',
            'e_Jmag': 'J_err',
            'e_Hmag': 'H_err',
            'e_Kmag': 'K_err'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        return df
        
    except Exception as e:
        print(f"Error fetching 2MASS data: {e}")
        return None


def compute_near_ir_colors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute near-infrared colors from 2MASS photometry
    
    Parameters
    ----------
    df : pd.DataFrame
        2MASS data with J, H, K magnitudes
    
    Returns
    -------
    pd.DataFrame
        DataFrame with added color columns
    """
    if df is None or len(df) == 0:
        return df
    
    # Compute colors
    if 'J' in df.columns and 'H' in df.columns:
        df['J-H'] = df['J'] - df['H']
    
    if 'H' in df.columns and 'K' in df.columns:
        df['H-K'] = df['H'] - df['K']
    
    if 'J' in df.columns and 'K' in df.columns:
        df['J-K'] = df['J'] - df['K']
    
    return df
