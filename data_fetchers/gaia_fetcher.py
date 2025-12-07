"""
Gaia data fetcher module
Queries Gaia DR3 for astrometry and photometry
"""
from typing import Optional, Dict, Tuple
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
import pandas as pd
# Lazy import Gaia to avoid connection on module load


def fetch_gaia_data(
    ra: Optional[float] = None,
    dec: Optional[float] = None,
    source_id: Optional[int] = None,
    radius: float = 5.0,
    max_results: int = 100
) -> Optional[pd.DataFrame]:
    """
    Fetch Gaia DR3 data by coordinates or source_id
    
    Parameters
    ----------
    ra : float, optional
        Right Ascension in degrees
    dec : float, optional
        Declination in degrees
    source_id : int, optional
        Gaia DR3 source_id
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    max_results : int, optional
        Maximum number of results (default: 100)
    
    Returns
    -------
    pd.DataFrame or None
        Gaia data as DataFrame, or None if query fails
    """
    try:
        # Import Gaia only when needed
        from astroquery.gaia import Gaia
        
        if source_id is not None:
            # Query by source_id
            query = f"""
            SELECT TOP {max_results}
                source_id, ra, dec, pmra, pmdec, parallax,
                phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                bp_rp, ruwe, parallax_over_error
            FROM gaiadr3.gaia_source
            WHERE source_id = {source_id}
            """
        elif ra is not None and dec is not None:
            # Query by coordinates (cone search)
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
            query = f"""
            SELECT TOP {max_results}
                source_id, ra, dec, pmra, pmdec, parallax,
                phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                bp_rp, ruwe, parallax_over_error,
                DISTANCE(
                    POINT('ICRS', ra, dec),
                    POINT('ICRS', {ra}, {dec})
                ) AS ang_sep
            FROM gaiadr3.gaia_source
            WHERE CONTAINS(
                POINT('ICRS', ra, dec),
                CIRCLE('ICRS', {ra}, {dec}, {radius/3600.0})
            ) = 1
            ORDER BY ang_sep
            """
        else:
            return None
        
        # Execute query
        job = Gaia.launch_job(query)
        results = job.get_results()
        
        if len(results) == 0:
            return None
        
        # Convert to pandas DataFrame
        df = results.to_pandas()
        return df
        
    except Exception as e:
        print(f"Error fetching Gaia data: {e}")
        return None


def resolve_object_to_coords(object_name: str) -> Optional[Tuple[float, float]]:
    """
    Resolve object name to coordinates using Simbad (with fallback catalog)
    
    Parameters
    ----------
    object_name : str
        Object name (e.g., "NGC 4151", "M31")
    
    Returns
    -------
    tuple or None
        (RA, Dec) in degrees, or None if resolution fails
    """
    # Common objects fallback catalog (RA, Dec in degrees)
    KNOWN_OBJECTS = {
        'M1': (83.6324, 22.0174),  # Crab Nebula
        'NGC 1952': (83.6324, 22.0174),  # M1
        'M31': (10.6847, 41.2692),
        'NGC 224': (10.6847, 41.2692),  # M31
        'NGC 4151': (182.6357, 39.4058),
        'NGC 1068': (40.6696, -0.0133),
        'M83': (204.2538, -29.8650),
        'NGC 628': (24.1739, 15.7839),
        'NGC 3184': (154.5708, 41.4244),
        '3C 273': (187.2779, 2.0524),
        'NGC 4579': (189.4312, 11.8181),
        'NGC 4472': (187.4449, 8.0003),
        'M87': (187.7059, 12.3911),
        'NGC 5128': (201.3651, -43.0192),  # Centaurus A
    }
    
    # Normalize object name
    obj_name_upper = object_name.strip().upper()
    
    # Check fallback catalog first
    for key, coords in KNOWN_OBJECTS.items():
        if obj_name_upper == key.upper():
            print(f"Resolved {object_name} from catalog to RA={coords[0]:.6f}, Dec={coords[1]:.6f}")
            return coords
    
    # Try Simbad
    try:
        from astroquery.simbad import Simbad
        
        # Configure Simbad with timeout
        Simbad.TIMEOUT = 30
        
        print(f"Querying Simbad for '{object_name}'...")
        result = Simbad.query_object(object_name)
        
        if result is None or len(result) == 0:
            print(f"No results found for '{object_name}'")
            return None
        
        # Parse coordinates (SIMBAD now returns lowercase column names and deg units)
        ra_deg = float(result['ra'][0])
        dec_deg = float(result['dec'][0])
        
        print(f"Resolved {object_name} via Simbad to RA={ra_deg:.6f}, Dec={dec_deg:.6f}")
        return ra_deg, dec_deg
        
    except Exception as e:
        print(f"Error resolving object name '{object_name}': {e}")
        print("Tip: Try using coordinates directly or check the object name spelling")
        return None
