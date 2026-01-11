"""
HST (Hubble Space Telescope) and JWST (James Webb Space Telescope) image fetcher module
Uses ESA Hubble archive and MAST for image retrieval
"""
from typing import Optional, Dict, List, Tuple
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.esa.hubble import ESAHubble
from astroquery.mast import Observations
import requests
from io import BytesIO
from PIL import Image


def fetch_hst_observations(
    ra: float,
    dec: float,
    radius: float = 5.0,
    instrument: Optional[str] = None,
    timeout: int = 30
) -> Optional[pd.DataFrame]:
    """
    Fetch HST observations with timeout (uses MAST directly for reliability)
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    instrument : str, optional
        Specific instrument (e.g., 'ACS', 'WFC3', 'WFPC2')
    timeout : int, optional
        Query timeout in seconds (default: 30)
    
    Returns
    -------
    pd.DataFrame or None
        HST observations table
    """
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Use MAST directly - more reliable than ESA archive
        print(f"Querying MAST for HST observations at RA={ra:.4f}, Dec={dec:.4f}...")
        
        obs_table = Observations.query_criteria(
            coordinates=coord,
            radius=radius*u.arcsec,
            obs_collection='HST',
            dataproduct_type='image'
        )
        
        if obs_table is None or len(obs_table) == 0:
            print("No HST observations found")
            return None
        
        print(f"Found {len(obs_table)} HST observations")
        
        # Convert to pandas
        df = obs_table.to_pandas()
        
        # Filter by instrument if specified
        if instrument is not None and 'instrument_name' in df.columns:
            df = df[df['instrument_name'].str.contains(instrument, case=False, na=False)]
            print(f"After filtering for {instrument}: {len(df)} observations")
        
        return df
        
    except Exception as e:
        print(f"Error fetching HST observations: {e}")
        return None


def get_hst_preview_url(observation_id: str) -> Optional[str]:
    """
    Get HST preview image URL from ESA archive
    
    Parameters
    ----------
    observation_id : str
        HST observation ID
    
    Returns
    -------
    str or None
        URL to preview image
    """
    try:
        # Try multiple URL patterns for HST previews
        url_patterns = [
            f"http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=POSTCARD&OBSERVATION_ID={observation_id}",
            f"https://hla.stsci.edu/cgi-bin/getdata.cgi?config=ops&dataset={observation_id}",
            f"https://hla.stsci.edu/cgi-bin/display?image={observation_id}&format=jpeg",
        ]
        
        for url in url_patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    # Additional check for content type
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type or 'jpeg' in content_type or 'png' in content_type:
                        return url
            except:
                continue
        
        return None
        
    except Exception as e:
        print(f"Error getting HST preview URL: {e}")
        return None


def fetch_hst_cutout_mast(
    ra: float,
    dec: float,
    size: int = 256,
    survey: str = 'ACS'
) -> Optional[str]:
    """
    Fetch HST cutout image from MAST cutout service
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    size : int, optional
        Image size in pixels (default: 256)
    survey : str, optional
        HST survey ('ACS', 'WFC3', 'WFPC2')
    
    Returns
    -------
    str or None
        URL to cutout image
    """
    try:
        # MAST HLA (Hubble Legacy Archive) cutout service
        base_url = "https://hla.stsci.edu/cgi-bin/fitscut.cgi"
        
        # Map survey to appropriate dataset
        survey_map = {
            'ACS': 'ACS',
            'WFC3': 'WFC3',
            'WFPC2': 'WFPC2'
        }
        
        survey_code = survey_map.get(survey.upper(), 'ACS')
        
        url = (
            f"{base_url}?"
            f"red={ra}&dec={dec}&size={size}&format=jpeg&autoscale=99.5"
        )
        
        return url
        
    except Exception as e:
        print(f"Error creating HST cutout URL: {e}")
        return None


