"""
Emission and absorption line fitting utilities

Uses lmfit for robust emission line fitting with proper models and constraints.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import numpy as np
from scipy.optimize import curve_fit
from lmfit import models, Parameters, Model


@dataclass
class LineResult:
    """Result from emission line fitting"""
    line_name: str
    center: float  # Observed wavelength
    center_err: float
    amplitude: float
    amplitude_err: float
    sigma: float  # Line width
    sigma_err: float
    flux: float  # Integrated flux
    flux_err: float
    ew: float  # Equivalent width
    ew_err: float
    snr: float  # Signal-to-noise ratio
    velocity: float  # Velocity offset from rest wavelength
    velocity_err: float
    continuum: float
    success: bool


def gaussian(x: np.ndarray, amplitude: float, center: float, sigma: float, continuum: float = 0) -> np.ndarray:
    """
    Gaussian function for line fitting
    
    Parameters
    ----------
    x : array
        Wavelength array
    amplitude : float
        Gaussian amplitude
    center : float
        Line center
    sigma : float
        Line width
    continuum : float
        Continuum level
    
    Returns
    -------
    array
        Gaussian profile
    """
    return amplitude * np.exp(-(x - center)**2 / (2 * sigma**2)) + continuum


def fit_emission_line_lmfit(
    wavelength: np.ndarray,
    flux: np.ndarray,
    ivar: Optional[np.ndarray],
    rest_wavelength: float,
    line_name: str,
    z: float = 0.0,
    window: float = 20.0,
    model_type: str = 'gaussian'
) -> LineResult:
    """
    Fit emission line using lmfit (more robust than scipy curve_fit)
    
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
    model_type : str, optional
        'gaussian', 'lorentzian', or 'voigt' (default: 'gaussian')
    
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
        weights[~np.isfinite(weights)] = 1e-10
        weights[weights == 0] = 1e-10
    else:
        weights = np.ones_like(flux_fit)
    
    # Build composite model: Line + Linear continuum
    if model_type == 'gaussian':
        line_model = models.GaussianModel(prefix='line_')
    elif model_type == 'lorentzian':
        line_model = models.LorentzianModel(prefix='line_')
    elif model_type == 'voigt':
        line_model = models.VoigtModel(prefix='line_')
    else:
        line_model = models.GaussianModel(prefix='line_')
    
    # Add linear continuum
    continuum_model = models.LinearModel(prefix='cont_')
    model = line_model + continuum_model
    
    # Set up parameters with physical constraints
    params = model.make_params()
    
    # Continuum parameters (linear: slope + intercept)
    continuum_level = np.median(flux_fit)
    params['cont_slope'].set(value=0, min=-1e-2, max=1e-2)
    params['cont_intercept'].set(value=continuum_level, min=0)
    
    # Line parameters
    amplitude_guess = np.max(flux_fit) - continuum_level
    sigma_guess = 3.0  # Angstroms, reasonable for optical spectra
    
    params['line_center'].set(value=obs_wavelength, min=obs_wavelength-10, max=obs_wavelength+10)
    params['line_amplitude'].set(value=amplitude_guess, min=0)
    params['line_sigma'].set(value=sigma_guess, min=0.5, max=15)
    
    if model_type == 'voigt':
        params['line_gamma'].set(value=sigma_guess, min=0.1, max=15)
    
    try:
        # Perform fit
        result = model.fit(flux_fit, params, x=wave_fit, weights=weights, method='leastsq')
        
        if not result.success:
            raise ValueError("Fit did not converge")
        
        # Extract results
        center = result.params['line_center'].value
        center_err = result.params['line_center'].stderr if result.params['line_center'].stderr else 0
        amplitude = result.params['line_amplitude'].value
        amplitude_err = result.params['line_amplitude'].stderr if result.params['line_amplitude'].stderr else 0
        sigma = result.params['line_sigma'].value
        sigma_err = result.params['line_sigma'].stderr if result.params['line_sigma'].stderr else 0
        
        # Continuum at line center
        continuum = result.params['cont_intercept'].value + result.params['cont_slope'].value * center
        
        # Calculate integrated flux (Gaussian: A * sigma * sqrt(2*pi))
        if model_type == 'gaussian':
            flux_integrated = amplitude * sigma * np.sqrt(2 * np.pi)
        elif model_type == 'lorentzian':
            flux_integrated = amplitude * sigma * np.pi
        else:  # voigt - approximate
            flux_integrated = amplitude * sigma * np.sqrt(2 * np.pi)
        
        flux_err = flux_integrated * np.sqrt(
            (amplitude_err/amplitude)**2 + (sigma_err/sigma)**2
        ) if amplitude > 0 and sigma > 0 else 0
        
        # Equivalent width
        ew = -flux_integrated / continuum if continuum > 0 else 0
        ew_err = np.abs(ew) * (flux_err / flux_integrated) if flux_integrated > 0 else 0
        
        # Signal-to-noise
        residuals = flux_fit - result.best_fit
        snr = amplitude / np.std(residuals) if np.std(residuals) > 0 else 0
        
        # Velocity offset
        c = 299792.458  # km/s
        velocity = c * (center - obs_wavelength) / obs_wavelength
        velocity_err = c * center_err / obs_wavelength
        
        return LineResult(
            line_name=line_name,
            center=center,
            center_err=center_err,
            amplitude=amplitude,
            amplitude_err=amplitude_err,
            sigma=sigma,
            sigma_err=sigma_err,
            flux=flux_integrated,
            flux_err=flux_err,
            ew=ew,
            ew_err=ew_err,
            snr=snr,
            velocity=velocity,
            velocity_err=velocity_err,
            continuum=continuum,
            success=True
        )
        
    except Exception as e:
        print(f"lmfit fitting failed for {line_name}: {e}")
        return LineResult(
            line_name=line_name,
            center=obs_wavelength,
            center_err=0,
            amplitude=0,
            amplitude_err=0,
            sigma=0,
            sigma_err=0,
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


def fit_emission_line(
    wavelength: np.ndarray,
    flux: np.ndarray,
    ivar: Optional[np.ndarray],
    rest_wavelength: float,
    line_name: str,
    z: float = 0.0,
    window: float = 20.0,
    fit_continuum: bool = True,
    use_lmfit: bool = True
) -> LineResult:
    """
    Fit a single emission line with Gaussian profile
    
    NOW USES LMFIT BY DEFAULT for better accuracy!
    
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
        Name of the line (e.g., 'Ha', 'OIII_5007')
    z : float, optional
        Redshift (default: 0.0)
    window : float, optional
        Fitting window around line in Angstroms (default: 20)
    fit_continuum : bool, optional
        Whether to fit continuum (default: True)
    use_lmfit : bool, optional
        Use lmfit (better) vs scipy curve_fit (default: True)
    
    Returns
    -------
    LineResult
        Fitting results
    """
    # Use improved lmfit version by default
    if use_lmfit:
        return fit_emission_line_lmfit(
            wavelength, flux, ivar, rest_wavelength, line_name, z, window
        )
    
    # Fallback to old scipy version (kept for compatibility)
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
    
    # Weights
    if ivar is not None:
        ivar_fit = ivar[mask]
        weights = np.sqrt(ivar_fit)
        weights[~np.isfinite(weights)] = 0
    else:
        weights = None
    
    # Initial guesses
    continuum_guess = np.median(flux_fit)
    amplitude_guess = np.max(flux_fit) - continuum_guess
    sigma_guess = 2.0  # Angstroms
    
    try:
        if fit_continuum:
            p0 = [amplitude_guess, obs_wavelength, sigma_guess, continuum_guess]
            popt, pcov = curve_fit(
                gaussian,
                wave_fit,
                flux_fit,
                p0=p0,
                sigma=1/weights if weights is not None else None,
                absolute_sigma=True,
                maxfev=5000
            )
            amplitude, center, sigma, continuum = popt
            perr = np.sqrt(np.diag(pcov))
        else:
            def gauss_no_cont(x, amp, cent, sig):
                return gaussian(x, amp, cent, sig, continuum_guess)
            
            p0 = [amplitude_guess, obs_wavelength, sigma_guess]
            popt, pcov = curve_fit(
                gauss_no_cont,
                wave_fit,
                flux_fit - continuum_guess,
                p0=p0,
                sigma=1/weights if weights is not None else None,
                absolute_sigma=True,
                maxfev=5000
            )
            amplitude, center, sigma = popt
            continuum = continuum_guess
            perr = np.sqrt(np.diag(pcov))
            perr = np.append(perr, 0)  # No error for fixed continuum
        
        # Calculate derived quantities
        flux_integrated = amplitude * sigma * np.sqrt(2 * np.pi)
        flux_err = flux_integrated * np.sqrt(
            (perr[0]/amplitude)**2 + (perr[2]/sigma)**2
        ) if amplitude > 0 and sigma > 0 else 0
        
        # Equivalent width (negative for emission)
        ew = -flux_integrated / continuum if continuum > 0 else 0
        ew_err = np.abs(ew) * np.sqrt(
            (flux_err/flux_integrated)**2 + (perr[3]/continuum)**2
        ) if flux_integrated > 0 and continuum > 0 else 0
        
        # Signal-to-noise
        snr = amplitude / np.std(flux_fit - gaussian(wave_fit, *popt))
        
        # Velocity offset
        c = 299792.458  # km/s
        velocity = c * (center - obs_wavelength) / obs_wavelength
        velocity_err = c * perr[1] / obs_wavelength
        
        return LineResult(
            line_name=line_name,
            center=center,
            center_err=perr[1],
            amplitude=amplitude,
            amplitude_err=perr[0],
            sigma=sigma,
            sigma_err=perr[2],
            flux=flux_integrated,
            flux_err=flux_err,
            ew=ew,
            ew_err=ew_err,
            snr=snr,
            velocity=velocity,
            velocity_err=velocity_err,
            continuum=continuum,
            success=True
        )
        
    except Exception as e:
        print(f"Line fitting failed for {line_name}: {e}")
        return LineResult(
            line_name=line_name,
            center=obs_wavelength,
            center_err=0,
            amplitude=0,
            amplitude_err=0,
            sigma=0,
            sigma_err=0,
            flux=0,
            flux_err=0,
            ew=0,
            ew_err=0,
            snr=0,
            velocity=0,
            velocity_err=0,
            continuum=continuum_guess,
            success=False
        )


# Common emission lines (rest wavelengths in Angstroms)
# Complete SDSS spectral line database (vacuum wavelengths in Angstroms)
EMISSION_LINES = {
    # UV lines (important for high-z quasars)
    'OVI_1034': 1033.82,
    'Lyalpha': 1215.24,
    'NV_1241': 1240.81,
    'OI_1306': 1305.53,
    'CII_1335': 1335.31,
    'SiIV_1398': 1397.61,
    'SiIV_OIV_1400': 1399.8,
    'CIV_1549': 1549.48,
    'HeII_1640': 1640.4,
    'OIII_1666': 1665.85,
    'AlIII_1857': 1857.4,
    'CIII_1909': 1908.734,
    'CII_2326': 2326.0,
    'NeIV_2439': 2439.5,
    'MgII_2799': 2799.117,
    # Optical lines
    'NeV_3346': 3346.79,
    'NeVI_3427': 3426.85,
    'OII_3727': 3727.092,
    'OII_3729': 3729.875,
    'HeI_3889': 3889.0,
    'SII_4072': 4072.3,
    'Hdelta': 4102.89,
    'Hgamma': 4341.68,
    'OIII_4363': 4364.436,
    'Hbeta': 4862.68,
    'OIII_4933': 4932.603,
    'OIII_4959': 4960.295,
    'OIII_5007': 5008.24,
    'OI_6300': 6302.046,
    'OI_6365': 6365.536,
    'NI_6529': 6529.03,
    'NII_6548': 6549.86,
    'Halpha': 6564.61,
    'NII_6583': 6585.27,
    'SII_6716': 6718.29,
    'SII_6731': 6732.67,
}

# Absorption lines (typically in galaxy spectra)
ABSORPTION_LINES = {
    'CaII_K': 3934.777,    # Ca II K line
    'CaII_H': 3969.588,    # Ca II H line  
    'G_band': 4305.61,     # CH G-band
    'Mg_5177': 5176.7,     # Mg I b triplet
    'Na_D': 5895.6,        # Na I D doublet
    'CaII_8500': 8500.36,  # Ca II triplet
    'CaII_8544': 8544.44,
    'CaII_8664': 8664.52,
}

# Line priorities for display (higher = more important, based on SDSS weights)
LINE_PRIORITIES = {
    # Highest priority (weight 8-10)
    'Halpha': 10,
    'Lyalpha': 10,
    'Hbeta': 9,
    'OIII_5007': 9,
    'CIV_1549': 9,
    'MgII_2799': 9,
    # High priority (weight 5-7)
    'CIII_1909': 8,
    'NII_6583': 8,
    'OII_3727': 8,
    'OIII_4959': 7,
    'Hgamma': 7,
    'NV_1241': 7,
    # Medium priority (weight 2-4)
    'SII_6716': 6,
    'SII_6731': 6,
    'NII_6548': 6,
    'Hgamma': 6,
    'Hdelta': 5,
    'OII_3729': 5,
    # Lower priority
    'OI_6300': 4,
    'OIII_4363': 4,
    'HeI_3889': 3,
    'OVI_1034': 3,
    'OIII_4933': 3,
    'OI_6365': 3,
    'NI_6529': 2,
    'SII_4072': 2,
    # UV lines
    'HeII_1640': 5,
    'OI_1306': 2,
    'CII_1335': 2,
    'SiIV_1398': 4,
    'SiIV_OIV_1400': 4,
    'OIII_1666': 2,
    'AlIII_1857': 2,
    'CII_2326': 2,
    'NeIV_2439': 3,
    'NeV_3346': 3,
    'NeVI_3427': 3,
    # Absorption lines
    'Na_D': 7,
    'CaII_K': 6,
    'CaII_H': 6,
    'Mg_5177': 5,
    'G_band': 5,
    'CaII_8500': 4,
    'CaII_8544': 4,
    'CaII_8664': 4,
}

# Color mapping for each emission line
LINE_COLORS = {
    # Balmer series (red to blue)
    'Halpha': '#FF0000',       # Red
    'Hbeta': '#0000FF',        # Blue
    'Hgamma': '#00BFFF',       # Deep Sky Blue
    'Hdelta': '#87CEEB',       # Sky Blue
    # Oxygen lines (greens and oranges)
    'OII_3727': '#00FF00',     # Lime Green
    'OII_3729': '#32CD32',     # Lime Green (slightly darker)
    'OIII_4363': '#FFA500',    # Orange
    'OIII_4933': '#FF7F00',    # Dark Orange
    'OIII_4959': '#FF8C00',    # Dark Orange
    'OIII_5007': '#FF6600',    # Orange Red
    'OI_6300': '#FFD700',      # Gold
    'OI_6365': '#DAA520',      # Goldenrod
    'OIII_1666': '#FFA07A',    # Light Salmon
    'OI_1306': '#F0E68C',      # Khaki
    'OVI_1034': '#FFFFE0',     # Light Yellow
    # Nitrogen lines (pinks and magentas)
    'NII_6548': '#FF1493',     # Deep Pink
    'NII_6583': '#FF00FF',     # Magenta
    'NI_6529': '#FF69B4',      # Hot Pink
    'NV_1241': '#DB7093',      # Pale Violet Red
    # Sulfur lines (purples)
    'SII_6716': '#8B008B',     # Dark Magenta
    'SII_6731': '#9932CC',     # Dark Orchid
    'SII_4072': '#BA55D3',     # Medium Orchid
    # Carbon lines (cyans and teals)
    'CIV_1549': '#00CED1',     # Dark Turquoise
    'CIII_1909': '#00FFFF',    # Cyan
    'CII_1335': '#40E0D0',     # Turquoise
    'CII_2326': '#48D1CC',     # Medium Turquoise
    # Silicon lines
    'SiIV_1398': '#4169E1',    # Royal Blue
    'SiIV_OIV_1400': '#4682B4', # Steel Blue
    # Other UV/optical lines
    'Lyalpha': '#E6E6FA',      # Lavender
    'MgII_2799': '#20B2AA',    # Light Sea Green
    'HeI_3889': '#FFB6C1',     # Light Pink
    'HeII_1640': '#FFC0CB',    # Pink
    'AlIII_1857': '#B0C4DE',   # Light Steel Blue
    'NeIV_2439': '#FF6347',    # Tomato
    'NeV_3346': '#FF4500',     # Orange Red
    'NeVI_3427': '#DC143C',    # Crimson
}


def fit_multiple_lines(
    wavelength: np.ndarray,
    flux: np.ndarray,
    ivar: Optional[np.ndarray],
    z: float = 0.0,
    lines: Optional[List[str]] = None
) -> Dict[str, LineResult]:
    """
    Fit multiple emission lines
    
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
        List of line names to fit (default: all common lines)
    
    Returns
    -------
    dict
        Dictionary mapping line names to LineResult objects
    """
    if lines is None:
        lines = list(EMISSION_LINES.keys())
    
    results = {}
    for line_name in lines:
        if line_name in EMISSION_LINES:
            rest_wave = EMISSION_LINES[line_name]
            result = fit_emission_line(
                wavelength, flux, ivar,
                rest_wave, line_name, z
            )
            results[line_name] = result
    
    return results
