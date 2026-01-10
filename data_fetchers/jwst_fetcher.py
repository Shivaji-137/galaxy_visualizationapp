"""
JWST (James Webb Space Telescope) data fetcher module
Query and retrieve images from JWST using MAST archive
"""
from typing import Optional, Dict, List, Tuple
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.mast import Observations
import requests
from io import BytesIO
from PIL import Image


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
                    
                    if is_preview:
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
                
                if is_image:
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


def list_jwst_instruments():
    """
    List all available JWST instruments
    
    Returns
    -------
    list
        List of instrument names
    """
    return ['NIRCAM', 'NIRSPEC', 'MIRI', 'NIRISS', 'FGS']


def get_jwst_filters(instrument: str) -> List[str]:
    """
    Get available filters for a JWST instrument
    
    Parameters
    ----------
    instrument : str
        Instrument name (NIRCAM, MIRI, NIRISS)
    
    Returns
    -------
    list
        List of filter names
    """
    filters = {
        'NIRCAM': [
            'F070W', 'F090W', 'F115W', 'F150W', 'F200W',  # Short wavelength
            'F277W', 'F356W', 'F444W',  # Long wavelength
            'F140M', 'F162M', 'F182M', 'F210M',  # Medium band
            'F164N', 'F187N', 'F212N'  # Narrow band
        ],
        'MIRI': [
            'F560W', 'F770W', 'F1000W', 'F1130W', 'F1280W',
            'F1500W', 'F1800W', 'F2100W', 'F2550W'
        ],
        'NIRISS': [
            'F090W', 'F115W', 'F140M', 'F150W', 'F158M',
            'F200W', 'F277W', 'F356W', 'F380M', 'F430M', 'F444W', 'F480M'
        ],
        'NIRSPEC': ['CLEAR', 'F070LP', 'F100LP', 'F170LP', 'F290LP'],
        'FGS': ['FGS']
    }
    
    return filters.get(instrument.upper(), [])


def get_jwst_famous_targets() -> Dict[str, Tuple[float, float]]:
    """
    Get coordinates of famous JWST targets
    
    Returns
    -------
    dict
        Dictionary mapping target names to (RA, Dec) in degrees
    """
    targets = {
        'Cartwheel Galaxy': (9.4333, -33.7128),
        'Stephan\'s Quintet': (339.0129, 33.9589),
        'Carina Nebula': (161.265, -59.866),
        'Southern Ring Nebula': (151.761, -40.444),
        'SMACS 0723': (110.841, -73.453),
        'Tarantula Nebula': (84.678, -69.103),
        'NGC 628': (24.1739, 15.7839),
        'NGC 7496': (348.3542, -43.4269),
        'Phantom Galaxy (NGC 628)': (24.1739, 15.7839),
        'WASP-96b': (345.7679, -23.8156),
        'Jupiter': None,  # Moving target
        'Neptune': None,  # Moving target
    }
    return targets


def download_jwst_image(preview_url: str, save_path: Optional[str] = None) -> Optional[Image.Image]:
    """
    Download JWST preview image from URL
    
    Parameters
    ----------
    preview_url : str
        URL to preview image
    save_path : str, optional
        Path to save the image (if None, returns PIL Image)
    
    Returns
    -------
    PIL.Image or None
        Downloaded image
    """
    try:
        response = requests.get(preview_url, timeout=30)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            
            if save_path:
                img.save(save_path)
                print(f"Saved image to {save_path}")
            
            return img
        else:
            print(f"Failed to download image: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error downloading JWST image: {e}")
        return None