def get_best_hst_image(
    ra: float,
    dec: float,
    radius: float = 5.0,
    preferred_instruments: List[str] = None
) -> Optional[Dict]:
    """
    Find and return the best available HST image for given coordinates
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    preferred_instruments : list of str, optional
        Preferred instruments in order (e.g., ['WFC3', 'ACS', 'WFPC2'])
    
    Returns
    -------
    dict or None
        Dictionary with observation info and preview URL
    """
    try:
        if preferred_instruments is None:
            preferred_instruments = ['WFC3', 'ACS', 'WFPC2']
        
        # Query HST observations
        df = fetch_hst_observations(ra, dec, radius)
        
        if df is None or len(df) == 0:
            return None
        
        # Sort by preferred instruments
        for instrument in preferred_instruments:
            instrument_data = df[df['instrument_name'].str.contains(instrument, case=False, na=False)]
            
            if len(instrument_data) > 0:
                # Get first observation
                obs = instrument_data.iloc[0]
                obs_id = obs.get('observation_id', obs.get('obs_id', None))
                
                if obs_id:
                    preview_url = get_hst_preview_url(obs_id)
                    
                    return {
                        'observation_id': obs_id,
                        'instrument': obs.get('instrument_name', instrument),
                        'target_name': obs.get('target_name', 'Unknown'),
                        'filter': obs.get('filter', 'N/A'),
                        'preview_url': preview_url,
                        'ra': obs.get('ra', ra),
                        'dec': obs.get('dec', dec)
                    }
        
        return None
        
    except Exception as e:
        print(f"Error getting best HST image: {e}")
        return None


def search_hla_images(
    ra: float,
    dec: float,
    radius: float = 5.0
) -> Optional[List[str]]:
    """
    Search Hubble Legacy Archive for processed images
    
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
    list of str or None
        List of image URLs
    """
    try:
        # Convert radius to arcminutes for HLA
        size_arcmin = radius / 60.0
        
        # Multiple HLA URL options
        urls = []
        
        # Option 1: HLA fitscut service with various filters
        for filt in ['ACS-WFC', 'WFC3-UVIS', 'WFPC2']:
            url = f"https://hla.stsci.edu/cgi-bin/fitscut.cgi?ra={ra}&dec={dec}&size={int(radius*2)}&filter={filt}&format=jpeg&autoscale=99.5"
            urls.append(url)
        
        # Option 2: Basic cutout without filter specification
        url = f"https://hla.stsci.edu/cgi-bin/fitscut.cgi?ra={ra}&dec={dec}&size={int(radius*2)}&format=jpeg&autoscale=99.5"
        urls.append(url)
        
        return urls
        
    except Exception as e:
        print(f"Error searching HLA: {e}")
        return None


def get_mast_hst_images(
    ra: float,
    dec: float,
    radius: float = 5.0,
    max_images: int = 5
) -> Optional[List[Dict]]:
    """
    Get HST images directly from MAST archive with actual preview URLs
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    max_images : int, optional
        Maximum number of images to return
    
    Returns
    -------
    list of dict or None
        List of dictionaries with image info and URLs
    """
    try:
        from astropy.coordinates import SkyCoord
        from astropy import units as u
        from astroquery.mast import Observations
        
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query MAST for HST observations
        obs_table = Observations.query_criteria(
            coordinates=coord,
            radius=radius*u.arcsec,
            obs_collection='HST',
            dataproduct_type='image'
        )
        
        if obs_table is None or len(obs_table) == 0:
            return None
        
        images = []
        for i, obs in enumerate(obs_table[:max_images*3]):  # Get more to ensure we find some with previews
            if len(images) >= max_images:
                break
                
            obs_id = obs.get('obs_id', obs.get('obsid', 'unknown'))
            instrument = obs.get('instrument_name', 'Unknown')
            filters = obs.get('filters', 'N/A')
            target = obs.get('target_name', 'Unknown')
            
            # Get actual data products for this observation
            try:
                products = Observations.get_product_list(obs)
                
                # Look for preview images (by file extension)
                preview_urls = []
                
                for product in products:
                    dataURI = product.get('dataURI', '')
                    product_type = str(product.get('productType', '')).upper()
                    
                    if not dataURI:
                        continue
                    
                    # Check for image file extensions OR preview type
                    dataURI_lower = dataURI.lower()
                    is_preview = (
                        '.jpg' in dataURI_lower or 
                        '.jpeg' in dataURI_lower or 
                        '.png' in dataURI_lower or 
                        '.gif' in dataURI_lower or
                        product_type == 'PREVIEW'
                    )
                    
                    # Filter: Only keep i2d images (drizzled combined images)
                    if is_preview:
                        # Only accept i2d files (final drizzled products)
                        if '_i2d' not in dataURI_lower:
                            continue
                        
                        download_url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={dataURI}"
                        preview_urls.append(download_url)
                
                # If we found preview URLs, add this observation
                if preview_urls:
                    images.append({
                        'obs_id': obs_id,
                        'instrument': instrument,
                        'filters': filters,
                        'preview_urls': preview_urls[:3],  # Limit to first 3
                        'target': target
                    })
                    
            except Exception as e:
                # If we can't get products, skip this observation
                continue
        
        return images if images else None
        
    except Exception as e:
        print(f"Error getting MAST HST images: {e}")
        return None


