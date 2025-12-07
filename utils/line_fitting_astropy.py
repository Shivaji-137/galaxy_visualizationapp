"""
Improved emission line fitting using astropy.modeling

Uses SDSS spectral line database from HTML file for accurate rest wavelengths.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
import re

from astropy.modeling import models, fitting
from astropy import units as u


@dataclass
class LineResult:
    """Result from emission line fitting"""
    line_name: str
    center: float  # Observed wavelength
    center_err: float
    amplitude: float
    amplitude_err: float
    sigma: float  # Line width (stddev)
    sigma_err: float
    fwhm: float  # Full width half maximum
    flux: float  # Integrated flux
    flux_err: float
    ew: float  # Equivalent width
    ew_err: float
    snr: float  # Signal-to-noise ratio
    velocity: float  # Velocity offset from rest wavelength
    velocity_err: float
    continuum: float
    success: bool


def load_sdss_spectral_lines(html_file: str) -> Dict[str, Dict]:
    """
    Load spectral lines from SDSS HTML table
    
    Parameters
    ----------
    html_file : str
        Path to "Table of Spectral Lines Used in SDSS.html"
    
    Returns
    -------
    dict
        Dictionary with line name as key, properties as value
    """
    with open(html_file, 'r') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    
    lines = {}
    line_type = 'emission'  # Default
    
    # Mapping for Greek letters in Balmer series
    greek_map = {
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'ε': 'epsilon'
    }
    
    if table:
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            
            # Check for section headers
            if len(cells) == 1 and 'colspan' in cells[0].attrs:
                header = cells[0].text.strip().lower()
                if 'absorption' in header:
                    line_type = 'absorption'
                elif 'sky' in header:
                    line_type = 'sky'
                continue
            
            if len(cells) >= 4:
                try:
                    wavelength = float(cells[0].text.strip())
                    rel_height_gal = float(cells[1].text.strip())
                    rel_height_qso = float(cells[2].text.strip())
                    
                    # Get name from cell (handle img tags for Greek letters)
                    name_cell = cells[3]
                    name_parts = []
                    
                    # Process text and img tags
                    for item in name_cell.contents:
                        if isinstance(item, str):
                            name_parts.append(item.strip())
                        elif item.name == 'img':
                            # Greek letter image
                            alt = item.get('alt', '')
                            if alt in greek_map:
                                name_parts.append(greek_map[alt])
                    
                    name_raw = ''.join(name_parts).strip()
                    name = re.sub(r'\s+', ' ', name_raw)
                    
                    # Create standardized keys
                    key = name.replace(' ', '_').replace('[', '').replace(']', '')
                    
                    # Create common aliases
                    aliases = [key]
                    if 'Halpha' in key or 'H' in name and 'alpha' in name:
                        aliases.extend(['Halpha', 'Ha', 'H_alpha'])
                    elif 'Hbeta' in key or 'H' in name and 'beta' in name:
                        aliases.extend(['Hbeta', 'Hb', 'H_beta'])
                    elif 'Hgamma' in key or 'H' in name and 'gamma' in name:
                        aliases.extend(['Hgamma', 'Hg', 'H_gamma'])
                    elif 'Hdelta' in key or 'H' in name and 'delta' in name:
                        aliases.extend(['Hdelta', 'Hd', 'H_delta'])
                    
                    # Add with all aliases
                    line_data = {
                        'wavelength': wavelength,
                        'rel_height_gal': rel_height_gal,
                        'rel_height_qso': rel_height_qso,
                        'name': name,
                        'type': line_type
                    }
                    
                    for alias in aliases:
                        lines[alias] = line_data
                        
                except Exception as e:
                    pass
    
    return lines


def fit_emission_line_astropy(
    wavelength: np.ndarray,
    flux: np.ndarray,
    ivar: Optional[np.ndarray],
    rest_wavelength: float,
    line_name: str,
    z: float = 0.0,
    window: float = 20.0,
    continuum_order: int = 1
) -> LineResult:
    """
    Fit emission line using astropy.modeling
    
    Uses composite model: Gaussian line + polynomial continuum
    
    Parameters
    ----------
    wavelength : array
        Wavelength array (Angstroms)
    flux : array
        Flux array
    ivar : array, optional
        Inverse variance array (for weighting)
    rest_wavelength : float
        Rest-frame wavelength of the line
    line_name : str
        Name of the line
    z : float, optional
        Redshift (default: 0.0)
    window : float, optional
        Fitting window around line in Angstroms (default: 20)
    continuum_order : int, optional
        Polynomial order for continuum (0=constant, 1=linear, default: 1)
    
    Returns
    -------
    LineResult
        Fitting results
    """
    # Observed wavelength
    obs_wavelength = rest_wavelength * (1 + z)
    
    # Select region around line
    mask = (wavelength > obs_wavelength - window) & (wavelength < obs_wavelength + window)
    
    if np.sum(mask) < 5:
        return LineResult(
            line_name=line_name,
            center=obs_wavelength,
            center_err=0,
            amplitude=0,
            amplitude_err=0,
            sigma=0,
            sigma_err=0,
            fwhm=0,
            flux=0,
            flux_err=0,
            ew=0,
            ew_err=0,
            snr=0,
            velocity=0,
            velocity_err=0,
            continuum=0,
            success=False
        )
    
    wave_fit = wavelength[mask]
    flux_fit = flux[mask]
    
    # Weights from inverse variance
    if ivar is not None:
        ivar_fit = ivar[mask]
        weights = np.sqrt(ivar_fit)
        weights[~np.isfinite(weights)] = 0
        weights[weights == 0] = 1e-10
    else:
        weights = np.ones_like(flux_fit)
    
    # Build composite model
    # 1. Gaussian line
    gaussian = models.Gaussian1D(
        amplitude=np.max(flux_fit) - np.median(flux_fit),
        mean=obs_wavelength,
        stddev=3.0,  # Initial guess: 3 Angstroms
        name='line'
    )
    
    # Set bounds
    gaussian.amplitude.bounds = (0, None)  # Positive for emission
    gaussian.mean.bounds = (obs_wavelength - 10, obs_wavelength + 10)
    gaussian.stddev.bounds = (0.5, 15)  # Physical range for line widths
    
    # 2. Continuum (polynomial)
    if continuum_order == 0:
        continuum = models.Const1D(amplitude=np.median(flux_fit), name='cont')
    elif continuum_order == 1:
        # Linear continuum
        continuum = models.Polynomial1D(degree=1, name='cont')
        continuum.c0 = np.median(flux_fit)
        continuum.c1 = 0
    else:
        continuum = models.Polynomial1D(degree=continuum_order, name='cont')
        continuum.c0 = np.median(flux_fit)
    
    # Composite model
    model = gaussian + continuum
    
    # Fitter with robust algorithm
    fitter = fitting.LevMarLSQFitter()
    
    try:
        # Perform fit
        fitted_model = fitter(model, wave_fit, flux_fit, weights=weights, maxiter=1000)
        
        # Check if fit converged
        if not fitter.fit_info['ierr'] in [1, 2, 3, 4]:
            raise ValueError("Fit did not converge properly")
        
        # Extract Gaussian parameters
        amplitude = fitted_model['line'].amplitude.value
        center = fitted_model['line'].mean.value
        sigma = fitted_model['line'].stddev.value
        
        # Calculate errors from covariance matrix
        if hasattr(fitter.fit_info, 'param_cov') and fitter.fit_info['param_cov'] is not None:
            cov = fitter.fit_info['param_cov']
            # Order: amplitude, mean, stddev (first 3 params)
            amplitude_err = np.sqrt(cov[0, 0]) if cov[0, 0] > 0 else 0
            center_err = np.sqrt(cov[1, 1]) if cov[1, 1] > 0 else 0
            sigma_err = np.sqrt(cov[2, 2]) if cov[2, 2] > 0 else 0
        else:
            # Fallback: estimate from residuals
            residuals = flux_fit - fitted_model(wave_fit)
            rms = np.std(residuals)
            amplitude_err = rms
            center_err = sigma / np.sqrt(amplitude / rms)
            sigma_err = sigma * 0.1  # 10% error estimate
        
        # Continuum at line center
        continuum_at_center = fitted_model['cont'](center)
        
        # Calculate integrated flux
        # For Gaussian: Flux = amplitude * sigma * sqrt(2*pi)
        flux_integrated = amplitude * sigma * np.sqrt(2 * np.pi)
        flux_err = flux_integrated * np.sqrt(
            (amplitude_err / amplitude)**2 + (sigma_err / sigma)**2
        ) if amplitude > 0 and sigma > 0 else 0
        
        # FWHM = 2 * sqrt(2 * ln(2)) * sigma ≈ 2.355 * sigma
        fwhm = 2.355 * sigma
        
        # Equivalent width (negative for emission)
        ew = -flux_integrated / continuum_at_center if continuum_at_center > 0 else 0
        ew_err = np.abs(ew) * (flux_err / flux_integrated) if flux_integrated > 0 else 0
        
        # Signal-to-noise ratio
        residuals = flux_fit - fitted_model(wave_fit)
        snr = amplitude / np.std(residuals) if np.std(residuals) > 0 else 0
        
        # Velocity offset from expected position
        c = 299792.458  # km/s
        velocity = c * (center - obs_wavelength) / obs_wavelength
        velocity_err = c * center_err / obs_wavelength if obs_wavelength > 0 else 0
        
        return LineResult(
            line_name=line_name,
            center=center,
            center_err=center_err,
            amplitude=amplitude,
            amplitude_err=amplitude_err,
            sigma=sigma,
            sigma_err=sigma_err,
            fwhm=fwhm,
            flux=flux_integrated,
            flux_err=flux_err,
            ew=ew,
            ew_err=ew_err,
            snr=snr,
            velocity=velocity,
            velocity_err=velocity_err,
            continuum=continuum_at_center,
            success=True
        )
        
    except Exception as e:
        print(f"astropy.modeling fit failed for {line_name}: {e}")
        return LineResult(
            line_name=line_name,
            center=obs_wavelength,
            center_err=0,
            amplitude=0,
            amplitude_err=0,
            sigma=0,
            sigma_err=0,
            fwhm=0,
            flux=0,
            flux_err=0,
            ew=0,
            ew_err=0,
            snr=0,
            velocity=0,
            velocity_err=0,
            continuum=np.median(flux_fit) if len(flux_fit) > 0 else 0,
            success=False
        )


def fit_multiple_lines_astropy(
    wavelength: np.ndarray,
    flux: np.ndarray,
    ivar: Optional[np.ndarray],
    z: float = 0.0,
    lines: Optional[List[str]] = None,
    sdss_lines: Optional[Dict] = None
) -> Dict[str, LineResult]:
    """
    Fit multiple emission lines using astropy.modeling
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array
    ivar : array, optional
        Inverse variance
    z : float, optional
        Redshift
    lines : list, optional
        List of line names to fit
    sdss_lines : dict, optional
        SDSS spectral lines dictionary (from load_sdss_spectral_lines)
    
    Returns
    -------
    dict
        Dictionary mapping line names to LineResult objects
    """
    if sdss_lines is None:
        # Try to load from default location
        html_file = Path(__file__).parent.parent / "Table of Spectral Lines Used in SDSS.html"
        if html_file.exists():
            sdss_lines = load_sdss_spectral_lines(str(html_file))
        else:
            raise FileNotFoundError("SDSS spectral lines HTML file not found")
    
    # Default to common emission lines
    if lines is None:
        lines = ['H_α', 'H_β', 'H_γ', 'O_III', 'N_II', 'S_II', 'O_II']
    
    results = {}
    for line_name in lines:
        # Try to find in SDSS lines
        if line_name in sdss_lines:
            rest_wave = sdss_lines[line_name]['wavelength']
        else:
            # Try alternative naming
            alt_names = {
                'Halpha': 'H_α',
                'Hbeta': 'H_β',
                'Hgamma': 'H_γ',
                'OIII_5007': 'O_III',
                'NII_6583': 'N_II',
                'SII_6716': 'S_II',
                'OII_3727': 'O_II'
            }
            if line_name in alt_names:
                sdss_name = alt_names[line_name]
                if sdss_name in sdss_lines:
                    rest_wave = sdss_lines[sdss_name]['wavelength']
                else:
                    continue
            else:
                continue
        
        result = fit_emission_line_astropy(
            wavelength, flux, ivar,
            rest_wave, line_name, z
        )
        results[line_name] = result
    
    return results


# Load SDSS lines at module import
SDSS_LINES = {}
try:
    html_file = Path(__file__).parent.parent / "Table of Spectral Lines Used in SDSS.html"
    if html_file.exists():
        SDSS_LINES = load_sdss_spectral_lines(str(html_file))
        print(f"Loaded {len(SDSS_LINES)} spectral lines from SDSS database")
except Exception as e:
    print(f"Warning: Could not load SDSS spectral lines: {e}")
