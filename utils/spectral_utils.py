"""
Spectral analysis utilities
"""
import numpy as np
from scipy.signal import medfilt, savgol_filter
from typing import Tuple, Optional


def smooth_spectrum(
    wavelength: np.ndarray,
    flux: np.ndarray,
    method: str = 'savgol',
    window: int = 11,
    **kwargs
) -> np.ndarray:
    """
    Smooth a spectrum
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array
    method : str, optional
        Smoothing method: 'savgol', 'median', 'boxcar' (default: 'savgol')
    window : int, optional
        Window size (default: 11)
    **kwargs
        Additional arguments for smoothing functions
    
    Returns
    -------
    array
        Smoothed flux
    """
    if method == 'savgol':
        polyorder = kwargs.get('polyorder', 3)
        return savgol_filter(flux, window, polyorder)
    elif method == 'median':
        return medfilt(flux, kernel_size=window)
    elif method == 'boxcar':
        kernel = np.ones(window) / window
        return np.convolve(flux, kernel, mode='same')
    else:
        return flux


def calculate_snr(
    flux: np.ndarray,
    ivar: Optional[np.ndarray] = None,
    wavelength_range: Optional[Tuple[float, float]] = None,
    wavelength: Optional[np.ndarray] = None
) -> float:
    """
    Calculate signal-to-noise ratio
    
    Parameters
    ----------
    flux : array
        Flux array
    ivar : array, optional
        Inverse variance array
    wavelength_range : tuple, optional
        (min, max) wavelength range to calculate SNR
    wavelength : array, optional
        Wavelength array (required if wavelength_range is specified)
    
    Returns
    -------
    float
        Signal-to-noise ratio
    """
    if wavelength_range is not None and wavelength is not None:
        mask = (wavelength >= wavelength_range[0]) & (wavelength <= wavelength_range[1])
        flux = flux[mask]
        if ivar is not None:
            ivar = ivar[mask]
    
    if ivar is not None:
        # Use inverse variance
        var = 1.0 / (ivar + 1e-10)
        noise = np.sqrt(np.median(var[var > 0]))
        signal = np.median(flux)
    else:
        # Estimate from flux scatter
        signal = np.median(flux)
        noise = np.std(flux)
    
    return signal / noise if noise > 0 else 0


def measure_continuum(
    wavelength: np.ndarray,
    flux: np.ndarray,
    method: str = 'median',
    windows: Optional[list] = None
) -> np.ndarray:
    """
    Measure continuum level
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array
    method : str, optional
        Method: 'median', 'percentile', 'polynomial' (default: 'median')
    windows : list, optional
        List of (min, max) wavelength ranges for continuum estimation
    
    Returns
    -------
    array
        Continuum estimate
    """
    if windows is not None:
        # Use specified continuum windows
        mask = np.zeros(len(wavelength), dtype=bool)
        for wmin, wmax in windows:
            mask |= (wavelength >= wmin) & (wavelength <= wmax)
        continuum_flux = flux[mask]
        continuum_level = np.median(continuum_flux)
        return np.full_like(flux, continuum_level)
    
    if method == 'median':
        # Simple median
        return np.full_like(flux, np.median(flux))
    
    elif method == 'percentile':
        # Lower percentile (avoid emission lines)
        percentile = 25
        return np.full_like(flux, np.percentile(flux, percentile))
    
    elif method == 'polynomial':
        # Polynomial fit to lower envelope
        from scipy.interpolate import UnivariateSpline
        # Iterative sigma clipping
        continuum = np.copy(flux)
        for _ in range(3):
            spline = UnivariateSpline(wavelength, continuum, k=3, s=len(wavelength))
            fit = spline(wavelength)
            residual = flux - fit
            sigma = np.std(residual)
            mask = residual < 2 * sigma
            continuum = np.where(mask, flux, fit)
        return fit
    
    else:
        return np.full_like(flux, np.median(flux))


def redshift_spectrum(
    wavelength: np.ndarray,
    flux: np.ndarray,
    z: float,
    to_rest: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert spectrum between observed and rest frame
    
    Parameters
    ----------
    wavelength : array
        Wavelength array
    flux : array
        Flux array
    z : float
        Redshift
    to_rest : bool, optional
        If True, convert to rest frame; if False, convert to observed (default: True)
    
    Returns
    -------
    tuple
        (wavelength, flux) in target frame
    """
    if to_rest:
        # Observed to rest
        wave_out = wavelength / (1 + z)
        flux_out = flux * (1 + z)  # Flux density correction
    else:
        # Rest to observed
        wave_out = wavelength * (1 + z)
        flux_out = flux / (1 + z)
    
    return wave_out, flux_out