def get_skyview_hst_image(
    ra: float,
    dec: float,
    size: float = 10.0
) -> Optional[str]:
    """
    Get HST composite image from SkyView service
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    size : float, optional
        Image size in arcminutes
    
    Returns
    -------
    str or None
        URL to SkyView HST image
    """
    try:
        # SkyView can generate on-the-fly images from HST data
        url = f"https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?Position={ra},{dec}&Survey=HST&Pixels=500&Return=JPEG"
        
        return url
        
    except Exception as e:
        print(f"Error getting SkyView HST image: {e}")
        return None


def fetch_jwst_observations(
    ra: float,
    dec: float,
    radius: float = 5.0,
    instrument: Optional[str] = None,
    filters: Optional[str] = None,
    proposal_id: Optional[str] = None,
    timeout: int = 30
) -> Optional[pd.DataFrame]:
    """
    Fetch JWST observations with flexible filtering options
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds (default: 5.0)
    instrument : str, optional
        Specific instrument (e.g., 'NIRCAM', 'NIRSPEC', 'MIRI', 'NIRISS')
    filters : str, optional
        Specific filter (e.g., 'F277W', 'F200W', 'F150W')
    proposal_id : str, optional
        JWST proposal ID (e.g., '1073', '2736')
    timeout : int, optional
        Query timeout in seconds (default: 30)
    
    Returns
    -------
    pd.DataFrame or None
        JWST observations table with metadata
    """
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Set timeout
        Observations.TIMEOUT = timeout
        
        print(f"Querying MAST for JWST observations at RA={ra:.4f}, Dec={dec:.4f}...")
        
        # Build query criteria
        query_params = {
            'coordinates': coord,
            'radius': radius*u.arcsec,
            'obs_collection': 'JWST',
            'dataproduct_type': 'image'
        }
        
        # Add optional filters
        if instrument is not None:
            query_params['instrument_name'] = instrument.upper()
        
        if filters is not None:
            query_params['filters'] = filters
        
        if proposal_id is not None:
            query_params['proposal_id'] = proposal_id
        
        # Query MAST
        obs_table = Observations.query_criteria(**query_params)
        
        if obs_table is None or len(obs_table) == 0:
            print("No JWST observations found")
            return None
        
        print(f"Found {len(obs_table)} JWST observations")
        
        # Convert to pandas
        df = obs_table.to_pandas()
        
        # Add helpful columns if not present
        if 'obs_id' not in df.columns and 'obsid' in df.columns:
            df['obs_id'] = df['obsid']
        
        return df
        
    except Exception as e:
        print(f"Error fetching JWST observations: {e}")
        return None


def get_jwst_preview_images(
    ra: float,
    dec: float,
    radius: float = 5.0,
    max_images: int = 5,
    instrument: Optional[str] = None
) -> Optional[List[Dict]]:
    """
    Get JWST preview images from MAST archive
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    max_images : int, optional
        Maximum number of images to return
    instrument : str, optional
        Specific instrument filter (e.g., 'NIRCAM', 'MIRI')
    
    Returns
    -------
    list of dict or None
        List of dictionaries with image info and preview URLs
    """
    try:
        from astropy.coordinates import SkyCoord
        from astropy import units as u
        from astroquery.mast import Observations
        
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Query MAST for JWST observations
        query_params = {
            'coordinates': coord,
            'radius': radius*u.arcsec,
            'obs_collection': 'JWST',
            'dataproduct_type': 'image'
        }
        
        if instrument is not None:
            query_params['instrument_name'] = instrument.upper()
        
        obs_table = Observations.query_criteria(**query_params)
        
        if obs_table is None or len(obs_table) == 0:
            return None
        
        images = []
        for i, obs in enumerate(obs_table[:max_images*3]):  # Get more to ensure we find some with previews
            if len(images) >= max_images:
                break
                
            obs_id = obs.get('obs_id', obs.get('obsid', 'unknown'))
            instrument_name = obs.get('instrument_name', 'Unknown')
            filters = obs.get('filters', 'N/A')
            target = obs.get('target_name', 'Unknown')
            proposal = obs.get('proposal_id', 'N/A')
            
            # Get actual data products for this observation
            try:
                products = Observations.get_product_list(obs)
                
                # Look for preview images
                preview_urls = []
                
                for product in products:
                    dataURI = product.get('dataURI', '')
                    product_type = str(product.get('productType', '')).upper()
                    
                    if not dataURI:
                        continue
                    
                    # Check for image file extensions OR preview type
                    dataURI_lower = dataURI.lower()
                    is_preview = (
                        '.jpg' in dataURI_lower or 
                        '.jpeg' in dataURI_lower or 
                        '.png' in dataURI_lower or 
                        '.gif' in dataURI_lower or
                        product_type == 'PREVIEW'
                    )
                    
                    # Filter: Only keep i2d images (drizzled combined images)
                    if is_preview:
                        # Only accept i2d files (final drizzled products)
                        if '_i2d' not in dataURI_lower:
                            continue
                        
                        download_url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={dataURI}"
                        preview_urls.append(download_url)
                
                # If we found preview URLs, add this observation
                if preview_urls:
                    images.append({
                        'obs_id': obs_id,
                        'instrument': instrument_name,
                        'filters': filters,
                        'preview_urls': preview_urls[:3],  # Limit to first 3
                        'target': target,
                        'proposal_id': proposal,
                        'telescope': 'JWST'
                    })
                    
            except Exception as e:
                # If we can't get products, skip this observation
                continue
        
        return images if images else None
        
    except Exception as e:
        print(f"Error getting JWST preview images: {e}")
        return None


