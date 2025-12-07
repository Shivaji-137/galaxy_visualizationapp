"""
Utility modules for spectral analysis and plotting
"""
from .line_fitting import fit_emission_line, fit_multiple_lines, LineResult
from .spectral_utils import smooth_spectrum, calculate_snr, measure_continuum
from .bpt_diagrams import create_bpt_diagram, classify_object_bpt
from .sed_builder import build_sed, plot_sed
from .galaxy_properties import estimate_stellar_mass, estimate_sfr

__all__ = [
    'fit_emission_line',
    'fit_multiple_lines',
    'LineResult',
    'smooth_spectrum',
    'calculate_snr',
    'measure_continuum',
    'create_bpt_diagram',
    'classify_object_bpt',
    'build_sed',
    'plot_sed',
    'estimate_stellar_mass',
    'estimate_sfr'
]
