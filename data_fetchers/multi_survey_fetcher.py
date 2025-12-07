"""
Multi-survey data fetcher - fetch data from multiple surveys simultaneously
"""
from typing import Dict, Optional, Tuple, List
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def fetch_all_surveys(
    ra: float,
    dec: float,
    object_name: str = "Target",
    radius: float = 5.0,
    surveys: Optional[List[str]] = None,
    parallel: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Fetch data from multiple astronomical surveys
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    object_name : str, optional
        Name of the object for logging
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    surveys : list of str, optional
        List of surveys to query. Options: 'gaia', 'sdss', 'panstarrs', '2mass', 'mast'
        If None, queries all available surveys
    parallel : bool, optional
        If True, fetch data in parallel (faster but more resource intensive)
    
    Returns
    -------
    dict
        Dictionary with survey names as keys and DataFrames as values
        Example: {'gaia': df_gaia, 'sdss': df_sdss, ...}
    """
    from .gaia_fetcher import fetch_gaia_data
    from .sdss_fetcher import fetch_sdss_data
    from .panstarrs_fetcher import fetch_panstarrs_data
    from .twomass_fetcher import fetch_2mass_data
    from .mast_fetcher import fetch_mast_observations
    
    if surveys is None:
        surveys = ['gaia', 'sdss', 'panstarrs', '2mass', 'mast']
    
    results = {}
    
    # Define fetch functions
    fetch_functions = {
        'gaia': lambda: fetch_gaia_data(ra, dec, radius=radius),
        'sdss': lambda: fetch_sdss_data(ra, dec, radius=radius),
        'panstarrs': lambda: fetch_panstarrs_data(ra, dec, radius=radius),
        '2mass': lambda: fetch_2mass_data(ra, dec, radius=radius),
        'mast': lambda: fetch_mast_observations(ra, dec, radius=radius)
    }
    
    if parallel:
        # Parallel fetching
        print(f"Fetching data for {object_name} in parallel...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_survey = {
                executor.submit(fetch_functions[survey]): survey
                for survey in surveys if survey in fetch_functions
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_survey):
                survey = future_to_survey[future]
                try:
                    data = future.result(timeout=30)
                    if data is not None and len(data) > 0:
                        results[survey] = data
                        print(f"  ✓ {survey.upper()}: {len(data)} sources")
                    else:
                        print(f"  ✗ {survey.upper()}: No data")
                except Exception as e:
                    print(f"  ✗ {survey.upper()}: Error - {e}")
    else:
        # Sequential fetching
        print(f"Fetching data for {object_name} sequentially...")
        for survey in surveys:
            if survey not in fetch_functions:
                continue
            
            print(f"  Querying {survey.upper()}...")
            try:
                data = fetch_functions[survey]()
                if data is not None and len(data) > 0:
                    results[survey] = data
                    print(f"    ✓ Found {len(data)} sources")
                else:
                    print(f"    ✗ No data")
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    return results


def fetch_galaxy_multiband_data(
    ra: float,
    dec: float,
    object_name: str = "Galaxy",
    radius: float = 5.0
) -> Dict[str, any]:
    """
    Fetch comprehensive multi-band data for a galaxy
    
    This function fetches:
    - Gaia: Astrometry and optical photometry (G, BP, RP)
    - SDSS: ugriz photometry and spectra
    - MAST: HST, JWST, GALEX observations
    - Pan-STARRS: grizy photometry
    - 2MASS: JHK near-infrared
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    object_name : str, optional
        Name of the galaxy
    radius : float, optional
        Search radius in arcseconds
    
    Returns
    -------
    dict
        Comprehensive data dictionary with keys:
        - 'catalogs': Dictionary of catalog DataFrames
        - 'summary': Summary statistics
        - 'coordinates': Input coordinates
    """
    print("=" * 70)
    print(f"MULTI-SURVEY GALAXY DATA FETCH")
    print(f"Object: {object_name}")
    print(f"Coordinates: RA={ra:.6f}°, Dec={dec:.6f}°")
    print(f"Search radius: {radius} arcsec")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    # Fetch all catalog data
    catalogs = fetch_all_surveys(
        ra, dec,
        object_name=object_name,
        radius=radius,
        parallel=True
    )
    
    elapsed = time.time() - start_time
    
    # Create summary
    summary = {
        'object_name': object_name,
        'ra': ra,
        'dec': dec,
        'radius_arcsec': radius,
        'n_surveys': len(catalogs),
        'surveys': list(catalogs.keys()),
        'total_sources': sum(len(df) for df in catalogs.values()),
        'fetch_time_sec': elapsed
    }
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Surveys queried: {summary['n_surveys']}")
    print(f"Total sources found: {summary['total_sources']}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print()
    
    for survey, df in catalogs.items():
        print(f"  {survey.upper():15s}: {len(df):4d} sources")
    
    print("=" * 70)
    
    return {
        'catalogs': catalogs,
        'summary': summary,
        'coordinates': {'ra': ra, 'dec': dec}
    }


def cross_match_catalogs(
    catalogs: Dict[str, pd.DataFrame],
    match_radius: float = 1.0
) -> pd.DataFrame:
    """
    Cross-match sources across different catalogs
    
    Parameters
    ----------
    catalogs : dict
        Dictionary of catalog DataFrames with survey names as keys
    match_radius : float, optional
        Matching radius in arcseconds (default: 1.0)
    
    Returns
    -------
    pd.DataFrame
        Cross-matched catalog with columns from all surveys
    """
    from astropy.coordinates import SkyCoord, match_coordinates_sky
    
    if len(catalogs) < 2:
        print("Need at least 2 catalogs for cross-matching")
        return None
    
    print(f"\nCross-matching catalogs within {match_radius} arcsec...")
    
    # Start with the first catalog as reference
    surveys = list(catalogs.keys())
    ref_survey = surveys[0]
    ref_cat = catalogs[ref_survey].copy()
    
    # Create SkyCoord for reference catalog
    ref_coords = SkyCoord(
        ra=ref_cat['ra'].values * u.deg,
        dec=ref_cat['dec'].values * u.deg
    )
    
    # Match with other catalogs
    for survey in surveys[1:]:
        cat = catalogs[survey]
        
        # Create SkyCoord for this catalog
        cat_coords = SkyCoord(
            ra=cat['ra'].values * u.deg,
            dec=cat['dec'].values * u.deg
        )
        
        # Perform matching
        idx, d2d, _ = match_coordinates_sky(ref_coords, cat_coords)
        
        # Keep only matches within radius
        match_mask = d2d < match_radius * u.arcsec
        n_matches = match_mask.sum()
        
        print(f"  {ref_survey} <-> {survey}: {n_matches} matches")
        
        # Add matched columns (with survey prefix to avoid conflicts)
        for col in cat.columns:
            if col not in ['ra', 'dec']:
                ref_cat[f'{survey}_{col}'] = None
                ref_cat.loc[match_mask, f'{survey}_{col}'] = cat.iloc[idx[match_mask]][col].values
    
    return ref_cat


# Example usage function
def example_fetch_galaxy():
    """
    Example of how to fetch multi-survey data for a galaxy
    """
    # NGC 4151 - Seyfert galaxy
    ra = 182.6357
    dec = 39.4058
    
    # Fetch all data
    result = fetch_galaxy_multiband_data(
        ra, dec,
        object_name="NGC 4151",
        radius=5.0
    )
    
    # Access the catalogs
    catalogs = result['catalogs']
    
    # Print some example data
    if 'gaia' in catalogs:
        print("\nGaia data sample:")
        print(catalogs['gaia'].head())
    
    if 'sdss' in catalogs:
        print("\nSDSS data sample:")
        print(catalogs['sdss'].head())
    
    return result


if __name__ == "__main__":
    # Run example
    example_fetch_galaxy()