def query_jwst_by_proposal(
    proposal_id: str,
    instrument: Optional[str] = None,
    filters: Optional[str] = None,
    max_results: int = 100
) -> Optional[pd.DataFrame]:
    """
    Query JWST observations by proposal ID
    
    Parameters
    ----------
    proposal_id : str
        JWST proposal ID (e.g., '1073', '2736')
    instrument : str, optional
        Specific instrument (e.g., 'NIRCAM', 'NIRSPEC', 'MIRI')
    filters : str, optional
        Specific filter (e.g., 'F277W', 'F200W')
    max_results : int, optional
        Maximum number of results (default: 100)
    
    Returns
    -------
    pd.DataFrame or None
        JWST observations matching the proposal
    """
    try:
        print(f"Querying JWST proposal {proposal_id}...")
        
        # Build query criteria
        query_params = {
            'obs_collection': 'JWST',
            'proposal_id': proposal_id,
            'dataproduct_type': 'image'
        }
        
        if instrument is not None:
            query_params['instrument_name'] = instrument.upper()
        
        if filters is not None:
            query_params['filters'] = filters
        
        # Query MAST
        obs_table = Observations.query_criteria(**query_params)
        
        if obs_table is None or len(obs_table) == 0:
            print(f"No JWST observations found for proposal {proposal_id}")
            return None
        
        # Limit results
        if len(obs_table) > max_results:
            obs_table = obs_table[:max_results]
        
        print(f"Found {len(obs_table)} JWST observations")
        
        # Convert to pandas
        df = obs_table.to_pandas()
        
        return df
        
    except Exception as e:
        print(f"Error querying JWST proposal {proposal_id}: {e}")
        return None


def get_jwst_instruments_info() -> Dict[str, Dict]:
    """
    Get information about JWST instruments
    
    Returns
    -------
    dict
        Dictionary with instrument information
    """
    info = {
        'NIRCAM': {
            'name': 'Near Infrared Camera',
            'type': 'Imager',
            'wavelength': '0.6-5.0 μm',
            'fov': '2.2 × 2.2 arcmin (short), 2.2 × 4.4 arcmin (long)',
            'pixel_scale': '0.031 arcsec/pixel (short), 0.063 arcsec/pixel (long)',
            'filters': 'F070W, F090W, F115W, F150W, F200W, F277W, F356W, F444W, ...',
            'description': 'Primary near-IR imager for JWST'
        },
        'NIRSPEC': {
            'name': 'Near Infrared Spectrograph',
            'type': 'Spectrograph',
            'wavelength': '0.6-5.3 μm',
            'spectral_resolution': 'R~100 (prism), R~1000 (grating), R~2700 (high-res)',
            'modes': 'Multi-object, IFU, fixed slit',
            'description': 'Near-IR spectroscopy with multiple modes'
        },
        'MIRI': {
            'name': 'Mid-Infrared Instrument',
            'type': 'Imager & Spectrograph',
            'wavelength': '5-28 μm',
            'fov': '74 × 113 arcsec (imaging)',
            'pixel_scale': '0.11 arcsec/pixel',
            'filters': 'F560W, F770W, F1000W, F1130W, F1280W, F1500W, F1800W, F2100W, F2550W',
            'description': 'Mid-IR imaging and spectroscopy'
        },
        'NIRISS': {
            'name': 'Near Infrared Imager and Slitless Spectrograph',
            'type': 'Imager & Spectrograph',
            'wavelength': '0.8-5.0 μm',
            'fov': '2.2 × 2.2 arcmin',
            'modes': 'Imaging, WFSS, SOSS, AMI',
            'description': 'Wide-field slitless spectroscopy and imaging'
        },
        'FGS': {
            'name': 'Fine Guidance Sensor',
            'type': 'Guider',
            'wavelength': '0.6-5.0 μm',
            'description': 'Precision pointing and guiding'
        }
    }
    return info


