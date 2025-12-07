"""
BPT diagnostic diagrams for galaxy classification
"""
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Tuple, Dict, Optional
from .line_fitting import LineResult


def kauffmann03_line(nii_ha: np.ndarray) -> np.ndarray:
    """
    Kauffmann et al. (2003) star-forming/AGN demarcation line
    
    Parameters
    ----------
    nii_ha : array
        log([NII]/Hα) values
    
    Returns
    -------
    array
        log([OIII]/Hβ) values on the demarcation line
    """
    return 0.61 / (nii_ha - 0.05) + 1.3


def kewley01_line(nii_ha: np.ndarray) -> np.ndarray:
    """
    Kewley et al. (2001) theoretical maximum starburst line
    
    Parameters
    ----------
    nii_ha : array
        log([NII]/Hα) values
    
    Returns
    -------
    array
        log([OIII]/Hβ) values on the demarcation line
    """
    return 0.61 / (nii_ha - 0.47) + 1.19


def classify_object_bpt(
    nii_ha: float,
    oiii_hb: float
) -> str:
    """
    Classify object using BPT diagram
    
    Parameters
    ----------
    nii_ha : float
        log([NII]/Hα)
    oiii_hb : float
        log([OIII]/Hβ)
    
    Returns
    -------
    str
        Classification: 'Star-forming', 'Composite', 'AGN', or 'LINER'
    """
    # Kauffmann line
    kauffmann_val = kauffmann03_line(nii_ha)
    
    # Kewley line
    kewley_val = kewley01_line(nii_ha)
    
    # LINER demarcation (Schawinski et al. 2007)
    liner_line = 1.89 * nii_ha + 0.76
    
    if oiii_hb < kauffmann_val:
        return 'Star-forming'
    elif oiii_hb < kewley_val:
        return 'Composite'
    elif oiii_hb > liner_line:
        return 'AGN (Seyfert)'
    else:
        return 'LINER'


def calculate_line_ratios(
    line_results: Dict[str, LineResult]
) -> Dict[str, float]:
    """
    Calculate BPT line ratios from fitting results
    
    Parameters
    ----------
    line_results : dict
        Dictionary of LineResult objects
    
    Returns
    -------
    dict
        Dictionary with line ratios (log scale)
    """
    ratios = {}
    
    # [NII]/Hα
    if 'NII_6583' in line_results and 'Halpha' in line_results:
        nii = line_results['NII_6583']
        ha = line_results['Halpha']
        if nii.flux > 0 and ha.flux > 0:
            ratios['NII_Ha'] = np.log10(nii.flux / ha.flux)
            # Error propagation
            ratios['NII_Ha_err'] = 0.434 * np.sqrt(
                (nii.flux_err / nii.flux)**2 + (ha.flux_err / ha.flux)**2
            )
    
    # [OIII]/Hβ
    if 'OIII_5007' in line_results and 'Hbeta' in line_results:
        oiii = line_results['OIII_5007']
        hb = line_results['Hbeta']
        if oiii.flux > 0 and hb.flux > 0:
            ratios['OIII_Hb'] = np.log10(oiii.flux / hb.flux)
            ratios['OIII_Hb_err'] = 0.434 * np.sqrt(
                (oiii.flux_err / oiii.flux)**2 + (hb.flux_err / hb.flux)**2
            )
    
    # [SII]/Hα
    if 'SII_6716' in line_results and 'SII_6731' in line_results and 'Halpha' in line_results:
        sii_6716 = line_results['SII_6716']
        sii_6731 = line_results['SII_6731']
        ha = line_results['Halpha']
        sii_total = sii_6716.flux + sii_6731.flux
        if sii_total > 0 and ha.flux > 0:
            ratios['SII_Ha'] = np.log10(sii_total / ha.flux)
    
    # [OI]/Hα
    if 'OI_6300' in line_results and 'Halpha' in line_results:
        oi = line_results['OI_6300']
        ha = line_results['Halpha']
        if oi.flux > 0 and ha.flux > 0:
            ratios['OI_Ha'] = np.log10(oi.flux / ha.flux)
    
    return ratios


