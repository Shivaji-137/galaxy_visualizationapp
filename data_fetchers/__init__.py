"""
Data fetching modules for various astronomical surveys
"""
from .gaia_fetcher import fetch_gaia_data
from .sdss_fetcher import fetch_sdss_data, fetch_sdss_spectrum
from .panstarrs_fetcher import fetch_panstarrs_data, fetch_panstarrs_image
from .desi_fetcher import fetch_desi_spectrum
from .twomass_fetcher import fetch_2mass_data

__all__ = [
    'fetch_gaia_data',
    'fetch_sdss_data',
    'fetch_sdss_spectrum',
    'fetch_panstarrs_data',
    'fetch_panstarrs_image',
    'fetch_desi_spectrum',
    'fetch_2mass_data'
]