def get_hst_preview_from_obs_id(obs_id: str, timeout: int = 20) -> Optional[Dict]:
    """
    Get HST preview images directly from observation ID using MAST API
    
    Parameters
    ----------
    obs_id : str
        HST observation ID (ESA or MAST format)
    timeout : int, optional
        Query timeout in seconds (default: 20)
    
    Returns
    -------
    dict or None
        Dictionary with preview URLs and metadata
    """
    try:
        from astroquery.mast import Observations
        
        # Set timeout for MAST queries
        Observations.TIMEOUT = timeout
        
        # Try multiple ID formats
        # ESA format: hst_17535_07_wfc3_uvis_f336w_if7p07zf
        # MAST format: if7p07zfq or if7p07
        
        obs_ids_to_try = [obs_id]
        
        # If it's a long ESA format, extract the root observation ID
        if obs_id.startswith('hst_') and len(obs_id) > 20:
            # Extract the last part (e.g., if7p07zf from hst_17535_07_wfc3_uvis_f336w_if7p07zf)
            parts = obs_id.split('_')
            if len(parts) > 5:
                root_id = parts[-1]  # e.g., if7p07zf
                obs_ids_to_try.append(root_id)
                # Also try without last character
                if len(root_id) > 7:
                    obs_ids_to_try.append(root_id[:-1])  # e.g., if7p07z
                    obs_ids_to_try.append(root_id[:-2])  # e.g., if7p07
        
        # Try each possible ID format (but only try first 2 to save time)
        for try_id in obs_ids_to_try[:2]:
            try:
                # Query for this specific observation
                obs_table = Observations.query_criteria(obs_id=try_id)
                
                if obs_table is not None and len(obs_table) > 0:
                    # Get products for this observation
                    products = Observations.get_product_list(obs_table[0])
                    
                    preview_images = []
                    
                    # Only check first 10 products to save time
                    for product in products[:10]:
                        dataURI = product.get('dataURI', '')
                        product_type = str(product.get('productType', '')).upper()
                        
                        if not dataURI:
                            continue
                        
                        # Look for actual image files by extension AND/OR type
                        is_image = False
                        img_type = 'unknown'
                        
                        # Check file extension
                        dataURI_lower = dataURI.lower()
                        if '.jpg' in dataURI_lower or '.jpeg' in dataURI_lower:
                            is_image = True
                            img_type = 'JPEG preview'
                        elif '.png' in dataURI_lower:
                            is_image = True
                            img_type = 'PNG preview'
                        elif '.gif' in dataURI_lower:
                            is_image = True
                            img_type = 'GIF preview'
                        
                        # Also check if explicitly marked as PREVIEW type
                        if product_type == 'PREVIEW':
                            is_image = True
                            if img_type == 'unknown':
                                img_type = 'Preview image'
                        
                        # Filter: Only keep i2d images (drizzled combined images)
                        if is_image:
                            # Only accept i2d files (final drizzled products)
                            if '_i2d' not in dataURI_lower:
                                continue
                            
                            download_url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={dataURI}"
                            preview_images.append({
                                'url': download_url,
                                'type': img_type,
                                'filename': dataURI.split('/')[-1] if '/' in dataURI else dataURI
                            })
                            
                            # Stop after finding 3 previews to speed things up
                            if len(preview_images) >= 3:
                                break
                    
                    if preview_images:
                        return {
                            'obs_id': obs_id,
                            'mast_id': try_id,
                            'previews': preview_images,
                            'has_previews': len(preview_images) > 0
                        }
            except Exception as e:
                # Try next ID format
                print(f"Error querying {try_id}: {e}")
                continue
        
        # No previews found
        return {
            'obs_id': obs_id,
            'has_previews': False,
            'previews': []
        }
        
    except Exception as e:
        print(f"Error getting preview for {obs_id}: {e}")
        return None


