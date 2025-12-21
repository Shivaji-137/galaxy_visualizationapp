"""
Photometry Visualization page - Multi-survey photometric data analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.sed_builder import mag_to_flux, FILTER_INFO
from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="Photometry", page_icon="📊", layout="wide")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("📊 Photometry Tools", "Multi-band photometric analysis"),
    unsafe_allow_html=True
)

st.title("📊 Multi-Survey Photometry")

st.markdown("""
Visualize and analyze photometric data from multiple surveys. Compare magnitudes across different 
bands and surveys, explore color-magnitude diagrams, and examine photometric properties.
""")

# Check prerequisites
if 'target_coords' not in st.session_state or st.session_state.target_coords is None:
    st.warning("⚠️ No target selected. Please go to the Overview page first.")
    st.stop()

target_name = st.session_state.target_name
st.markdown(f"## Target: **{target_name}**")

# Check for catalog data
if 'catalog_data' not in st.session_state or len(st.session_state.catalog_data) == 0:
    st.warning("⚠️ No photometric data available. Please go to the **Overview** page and fetch catalog data first.")
    st.stop()

catalog_data = st.session_state.catalog_data

st.markdown("---")

# Compile photometry from all surveys
def extract_photometry():
    """Extract photometry from all available surveys"""
    phot_data = {
        'filter': [],
        'magnitude': [],
        'magnitude_err': [],
        'survey': [],
        'band': [],
        'wavelength': []
    }
    
    # SDSS
    if 'sdss' in catalog_data and len(catalog_data['sdss']) > 0:
        sdss_obj = catalog_data['sdss'].iloc[0]
        for band in ['u', 'g', 'r', 'i', 'z']:
            if band in sdss_obj and pd.notna(sdss_obj[band]):
                mag = sdss_obj[band]
                err_col = f'err_{band}'
                err = sdss_obj[err_col] if err_col in sdss_obj and pd.notna(sdss_obj[err_col]) else 0.1
                
                phot_data['filter'].append(f'SDSS {band}')
                phot_data['magnitude'].append(mag)
                phot_data['magnitude_err'].append(err)
                phot_data['survey'].append('SDSS')
                phot_data['band'].append(band)
                phot_data['wavelength'].append(FILTER_INFO.get(f'sdss_{band}', {}).get('wave', 0))
    
    # Pan-STARRS
    if 'panstarrs' in catalog_data and len(catalog_data['panstarrs']) > 0:
        ps_obj = catalog_data['panstarrs'].iloc[0]
        for band in ['g', 'r', 'i', 'z', 'y']:
            mag_col = f'{band}MeanPSFMag'
            err_col = f'{band}MeanPSFMagErr'
            
            if mag_col in ps_obj and pd.notna(ps_obj[mag_col]):
                mag = ps_obj[mag_col]
                err = ps_obj[err_col] if err_col in ps_obj and pd.notna(ps_obj[err_col]) else 0.1
                
                phot_data['filter'].append(f'PS {band}')
                phot_data['magnitude'].append(mag)
                phot_data['magnitude_err'].append(err)
                phot_data['survey'].append('Pan-STARRS')
                phot_data['band'].append(band)
                phot_data['wavelength'].append(FILTER_INFO.get(f'ps_{band}', {}).get('wave', 0))
    
    # 2MASS
    if '2mass' in catalog_data and len(catalog_data['2mass']) > 0:
        tmass_obj = catalog_data['2mass'].iloc[0]
        for band in ['j', 'h', 'k']:
            mag_col = f'{band}_m'
            err_col = f'{band}_msigcom'
            
            if mag_col in tmass_obj and pd.notna(tmass_obj[mag_col]):
                mag = tmass_obj[mag_col]
                err = tmass_obj[err_col] if err_col in tmass_obj and pd.notna(tmass_obj[err_col]) else 0.1
                
                phot_data['filter'].append(f'2MASS {band.upper()}')
                phot_data['magnitude'].append(mag)
                phot_data['magnitude_err'].append(err)
                phot_data['survey'].append('2MASS')
                phot_data['band'].append(band.upper())
                phot_data['wavelength'].append(FILTER_INFO.get(f'2mass_{band.upper()}', {}).get('wave', 0))
    
    # Gaia
    if 'gaia' in catalog_data and len(catalog_data['gaia']) > 0:
        gaia_obj = catalog_data['gaia'].iloc[0]
        for band, col in [('G', 'phot_g_mean_mag'), ('BP', 'phot_bp_mean_mag'), ('RP', 'phot_rp_mean_mag')]:
            if col in gaia_obj and pd.notna(gaia_obj[col]):
                mag = gaia_obj[col]
                # Gaia doesn't always have errors in the simple query
                err = 0.05  # Typical Gaia precision
                
                phot_data['filter'].append(f'Gaia {band}')
                phot_data['magnitude'].append(mag)
                phot_data['magnitude_err'].append(err)
                phot_data['survey'].append('Gaia')
                phot_data['band'].append(band)
                phot_data['wavelength'].append(FILTER_INFO.get(f'gaia_{band}', {}).get('wave', 0))
    
    return pd.DataFrame(phot_data)

phot_df = extract_photometry()

if len(phot_df) == 0:
    st.warning("No photometric data found in the available catalogs.")
    st.stop()

st.success(f"✓ Found {len(phot_df)} photometric measurements across {phot_df['survey'].nunique()} surveys")

# Display photometry table
st.markdown("## 📋 Photometry Table")

col1, col2 = st.columns([2, 1])

with col1:
    st.dataframe(
        phot_df[['filter', 'magnitude', 'magnitude_err', 'wavelength']].style.format({
            'magnitude': '{:.3f}',
            'magnitude_err': '{:.3f}',
            'wavelength': '{:.0f}'
        }),
        width='stretch',
        height=300
    )

with col2:
    st.markdown("### 📊 Survey Summary")
    survey_counts = phot_df['survey'].value_counts()
    for survey, count in survey_counts.items():
        st.metric(survey, f"{count} bands")
    
    # Download button
    csv = phot_df.to_csv(index=False)
    st.download_button(
        label="💾 Download Photometry CSV",
        data=csv,
        file_name=f"photometry_{target_name.replace(' ', '_')}.csv",
        mime="text/csv"
    )

st.markdown("---")

# Visualization section
st.markdown("## 📈 Photometry Visualizations")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Magnitude vs Wavelength", "🌈 Filter Comparison", "🎨 Color-Color Diagrams", "📉 Flux Plot"])

with tab1:
    st.markdown("### Magnitude vs Wavelength")
    st.markdown("Visualize how the object's magnitude varies across different wavelengths and surveys.")
    
    # Create magnitude vs wavelength plot
    fig = go.Figure()
    
    for survey in phot_df['survey'].unique():
        survey_data = phot_df[phot_df['survey'] == survey]
        
        fig.add_trace(go.Scatter(
            x=survey_data['wavelength'],
            y=survey_data['magnitude'],
            error_y=dict(
                type='data',
                array=survey_data['magnitude_err'],
                visible=True
            ),
            mode='markers+lines',
            name=survey,
            marker=dict(size=10),
            text=survey_data['filter'],
            hovertemplate='%{text}<br>λ=%{x:.0f} Å<br>mag=%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis_title="Wavelength (Å)",
        yaxis_title="Magnitude (AB)",
        yaxis_autorange='reversed',
        height=500,
        hovermode='closest',
        template='plotly_dark',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    st.plotly_chart(fig, width='stretch')
    
    st.info("💡 Lower magnitude = brighter object. The y-axis is inverted to show brighter objects at the top.")

with tab2:
    st.markdown("### Filter Comparison")
    st.markdown("Compare magnitudes across different filters and surveys.")
    
    # Bar chart of magnitudes
    fig = px.bar(
        phot_df,
        x='filter',
        y='magnitude',
        color='survey',
        error_y='magnitude_err',
        title='Magnitude by Filter',
        labels={'magnitude': 'Magnitude (AB)', 'filter': 'Filter'},
        height=500,
        template='plotly_dark'
    )
    
    fig.update_layout(yaxis_autorange='reversed')
    st.plotly_chart(fig, width='stretch')
    
    # Statistical summary
    st.markdown("### 📊 Statistical Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Brightest", f"{phot_df['magnitude'].min():.2f} mag")
    with col2:
        st.metric("Faintest", f"{phot_df['magnitude'].max():.2f} mag")
    with col3:
        st.metric("Magnitude Range", f"{phot_df['magnitude'].max() - phot_df['magnitude'].min():.2f} mag")

with tab3:
    st.markdown("### Color-Color Diagrams")
    st.markdown("Explore color-color diagrams to understand the object's spectral properties.")
    
    # Calculate colors
    colors_available = {}
    
    # Helper function to get magnitude for a specific filter
    def get_mag(survey, band):
        mask = (phot_df['survey'] == survey) & (phot_df['band'] == band)
        if mask.any():
            return phot_df[mask]['magnitude'].values[0]
        return None
    
    # SDSS colors
    sdss_u = get_mag('SDSS', 'u')
    sdss_g = get_mag('SDSS', 'g')
    sdss_r = get_mag('SDSS', 'r')
    sdss_i = get_mag('SDSS', 'i')
    sdss_z = get_mag('SDSS', 'z')
    
    if sdss_u and sdss_g:
        colors_available['u - g'] = sdss_u - sdss_g
    if sdss_g and sdss_r:
        colors_available['g - r'] = sdss_g - sdss_r
    if sdss_r and sdss_i:
        colors_available['r - i'] = sdss_r - sdss_i
    if sdss_i and sdss_z:
        colors_available['i - z'] = sdss_i - sdss_z
    
    # 2MASS colors
    j_mag = get_mag('2MASS', 'J')
    h_mag = get_mag('2MASS', 'H')
    k_mag = get_mag('2MASS', 'K')
    
    if j_mag and h_mag:
        colors_available['J - H'] = j_mag - h_mag
    if h_mag and k_mag:
        colors_available['H - K'] = h_mag - k_mag
    if j_mag and k_mag:
        colors_available['J - K'] = j_mag - k_mag
    
    # Gaia colors
    bp_mag = get_mag('Gaia', 'BP')
    rp_mag = get_mag('Gaia', 'RP')
    g_mag = get_mag('Gaia', 'G')
    
    if bp_mag and rp_mag:
        colors_available['BP - RP'] = bp_mag - rp_mag
    if bp_mag and g_mag:
        colors_available['BP - G'] = bp_mag - g_mag
    if g_mag and rp_mag:
        colors_available['G - RP'] = g_mag - rp_mag
    
    if colors_available:
        st.markdown("#### Available Colors")
        
        cols = st.columns(min(4, len(colors_available)))
        for idx, (color_name, color_val) in enumerate(colors_available.items()):
            with cols[idx % 4]:
                st.metric(color_name, f"{color_val:.3f}")
        
        # Color-magnitude diagram
        if len(colors_available) >= 2:
            st.markdown("---")
            st.markdown("#### Color-Magnitude Diagram")
            
            color_options = list(colors_available.keys())
            col1, col2 = st.columns(2)
            
            with col1:
                x_color = st.selectbox("X-axis color", color_options, index=0)
            with col2:
                y_mag_options = phot_df['filter'].tolist()
                y_mag = st.selectbox("Y-axis magnitude", y_mag_options, index=0)
            
            # Create CMD
            fig = go.Figure()
            
            y_val = phot_df[phot_df['filter'] == y_mag]['magnitude'].values[0]
            
            fig.add_trace(go.Scatter(
                x=[colors_available[x_color]],
                y=[y_val],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name=target_name,
                text=[target_name],
                hovertemplate='%{text}<br>Color=%{x:.3f}<br>Mag=%{y:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title=x_color,
                yaxis_title=y_mag,
                yaxis_autorange='reversed',
                height=500,
                template='plotly_dark',
                title=f"Color-Magnitude Diagram: {x_color} vs {y_mag}"
            )
            
            st.plotly_chart(fig, width='stretch')
            
            st.info("💡 Color-magnitude diagrams help classify stellar populations and identify unusual objects.")
    else:
        st.warning("Not enough photometric data available to compute colors. Need at least 2 bands from the same survey.")

with tab4:
    st.markdown("### Flux vs Wavelength")
    st.markdown("View the spectral energy distribution in flux units.")
    
    # Convert magnitudes to flux
    flux_data = []
    for _, row in phot_df.iterrows():
        flux, flux_err = mag_to_flux(row['magnitude'], row['wavelength'], row['magnitude_err'])
        flux_data.append({
            'filter': row['filter'],
            'wavelength': row['wavelength'],
            'flux': flux,
            'flux_err': flux_err,
            'survey': row['survey']
        })
    
    flux_df = pd.DataFrame(flux_data)
    
    # Plot flux vs wavelength
    fig = go.Figure()
    
    for survey in flux_df['survey'].unique():
        survey_data = flux_df[flux_df['survey'] == survey]
        
        fig.add_trace(go.Scatter(
            x=survey_data['wavelength'],
            y=survey_data['flux'],
            error_y=dict(
                type='data',
                array=survey_data['flux_err'],
                visible=True
            ),
            mode='markers+lines',
            name=survey,
            marker=dict(size=10),
            text=survey_data['filter'],
            hovertemplate='%{text}<br>λ=%{x:.0f} Å<br>Flux=%{y:.2e}<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis_title="Wavelength (Å)",
        yaxis_title="Flux (erg/s/cm²/Å)",
        yaxis_type="log",
        height=500,
        hovermode='closest',
        template='plotly_dark',
        title="Spectral Energy Distribution (Flux)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    st.plotly_chart(fig, width='stretch')
    
    st.info("💡 This is a simple SED based on photometry. For more detailed SED analysis, visit the **SED Viewer** page.")

# Additional analysis section
st.markdown("---")
st.markdown("## 🔍 Photometric Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Survey Coverage")
    
    # Show wavelength coverage by survey
    coverage_data = []
    for survey in phot_df['survey'].unique():
        survey_data = phot_df[phot_df['survey'] == survey]
        coverage_data.append({
            'Survey': survey,
            'Min λ (Å)': survey_data['wavelength'].min(),
            'Max λ (Å)': survey_data['wavelength'].max(),
            'Coverage (Å)': survey_data['wavelength'].max() - survey_data['wavelength'].min(),
            'N bands': len(survey_data)
        })
    
    coverage_df = pd.DataFrame(coverage_data)
    st.dataframe(coverage_df, width='stretch')

with col2:
    st.markdown("### 🎯 Data Quality")
    
    # Show average uncertainties
    quality_data = []
    for survey in phot_df['survey'].unique():
        survey_data = phot_df[phot_df['survey'] == survey]
        quality_data.append({
            'Survey': survey,
            'Mean Error (mag)': survey_data['magnitude_err'].mean(),
            'Max Error (mag)': survey_data['magnitude_err'].max()
        })
    
    quality_df = pd.DataFrame(quality_data)
    st.dataframe(quality_df.style.format({
        'Mean Error (mag)': '{:.3f}',
        'Max Error (mag)': '{:.3f}'
    }), width='stretch')

# Next steps
st.markdown("---")
st.info("""
**Next Steps:**
- Navigate to **SED Viewer** for detailed spectral energy distribution modeling
- Check **BPT & Classification** for emission line diagnostics
- View **Thumbnails** to see imaging data
""")

# Footer
st.markdown("---")
st.markdown("*Multi-survey photometric data compiled from Gaia, SDSS, Pan-STARRS, and 2MASS*")
