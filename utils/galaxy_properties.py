"""
Galaxy physical properties estimation utilities
"""
import numpy as np
from typing import Optional, Dict
from .line_fitting import LineResult


def estimate_stellar_mass(
    g_mag: float,
    r_mag: float,
    z: float = 0.0,
    method: str = 'taylor11'
) -> float:
    """
    Estimate stellar mass from optical colors
    
    Parameters
    ----------
    g_mag : float
        g-band magnitude
    r_mag : float
        r-band magnitude
    z : float, optional
        Redshift
    method : str, optional
        Method: 'taylor11' (Taylor et al. 2011) or 'bell03' (Bell et al. 2003)
    
    Returns
    -------
    float
        Log stellar mass (solar masses)
    
    Notes
    -----
    These are approximate relations for quick estimates.
    For accurate masses, use dedicated SED fitting codes.
    """
    # Distance modulus
    if z > 0:
        # Simple approximation (assumes flat ΛCDM, H0=70)
        from astropy.cosmology import FlatLambdaCDM
        cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
        d_L = cosmo.luminosity_distance(z).value  # Mpc
        dist_mod = 5 * np.log10(d_L * 1e6) - 5
    else:
        dist_mod = 0
    
    # Absolute magnitude
    M_r = r_mag - dist_mod
    
    # Color
    g_r = g_mag - r_mag
    
    if method == 'taylor11':
        # Taylor et al. (2011) - SDSS-based color-mass relation
        # log(M*/M☉) = -0.406 + 1.097(g-r) - 0.4M_r - 0.0158(g-r)²
        log_mass = -0.406 + 1.097 * g_r - 0.4 * M_r - 0.0158 * g_r**2
    elif method == 'bell03':
        # Bell et al. (2003) - simplified
        # log(M*/L) ≈ -0.4 + 1.0(g-r)
        log_M_L = -0.4 + 1.0 * g_r
        # M_r,sun ≈ 4.64
        M_sun_r = 4.64
        log_L = -0.4 * (M_r - M_sun_r)
        log_mass = log_M_L + log_L
    else:
        log_mass = 10.0  # Default fallback
    
    return log_mass


def estimate_sfr(
    ha_flux: float,
    ha_flux_err: Optional[float] = None,
    z: float = 0.0,
    method: str = 'kennicutt98'
) -> Dict[str, float]:
    """
    Estimate star formation rate from Hα emission
    
    Parameters
    ----------
    ha_flux : float
        Hα flux (erg/s/cm²)
    ha_flux_err : float, optional
        Hα flux error
    z : float, optional
        Redshift
    method : str, optional
        Calibration: 'kennicutt98' or 'kennicutt12'
    
    Returns
    -------
    dict
        {'sfr': value, 'sfr_err': error} in M☉/yr
    
    Notes
    -----
    Assumes no extinction correction. Apply extinction correction
    for accurate SFR estimates.
    """
    # Luminosity distance
    if z > 0:
        from astropy.cosmology import FlatLambdaCDM
        cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
        d_L = cosmo.luminosity_distance(z).to('cm').value
    else:
        d_L = 3.086e24  # 10 pc in cm (for local objects)
    
    # Hα luminosity
    L_ha = ha_flux * 4 * np.pi * d_L**2  # erg/s
    
    if method == 'kennicutt98':
        # Kennicutt (1998) calibration
        # SFR(M☉/yr) = 7.9×10^-42 × L(Hα) [erg/s]
        sfr = 7.9e-42 * L_ha
    elif method == 'kennicutt12':
        # Kennicutt & Evans (2012) - updated for Kroupa IMF
        # SFR(M☉/yr) = 5.5×10^-42 × L(Hα) [erg/s]
        sfr = 5.5e-42 * L_ha
    else:
        sfr = 7.9e-42 * L_ha
    
    # Error propagation
    if ha_flux_err is not None and ha_flux > 0:
        sfr_err = sfr * (ha_flux_err / ha_flux)
    else:
        sfr_err = 0.0
    
    return {
        'sfr': sfr,
        'sfr_err': sfr_err,
        'L_ha': L_ha
    }


def calculate_metallicity(
    line_results: Dict[str, LineResult],
    method: str = 'pp04_o3n2'
) -> Optional[Dict[str, float]]:
    """
    Estimate gas-phase metallicity from emission line ratios
    
    Parameters
    ----------
    line_results : dict
        Line fitting results
    method : str, optional
        Calibration method:
        - 'pp04_o3n2': Pettini & Pagel (2004) O3N2 index
        - 'pp04_n2': Pettini & Pagel (2004) N2 index
    
    Returns
    -------
    dict or None
        {'12+log(O/H)': value, 'error': error}
    """
    if method == 'pp04_o3n2':
        # O3N2 = ([OIII]5007/Hβ) / ([NII]6583/Hα)
        if ('OIII_5007' in line_results and 'Hbeta' in line_results and
            'NII_6583' in line_results and 'Halpha' in line_results):
            
            oiii = line_results['OIII_5007'].flux
            hb = line_results['Hbeta'].flux
            nii = line_results['NII_6583'].flux
            ha = line_results['Halpha'].flux
            
            if oiii > 0 and hb > 0 and nii > 0 and ha > 0:
                O3N2 = np.log10((oiii / hb) / (nii / ha))
                # PP04 calibration: 12+log(O/H) = 8.73 - 0.32 × O3N2
                metallicity = 8.73 - 0.32 * O3N2
                return {'12+log(O/H)': metallicity, 'method': 'O3N2'}
    
    elif method == 'pp04_n2':
        # N2 = [NII]6583/Hα
        if 'NII_6583' in line_results and 'Halpha' in line_results:
            nii = line_results['NII_6583'].flux
            ha = line_results['Halpha'].flux
            
            if nii > 0 and ha > 0:
                N2 = np.log10(nii / ha)
                # PP04 calibration: 12+log(O/H) = 8.90 + 0.57 × N2
                metallicity = 8.90 + 0.57 * N2
                return {'12+log(O/H)': metallicity, 'method': 'N2'}
    
    return None


def estimate_sersic_properties(
    petroR50: float,
    petroR90: float
) -> Dict[str, float]:
    """
    Estimate Sersic index and effective radius from Petrosian radii
    
    Parameters
    ----------
    petroR50 : float
        Petrosian radius containing 50% of light (arcsec)
    petroR90 : float
        Petrosian radius containing 90% of light (arcsec)
    
    Returns
    -------
    dict
        Estimated morphological parameters
    """
    # Concentration parameter
    C = petroR90 / petroR50 if petroR50 > 0 else 0
    
    # Rough Sersic index estimate
    # C ~ 2.5 for n=1 (exponential), C ~ 3.5-4 for n=4 (de Vaucouleurs)
    if C < 2.3:
        n_estimate = 1.0
        type_estimate = 'Late-type/Disk'
    elif C > 3.5:
        n_estimate = 4.0
        type_estimate = 'Early-type/Bulge'
    else:
        n_estimate = 2.0
        type_estimate = 'Intermediate'
    
    return {
        'concentration': C,
        'sersic_n_estimate': n_estimate,
        'morphology_type': type_estimate,
        'R_eff_estimate': petroR50
    }