def get_jwst_preview_from_obs_id(obs_id: str, timeout: int = 20) -> Optional[Dict]:
    """
    Get JWST preview images directly from observation ID using MAST API
    
    Parameters
    ----------
    obs_id : str
        JWST observation ID
    timeout : int, optional
        Query timeout in seconds (default: 20)
    
    Returns
    -------
    dict or None
        Dictionary with preview URLs and metadata
    """
    try:
        from astroquery.mast import Observations
        
        # Set timeout for MAST queries
        Observations.TIMEOUT = timeout
        
        # Query for this specific observation
        obs_table = Observations.query_criteria(obs_id=obs_id, obs_collection='JWST')
        
        if obs_table is not None and len(obs_table) > 0:
            # Get products for this observation
            products = Observations.get_product_list(obs_table[0])
            
            preview_images = []
            
            # Check first 10 products to save time
            for product in products[:10]:
                dataURI = product.get('dataURI', '')
                product_type = str(product.get('productType', '')).upper()
                
                if not dataURI:
                    continue
                
                # Look for image files
                is_image = False
                img_type = 'unknown'
                
                # Check file extension
                dataURI_lower = dataURI.lower()
                if '.jpg' in dataURI_lower or '.jpeg' in dataURI_lower:
                    is_image = True
                    img_type = 'JPEG preview'
                elif '.png' in dataURI_lower:
                    is_image = True
                    img_type = 'PNG preview'
                elif '.gif' in dataURI_lower:
                    is_image = True
                    img_type = 'GIF preview'
                
                # Also check if explicitly marked as PREVIEW type
                if product_type == 'PREVIEW':
                    is_image = True
                    if img_type == 'unknown':
                        img_type = 'Preview image'
                
                # Filter: Only keep i2d images (drizzled combined images)
                if is_image:
                    # Only accept i2d files (final drizzled products)
                    if '_i2d' not in dataURI_lower:
                        continue
                    
                    download_url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={dataURI}"
                    preview_images.append({
                        'url': download_url,
                        'type': img_type,
                        'filename': dataURI.split('/')[-1] if '/' in dataURI else dataURI
                    })
                    
                    # Stop after finding 3 previews
                    if len(preview_images) >= 3:
                        break
            
            if preview_images:
                return {
                    'obs_id': obs_id,
                    'previews': preview_images,
                    'has_previews': len(preview_images) > 0,
                    'telescope': 'JWST'
                }
        
        # No previews found
        return {
            'obs_id': obs_id,
            'has_previews': False,
            'previews': [],
            'telescope': 'JWST'
        }
        
    except Exception as e:
        print(f"Error getting JWST preview for {obs_id}: {e}")
        return None


def get_hst_and_jwst_images(
    ra: float,
    dec: float,
    radius: float = 5.0,
    max_images: int = 5,
    include_jwst: bool = True
) -> Optional[Dict[str, List[Dict]]]:
    """
    Get both HST and JWST images for comparison
    
    Parameters
    ----------
    ra : float
        Right Ascension in degrees
    dec : float
        Declination in degrees
    radius : float, optional
        Search radius in arcseconds
    max_images : int, optional
        Maximum number of images per telescope
    include_jwst : bool, optional
        Whether to include JWST data (default: True)
    
    Returns
    -------
    dict or None
        Dictionary with 'HST' and 'JWST' keys containing image lists
    """
    try:
        results = {}
        
        # Get HST images
        print("Querying HST...")
        hst_images = get_mast_hst_images(ra, dec, radius, max_images)
        if hst_images:
            results['HST'] = hst_images
            print(f"Found {len(hst_images)} HST images with previews")
        else:
            print("No HST images found")
        
        # Get JWST images if requested
        if include_jwst:
            print("\nQuerying JWST...")
            jwst_images = get_jwst_preview_images(ra, dec, radius, max_images)
            if jwst_images:
                results['JWST'] = jwst_images
                print(f"Found {len(jwst_images)} JWST images with previews")
            else:
                print("No JWST images found")
        
        return results if results else None
        
    except Exception as e:
        print(f"Error getting HST/JWST images: {e}")
        return None
