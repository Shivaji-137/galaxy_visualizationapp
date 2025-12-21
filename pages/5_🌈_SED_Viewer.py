"""
SED Viewer page - Spectral Energy Distribution builder
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.sed_builder import build_sed, plot_sed
from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="SED Viewer", page_icon="🌈", layout="wide")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("🌈 SED Tools", "Multi-wavelength analysis"),
    unsafe_allow_html=True
)

st.title("🌈 Spectral Energy Distribution (SED)")

st.markdown("""
Build and visualize multi-wavelength SEDs combining photometry from all available surveys.
The SED traces the galaxy's energy output across the electromagnetic spectrum.
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
st.markdown("### 📊 Available Photometry")

# Show available surveys
available_surveys = list(catalog_data.keys())
st.success(f"✓ Data available from: {', '.join([s.upper() for s in available_surveys])}")

# Compile photometry
st.markdown("### 🔧 Photometry Selection")

photometry = {}

# SDSS
if 'sdss' in catalog_data and len(catalog_data['sdss']) > 0:
    with st.expander("SDSS ugriz", expanded=True):
        sdss_obj = catalog_data['sdss'].iloc[0]
        
        sdss_phot = {}
        for band in ['u', 'g', 'r', 'i', 'z']:
            if band in sdss_obj:
                mag = sdss_obj[band]
                err_col = f'err_{band}'
                err = sdss_obj[err_col] if err_col in sdss_obj else 0.1
                
                use_band = st.checkbox(f"Use {band}-band", value=True, key=f"sdss_{band}")
                if use_band:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{band} mag", f"{mag:.3f}")
                    with col2:
                        st.metric(f"Error", f"{err:.3f}")
                    
                    sdss_phot[band] = {'mag': mag, 'err': err}
        
        if sdss_phot:
            photometry['sdss'] = sdss_phot

# Pan-STARRS
if 'panstarrs' in catalog_data and len(catalog_data['panstarrs']) > 0:
    with st.expander("Pan-STARRS grizy", expanded=True):
        ps_obj = catalog_data['panstarrs'].iloc[0]
        
        ps_phot = {}
        for band in ['g', 'r', 'i', 'z', 'y']:
            mag_col = f'{band}MeanPSFMag'
            err_col = f'{band}MeanPSFMagErr'
            
            if mag_col in ps_obj:
                mag = ps_obj[mag_col]
                err = ps_obj[err_col] if err_col in ps_obj else 0.1
                
                use_band = st.checkbox(f"Use {band}-band", value=True, key=f"ps_{band}")
                if use_band:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{band} mag", f"{mag:.3f}")
                    with col2:
                        st.metric(f"Error", f"{err:.3f}")
                    
                    ps_phot[band] = {'mag': mag, 'err': err}
        
        if ps_phot:
            photometry['panstarrs'] = ps_phot

# 2MASS
if '2mass' in catalog_data and len(catalog_data['2mass']) > 0:
    with st.expander("2MASS JHK", expanded=True):
        tmass_obj = catalog_data['2mass'].iloc[0]
        
        tmass_phot = {}
        for band in ['J', 'H', 'K']:
            if band in tmass_obj:
                mag = tmass_obj[band]
                err_col = f'{band}_err'
                err = tmass_obj[err_col] if err_col in tmass_obj else 0.1
                
                use_band = st.checkbox(f"Use {band}-band", value=True, key=f"2mass_{band}")
                if use_band:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{band} mag", f"{mag:.3f}")
                    with col2:
                        st.metric(f"Error", f"{err:.3f}")
                    
                    tmass_phot[band] = {'mag': mag, 'err': err}
        
        if tmass_phot:
            photometry['2mass'] = tmass_phot

# Gaia
if 'gaia' in catalog_data and len(catalog_data['gaia']) > 0:
    with st.expander("Gaia G/BP/RP", expanded=True):
        gaia_obj = catalog_data['gaia'].iloc[0]
        
        gaia_phot = {}
        for band, col_name in [('G', 'phot_g_mean_mag'), ('BP', 'phot_bp_mean_mag'), ('RP', 'phot_rp_mean_mag')]:
            if col_name in gaia_obj:
                mag = gaia_obj[col_name]
                
                use_band = st.checkbox(f"Use {band}-band", value=True, key=f"gaia_{band}")
                if use_band:
                    st.metric(f"{band} mag", f"{mag:.3f}")
                    gaia_phot[band] = {'mag': mag, 'err': 0.05}
        
        if gaia_phot:
            photometry['gaia'] = gaia_phot

