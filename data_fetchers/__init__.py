"""
Data fetching modules for various astronomical surveys
"""
from .gaia_fetcher import fetch_gaia_data
from .sdss_fetcher import fetch_sdss_data, fetch_sdss_spectrum
from .panstarrs_fetcher import fetch_panstarrs_data, fetch_panstarrs_image
from .desi_fetcher import fetch_desi_spectrum
from .twomass_fetcher import fetch_2mass_data
from .hst_fetcher import fetch_hst_observations
from .jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images,
    query_jwst_by_proposal,
    get_jwst_instruments_info,
    get_jwst_preview_from_obs_id,
    list_jwst_instruments,
    get_jwst_filters,
    get_jwst_famous_targets,
    download_jwst_image
)

__all__ = [
    'fetch_gaia_data',
    'fetch_sdss_data',
    'fetch_sdss_spectrum',
    'fetch_panstarrs_data',
    'fetch_panstarrs_image',
    'fetch_desi_spectrum',
    'fetch_2mass_data',
    'fetch_hst_observations',
    'fetch_jwst_observations',
    'get_jwst_preview_images',
    'query_jwst_by_proposal',
    'get_jwst_instruments_info',
    'get_jwst_preview_from_obs_id',
    'list_jwst_instruments',
    'get_jwst_filters',
    'get_jwst_famous_targets',
    'download_jwst_image'
]
