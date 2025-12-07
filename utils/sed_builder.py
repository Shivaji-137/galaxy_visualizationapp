"""
SED (Spectral Energy Distribution) builder utilities
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple


# Filter effective wavelengths (Angstroms) and zero points
FILTER_INFO = {
    # SDSS
    'sdss_u': {'wave': 3551, 'zp_ab': 0.0},
    'sdss_g': {'wave': 4686, 'zp_ab': 0.0},
    'sdss_r': {'wave': 6165, 'zp_ab': 0.0},
    'sdss_i': {'wave': 7481, 'zp_ab': 0.0},
    'sdss_z': {'wave': 8931, 'zp_ab': 0.0},
    # Pan-STARRS
    'ps_g': {'wave': 4866, 'zp_ab': 0.0},
    'ps_r': {'wave': 6215, 'zp_ab': 0.0},
    'ps_i': {'wave': 7545, 'zp_ab': 0.0},
    'ps_z': {'wave': 8679, 'zp_ab': 0.0},
    'ps_y': {'wave': 9633, 'zp_ab': 0.0},
    # 2MASS
    '2mass_J': {'wave': 12350, 'zp_ab': 0.0},
    '2mass_H': {'wave': 16620, 'zp_ab': 0.0},
    '2mass_K': {'wave': 21590, 'zp_ab': 0.0},
    # Gaia
    'gaia_G': {'wave': 6730, 'zp_ab': 0.0},
    'gaia_BP': {'wave': 5320, 'zp_ab': 0.0},
    'gaia_RP': {'wave': 7970, 'zp_ab': 0.0},
}


def mag_to_flux(magnitude: float, wavelength: float, mag_err: Optional[float] = None) -> Tuple[float, float]:
    """
    Convert AB magnitude to flux density
    
    Parameters
    ----------
    magnitude : float
        AB magnitude
    wavelength : float
        Effective wavelength in Angstroms
    mag_err : float, optional
        Magnitude error
    
    Returns
    -------
    tuple
        (flux in erg/s/cm²/Å, flux_err)
    """
    # AB magnitude zero point
    # f_ν = 3631 Jy × 10^(-mag/2.5)
    # f_λ = f_ν × c / λ²
    
    c = 2.998e18  # Speed of light in Angstrom/s
    f_nu_zp = 3.631e-20  # erg/s/cm²/Hz (3631 Jy)
    
    f_nu = f_nu_zp * 10**(-magnitude / 2.5)
    f_lambda = f_nu * c / wavelength**2
    
    if mag_err is not None:
        # Error propagation
        f_lambda_err = f_lambda * mag_err * np.log(10) / 2.5
        return f_lambda, f_lambda_err
    
    return f_lambda, 0.0


def build_sed(
    photometry: Dict[str, Dict[str, float]],
    z: float = 0.0
) -> pd.DataFrame:
    """
    Build SED from multi-survey photometry
    
    Parameters
    ----------
    photometry : dict
        Dictionary with survey data:
        {
            'sdss': {'u': 19.5, 'g': 18.2, ...},
            'panstarrs': {'g': 18.3, ...},
            '2mass': {'J': 15.2, ...},
            'gaia': {'G': 17.8, ...}
        }
    z : float, optional
        Redshift (for rest-frame conversion)
    
    Returns
    -------
    pd.DataFrame
        SED table with wavelength, flux, flux_err, filter columns
    """
    sed_data = []
    
    for survey, mags in photometry.items():
        for band, mag_value in mags.items():
            if isinstance(mag_value, dict):
                mag = mag_value.get('mag', None)
                mag_err = mag_value.get('err', None)
            else:
                mag = mag_value
                mag_err = None
            
            if mag is None or not np.isfinite(mag):
                continue
            
            # Construct filter name
            if survey == 'sdss':
                filter_name = f'sdss_{band}'
            elif survey == 'panstarrs':
                filter_name = f'ps_{band}'
            elif survey == '2mass':
                filter_name = f'2mass_{band}'
            elif survey == 'gaia':
                filter_name = f'gaia_{band}'
            else:
                continue
            
            if filter_name not in FILTER_INFO:
                continue
            
            wave = FILTER_INFO[filter_name]['wave']
            flux, flux_err = mag_to_flux(mag, wave, mag_err)
            
            # Convert to rest frame if redshift provided
            if z > 0:
                wave_rest = wave / (1 + z)
                flux_rest = flux * (1 + z)
                flux_err_rest = flux_err * (1 + z)
            else:
                wave_rest = wave
                flux_rest = flux
                flux_err_rest = flux_err
            
            sed_data.append({
                'wavelength': wave_rest,
                'wavelength_obs': wave,
                'flux': flux_rest,
                'flux_err': flux_err_rest,
                'filter': filter_name,
                'magnitude': mag,
                'mag_err': mag_err if mag_err is not None else 0.0
            })
    
    df = pd.DataFrame(sed_data)
    df = df.sort_values('wavelength')
    
    return df


def plot_sed(
    sed_df: pd.DataFrame,
    title: str = "Spectral Energy Distribution",
    interactive: bool = True,
    show_filters: bool = True
) -> Optional[go.Figure]:
    """
    Plot SED
    
    Parameters
    ----------
    sed_df : pd.DataFrame
        SED data from build_sed()
    title : str, optional
        Plot title
    interactive : bool, optional
        If True, return Plotly figure; if False, return Matplotlib figure
    show_filters : bool, optional
        Whether to show filter labels
    
    Returns
    -------
    figure
        SED plot
    """
    if sed_df is None or len(sed_df) == 0:
        return None
    
    if interactive:
        # Plotly version
        fig = go.Figure()
        
        # Plot photometry points
        fig.add_trace(go.Scatter(
            x=sed_df['wavelength'],
            y=sed_df['flux'],
            mode='markers',
            name='Photometry',
            marker=dict(size=10, color='blue'),
            error_y=dict(
                type='data',
                array=sed_df['flux_err'],
                visible=True
            ),
            text=sed_df['filter'],
            hovertemplate='<b>%{text}</b><br>' +
                         'λ: %{x:.0f} Å<br>' +
                         'Flux: %{y:.2e} erg/s/cm²/Å<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Wavelength (Å)',
            yaxis_title='Flux Density (erg/s/cm²/Å)',
            xaxis_type='log',
            yaxis_type='log',
            hovermode='closest',
            showlegend=True,
            width=900,
            height=600
        )
        
        return fig
    
    else:
        # Matplotlib version
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot photometry points
        ax.errorbar(
            sed_df['wavelength'],
            sed_df['flux'],
            yerr=sed_df['flux_err'],
            fmt='o',
            color='blue',
            markersize=8,
            capsize=4,
            label='Photometry'
        )
        
        # Add filter labels if requested
        if show_filters:
            for _, row in sed_df.iterrows():
                ax.text(
                    row['wavelength'],
                    row['flux'] * 1.2,
                    row['filter'].replace('_', ' '),
                    fontsize=8,
                    rotation=45,
                    ha='right'
                )
        
        ax.set_xlabel('Wavelength (Å)', fontsize=14)
        ax.set_ylabel('Flux Density (erg/s/cm²/Å)', fontsize=14)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(fontsize=10)
        ax.set_title(title, fontsize=16)
        
        return fig
