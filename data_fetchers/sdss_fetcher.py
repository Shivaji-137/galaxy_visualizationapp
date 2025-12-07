"""
SDSS data fetcher module
Queries SDSS for imaging, photometry, and spectroscopy
"""
from typing import Optional, Dict
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.sdss import SDSS
from astropy.io import fits
import requests



# -------------------------------------------------------
# SDSS PHOTOMETRY FETCHER
# -------------------------------------------------------
def fetch_sdss_data(
    ra: Optional[float] = None,
    dec: Optional[float] = None,
    radius: float = 5.0,
    max_results: int = 100,
    photoobj_fields: Optional[list] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch SDSS photometric data
    """
    try:
        if ra is None or dec is None:
            return None
        
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        
        # Default fields
        if photoobj_fields is None:
            photoobj_fields = [
                'objID', 'ra', 'dec', 'type', 'mode',
                'u', 'g', 'r', 'i', 'z',
                'err_u', 'err_g', 'err_r', 'err_i', 'err_z',
                'petroMag_u', 'petroMag_g', 'petroMag_r', 'petroMag_i', 'petroMag_z',
                'petroRad_r', 'petroR50_r', 'petroR90_r',
                'modelMag_u', 'modelMag_g', 'modelMag_r', 'modelMag_i', 'modelMag_z',
                'specObjID', 'z', 'zErr', 'class'
            ]
        
        # Query SDSS
        result = SDSS.query_region(
            coord,
            radius=radius*u.arcsec,
            photoobj_fields=photoobj_fields,
            data_release=17
        )
        
        if result is None or len(result) == 0:
            return None
        
        # Convert to pandas
        df = result.to_pandas()
        return df
        
    except Exception as e:
        print(f"Error fetching SDSS data: {e}")
        return None



# -------------------------------------------------------
# UPDATED SPECTRUM FETCHER (MULTIPLE PIPELINES)
# -------------------------------------------------------
def fetch_sdss_spectrum(
    plate: int,
    mjd: int,
    fiberid: int,
    data_release: int = 17,
    verbose: bool = False
) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch SDSS spectrum by plate-MJD-fiber.
    First tries astroquery's get_spectra, then falls back to direct URL access.
    """

    # Try using astroquery's get_spectra method first
    try:
        if verbose:
            print(f"Trying astroquery SDSS.get_spectra for plate={plate}, mjd={mjd}, fiber={fiberid}")
        
        spectra = SDSS.get_spectra(plate=plate, mjd=mjd, fiberID=fiberid, data_release=data_release)
        
        if spectra and len(spectra) > 0:
            hdul = spectra[0]
            data = hdul[1].data
            
            wavelength = np.asarray(10 ** data['loglam'], dtype=np.float64)
            flux = np.asarray(data['flux'], dtype=np.float64)
            ivar = np.asarray(data['ivar'], dtype=np.float64)
            model = np.asarray(data['model'], dtype=np.float64) if 'model' in data.names else None
            
            if verbose:
                print(f"Successfully loaded spectrum via astroquery")
            
            return {
                'wavelength': wavelength,
                'flux': flux,
                'ivar': ivar,
                'model': model,
                'plate': plate,
                'mjd': mjd,
                'fiberid': fiberid,
                'source': 'astroquery'
            }
    except Exception as e:
        if verbose:
            print(f"Astroquery method failed: {e}, trying direct URL access...")

    # Fallback: Known pipelines for SDSS DR17 (BOSS and legacy)
    # Redux 26 = SDSS legacy, 103/104 = BOSS
    redux_versions = ["v5_13_2", "v5_13_0", "26", "103", "104"]

    for redux in redux_versions:
        # Try both boss and sdss paths
        paths = [
            f"https://data.sdss.org/sas/dr{data_release}/eboss/spectro/redux/{redux}/spectra/lite/{plate:04d}/spec-{plate:04d}-{mjd}-{fiberid:04d}.fits",
            f"https://data.sdss.org/sas/dr{data_release}/sdss/spectro/redux/{redux}/spectra/lite/{plate:04d}/spec-{plate:04d}-{mjd}-{fiberid:04d}.fits"
        ]

        for url in paths:
            if verbose:
                print(f"Trying URL: {url}")

            try:
                response = requests.get(url, timeout=20)

                if response.status_code != 200:
                    continue

                # Read FITS from bytes
                from io import BytesIO
                hdul = fits.open(BytesIO(response.content))

                data = hdul[1].data
                wavelength = np.asarray(10 ** data['loglam'], dtype=np.float64)
                flux = np.asarray(data['flux'], dtype=np.float64)
                ivar = np.asarray(data['ivar'], dtype=np.float64)
                model = np.asarray(data['model'], dtype=np.float64) if 'model' in data.names else None

                hdul.close()

                if verbose:
                    print(f"Loaded spectrum successfully from {url}")

                return {
                    'wavelength': wavelength,
                    'flux': flux,
                    'ivar': ivar,
                    'model': model,
                    'plate': plate,
                    'mjd': mjd,
                    'fiberid': fiberid,
                    'redux': redux,
                    'source': 'direct_url'
                }

            except requests.exceptions.Timeout:
                if verbose:
                    print("Timeout while contacting SDSS server.")
                continue

            except Exception as e:
                if verbose:
                    print(f"Error reading SDSS spectrum: {e}")
                continue

    if verbose:
        print("Spectrum not found in any available pipelines.")

    return None



# -------------------------------------------------------
# SPECTRUM FETCHER BY SKY COORDINATES
# -------------------------------------------------------
def fetch_sdss_spectrum_by_coords(
    ra: float,
    dec: float,
    radius: float = 3.0,
    use_demo: bool = True,
    verbose: bool = False
) -> Optional[Dict[str, np.ndarray]]:
    """
    Fetch SDSS spectrum closest to given coordinates.
    Uses astroquery's get_spectra with coordinates directly (per PDF docs).
    Optionally returns demo AGN spectrum if no SDSS match.
    """

    # Demo case for NGC 4151
    if use_demo and abs(ra - 182.6357) < 0.01 and abs(dec - 39.4058) < 0.01:
        print("Using demo NGC 4151 data...")
        from .demo_data import generate_demo_spectrum
        return generate_demo_spectrum('seyfert', z=0.0033)
    
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')

        # Method 1: Try get_spectra directly with coordinates (recommended in PDF)
        if verbose:
            print(f"Trying get_spectra with coordinates (ra={ra}, dec={dec}, radius={radius}\")")
        
        try:
            spectra_list = SDSS.get_spectra(
                coordinates=coord,
                radius=radius*u.arcsec,
                data_release=17
            )
            
            if spectra_list and len(spectra_list) > 0:
                # Get first spectrum
                hdul = spectra_list[0]
                data = hdul[1].data
                
                wavelength = np.asarray(10 ** data['loglam'], dtype=np.float64)
                flux = np.asarray(data['flux'], dtype=np.float64)
                ivar = np.asarray(data['ivar'], dtype=np.float64)
                model = np.asarray(data['model'], dtype=np.float64) if 'model' in data.names else None
                
                # Extract metadata from header
                header = hdul[0].header
                plate = header.get('PLATEID', 0)
                mjd = header.get('MJD', 0)
                fiberid = header.get('FIBERID', 0)
                
                if verbose:
                    print(f"✓ Got spectrum via coordinates: plate={plate}, mjd={mjd}, fiber={fiberid}")
                
                return {
                    'wavelength': wavelength,
                    'flux': flux,
                    'ivar': ivar,
                    'model': model,
                    'plate': plate,
                    'mjd': mjd,
                    'fiberid': fiberid,
                    'source': 'get_spectra_coords'
                }
        except Exception as e:
            if verbose:
                print(f"get_spectra with coordinates failed: {e}")

        # Method 2: Query spectroscopic objects, then download
        if verbose:
            print("Trying query_region with spectro=True...")
            
        result = SDSS.query_region(
            coord,
            radius=radius*u.arcsec,
            spectro=True,
            data_release=17
        )

        if result is None or len(result) == 0:
            # Try querying specobj table directly
            if verbose:
                print("No spectro match, trying query_specobj...")
            
            try:
                result = SDSS.query_specobj(coord, radius=radius*u.arcsec, data_release=17)
            except:
                result = None
        
        if result is None or len(result) == 0:
            if verbose:
                print("No SDSS spectrum found in catalog.")
            if use_demo:
                print("Using demo dataset instead.")
                from .demo_data import generate_demo_spectrum
                return generate_demo_spectrum('seyfert', z=0.01)
            return None

        # Pick the first entry with a valid spectrum
        for row in result:
            # Check for valid specObjID
            spec_id = row.get('specObjID', row.get('specobjid', 0))
            if spec_id > 0:
                plate = row['plate']
                mjd = row['mjd']
                # Handle both fiberID and fiberid
                fiberid = row.get('fiberID', row.get('fiberid', row.get('fiber', None)))
                
                if fiberid is None:
                    continue
                
                if verbose:
                    print(f"Found spectrum metadata: plate={plate}, mjd={mjd}, fiber={fiberid}")
                
                spectrum = fetch_sdss_spectrum(
                    plate, mjd, fiberid, verbose=verbose
                )
                
                if spectrum is not None:
                    return spectrum
        
        if verbose:
            print("No valid spectrum could be downloaded.")
        
        return None

    except Exception as e:
        print(f"Error fetching SDSS spectrum by coordinates: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None