# Build SED
if len(photometry) > 0:
    st.markdown("---")
    st.markdown("### 🌈 Build SED")
    
    # Redshift for rest-frame conversion
    z_sed = st.number_input(
        "Redshift (for rest-frame SED)",
        min_value=0.0,
        max_value=2.0,
        value=0.0,
        step=0.001,
        format="%.4f",
        help="Enter redshift to convert SED to rest frame"
    )
    
    if st.button("⚡ Build SED", width='stretch', type="primary"):
        with st.spinner("Building SED..."):
            try:
                sed_df = build_sed(photometry, z=z_sed)
                
                if sed_df is not None and len(sed_df) > 0:
                    st.session_state.sed_data = sed_df
                    st.success(f"✓ Built SED with {len(sed_df)} photometric points")
                else:
                    st.error("Failed to build SED")
            
            except Exception as e:
                st.error(f"Error building SED: {e}")
    
    # Plot SED
    if 'sed_data' in st.session_state and st.session_state.sed_data is not None:
        st.markdown("---")
        st.markdown("### 📈 SED Plot")
        
        sed_df = st.session_state.sed_data
        
        # Plot options
        col1, col2 = st.columns(2)
        with col1:
            show_filter_labels = st.checkbox("Show filter labels", value=False)
        with col2:
            frame_label = "Rest Frame" if z_sed > 0 else "Observed Frame"
            st.info(f"**Frame:** {frame_label}")
        
        # Create plot
        fig = plot_sed(
            sed_df,
            title=f"SED: {target_name}",
            interactive=True,
            show_filters=show_filter_labels
        )
        
        if fig:
            st.plotly_chart(fig, width='stretch')
        
        # SED table
        st.markdown("### 📋 SED Data Table")
        
        # Format for display
        display_df = sed_df.copy()
        display_df['wavelength'] = display_df['wavelength'].apply(lambda x: f"{x:.1f}")
        display_df['flux'] = display_df['flux'].apply(lambda x: f"{x:.2e}")
        display_df['flux_err'] = display_df['flux_err'].apply(lambda x: f"{x:.2e}")
        
        st.dataframe(display_df, width='stretch')
        
        # Download
        csv = sed_df.to_csv(index=False)
        st.download_button(
            "💾 Download SED Data (CSV)",
            csv,
            f"sed_{target_name.replace(' ', '_')}.csv",
            "text/csv"
        )
        
        # SED analysis
        st.markdown("---")
        st.markdown("### 🔬 SED Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Wavelength Coverage",
                f"{sed_df['wavelength'].min():.0f} - {sed_df['wavelength'].max():.0f} Å"
            )
        
        with col2:
            # UV-to-optical color
            if len(sed_df) > 1:
                flux_ratio = sed_df['flux'].max() / sed_df['flux'].min()
                st.metric("Flux Dynamic Range", f"{flux_ratio:.1f}×")
        
        with col3:
            st.metric("Photometric Points", len(sed_df))
        
        # Color information
        st.markdown("#### Broad-band Colors")
        
        # Calculate some colors if data available
        colors_dict = {}
        
        for _, row in sed_df.iterrows():
            if 'sdss_g' in row['filter']:
                colors_dict['g_mag'] = row['magnitude']
            elif 'sdss_r' in row['filter']:
                colors_dict['r_mag'] = row['magnitude']
            elif 'sdss_i' in row['filter']:
                colors_dict['i_mag'] = row['magnitude']
            elif '2mass_J' in row['filter']:
                colors_dict['J_mag'] = row['magnitude']
            elif '2mass_K' in row['filter']:
                colors_dict['K_mag'] = row['magnitude']
        
        color_metrics = st.columns(4)
        
        with color_metrics[0]:
            if 'g_mag' in colors_dict and 'r_mag' in colors_dict:
                g_r = colors_dict['g_mag'] - colors_dict['r_mag']
                st.metric("g - r", f"{g_r:.3f}")
        
        with color_metrics[1]:
            if 'r_mag' in colors_dict and 'i_mag' in colors_dict:
                r_i = colors_dict['r_mag'] - colors_dict['i_mag']
                st.metric("r - i", f"{r_i:.3f}")
        
        with color_metrics[2]:
            if 'g_mag' in colors_dict and 'J_mag' in colors_dict:
                g_J = colors_dict['g_mag'] - colors_dict['J_mag']
                st.metric("g - J", f"{g_J:.3f}")
        
        with color_metrics[3]:
            if 'J_mag' in colors_dict and 'K_mag' in colors_dict:
                J_K = colors_dict['J_mag'] - colors_dict['K_mag']
                st.metric("J - K", f"{J_K:.3f}")
        
        # Interpretation
        st.markdown("#### SED Interpretation")
        
        with st.expander("Understanding Your SED"):
            st.markdown("""
            **SED Shape Indicators:**
            
            - **Blue colors (g-r < 0.6)**: Young stellar population, active star formation
            - **Red colors (g-r > 0.8)**: Old stellar population, passive evolution
            - **Strong UV excess**: Ongoing star formation or AGN
            - **Strong near-IR**: Old stars, dust emission, or cool stars
            
            **Next Steps for Detailed Analysis:**
            
            1. **K-corrections**: Apply redshift-dependent corrections for accurate rest-frame
               magnitudes
            
            2. **Dust Extinction**: Correct for Galactic and internal dust using E(B-V) estimates
            
            3. **AGN Contribution**: If AGN is present, separate stellar and AGN components
            """)

else:
    st.warning("No photometric data selected. Please select at least one filter from each available survey.")

# Footer
st.markdown("---")
st.markdown("### 📚 Resources")

st.markdown("""
**Stellar Population Models:**
- FSPS (Flexible Stellar Population Synthesis)
- BC03 (Bruzual & Charlot 2003)
- PEGASE
""")

st.markdown("---")
st.markdown("*Congratulations! You've completed the full analysis workflow.*")