def create_bpt_diagram(
    line_results: Optional[Dict[str, LineResult]] = None,
    show_object: bool = True,
    interactive: bool = True
) -> Optional[go.Figure]:
    """
    Create BPT diagram with classification regions
    
    Parameters
    ----------
    line_results : dict, optional
        Line fitting results to plot object position
    show_object : bool, optional
        Whether to show the object on the diagram
    interactive : bool, optional
        If True, return Plotly figure; if False, return Matplotlib figure
    
    Returns
    -------
    figure
        BPT diagram figure
    """
    # Create grid for classification lines
    nii_ha = np.linspace(-2, 0.5, 100)
    kauffmann = kauffmann03_line(nii_ha)
    kewley = kewley01_line(nii_ha)
    
    # LINER line
    liner_x = np.linspace(-0.4, 0.5, 50)
    liner_y = 1.89 * liner_x + 0.76
    
    if interactive:
        # Plotly version
        fig = go.Figure()
        
        # Add classification regions
        fig.add_trace(go.Scatter(
            x=nii_ha, y=kauffmann,
            mode='lines',
            name='Kauffmann+03 (SF)',
            line=dict(color='blue', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=nii_ha, y=kewley,
            mode='lines',
            name='Kewley+01 (max SB)',
            line=dict(color='green', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=liner_x, y=liner_y,
            mode='lines',
            name='Schawinski+07 (LINER)',
            line=dict(color='red', dash='dash')
        ))
        
        # Add object if provided
        if line_results is not None and show_object:
            ratios = calculate_line_ratios(line_results)
            if 'NII_Ha' in ratios and 'OIII_Hb' in ratios:
                classification = classify_object_bpt(ratios['NII_Ha'], ratios['OIII_Hb'])
                
                fig.add_trace(go.Scatter(
                    x=[ratios['NII_Ha']],
                    y=[ratios['OIII_Hb']],
                    mode='markers',
                    name=f'Target ({classification})',
                    marker=dict(size=15, color='red', symbol='star'),
                    error_x=dict(
                        type='data',
                        array=[ratios.get('NII_Ha_err', 0)],
                        visible=True
                    ),
                    error_y=dict(
                        type='data',
                        array=[ratios.get('OIII_Hb_err', 0)],
                        visible=True
                    )
                ))
        
        # Add region labels
        annotations = [
            dict(x=-1.5, y=0.2, text='Star-forming', showarrow=False, font=dict(size=12, color='blue')),
            dict(x=-0.3, y=0.8, text='Composite', showarrow=False, font=dict(size=12, color='green')),
            dict(x=0.2, y=1.3, text='Seyfert', showarrow=False, font=dict(size=12, color='red')),
            dict(x=0.1, y=0.3, text='LINER', showarrow=False, font=dict(size=12, color='orange'))
        ]
        
        fig.update_layout(
            title='BPT Diagram: [NII]/Hα vs [OIII]/Hβ',
            xaxis_title='log([NII] λ6583 / Hα)',
            yaxis_title='log([OIII] λ5007 / Hβ)',
            xaxis=dict(range=[-2, 0.5]),
            yaxis=dict(range=[-1.5, 1.5]),
            annotations=annotations,
            hovermode='closest',
            showlegend=True,
            width=800,
            height=600
        )
        
        return fig
    
    else:
        # Matplotlib version
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot classification lines
        ax.plot(nii_ha, kauffmann, 'b--', label='Kauffmann+03 (SF)', linewidth=2)
        ax.plot(nii_ha, kewley, 'g--', label='Kewley+01 (max SB)', linewidth=2)
        ax.plot(liner_x, liner_y, 'r--', label='Schawinski+07 (LINER)', linewidth=2)
        
        # Add object if provided
        if line_results is not None and show_object:
            ratios = calculate_line_ratios(line_results)
            if 'NII_Ha' in ratios and 'OIII_Hb' in ratios:
                classification = classify_object_bpt(ratios['NII_Ha'], ratios['OIII_Hb'])
                ax.errorbar(
                    ratios['NII_Ha'], ratios['OIII_Hb'],
                    xerr=ratios.get('NII_Ha_err', 0),
                    yerr=ratios.get('OIII_Hb_err', 0),
                    fmt='r*', markersize=15, label=f'Target ({classification})'
                )
        
        # Add region labels
        ax.text(-1.5, 0.2, 'Star-forming', fontsize=12, color='blue', weight='bold')
        ax.text(-0.3, 0.8, 'Composite', fontsize=12, color='green', weight='bold')
        ax.text(0.2, 1.3, 'Seyfert', fontsize=12, color='red', weight='bold')
        ax.text(0.1, 0.3, 'LINER', fontsize=12, color='orange', weight='bold')
        
        ax.set_xlabel('log([NII] λ6583 / Hα)', fontsize=14)
        ax.set_ylabel('log([OIII] λ5007 / Hβ)', fontsize=14)
        ax.set_xlim(-2, 0.5)
        ax.set_ylim(-1.5, 1.5)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_title('BPT Diagram: [NII]/Hα vs [OIII]/Hβ', fontsize=16)
        
        return fig
