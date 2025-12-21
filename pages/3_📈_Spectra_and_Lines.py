"""
Spectra & Lines page - Spectroscopic analysis and emission line fitting
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_fetchers.sdss_fetcher import fetch_sdss_spectrum_by_coords
from utils.line_fitting import fit_multiple_lines, EMISSION_LINES, LINE_PRIORITIES, LINE_COLORS
from utils.spectral_utils import smooth_spectrum, calculate_snr
from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="Spectra & Lines", page_icon="📈", layout="wide")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("📈 Spectral Tools", "Line fitting and measurements"),
    unsafe_allow_html=True
)

st.title("📈 Spectroscopy & Emission Line Analysis")

st.markdown("""
Analyze spectra from SDSS and DESI. Fit emission and absorption lines to measure
fluxes, equivalent widths, and velocity offsets.
""")

# Check if target is set
if 'target_coords' not in st.session_state or st.session_state.target_coords is None:
    st.warning("⚠️ No target selected. Please go to the Overview page first.")
    st.stop()

ra, dec = st.session_state.target_coords
target_name = st.session_state.target_name

st.markdown(f"## Target: **{target_name}**")

# Initialize session state for spectrum
if 'spectrum_data' not in st.session_state:
    st.session_state.spectrum_data = None
if 'line_fits' not in st.session_state:
    st.session_state.line_fits = None

# Spectrum loading
st.markdown("---")
st.markdown("### 📡 Load Spectrum")

col1, col2 = st.columns([2, 1])

with col1:
    search_radius_spec = st.slider(
        "Search radius (arcsec)",
        min_value=1.0,
        max_value=100.0,
        value=3.0,
        step=0.5
    )

with col2:
    st.markdown("**Or upload spectrum:**")
    uploaded_file = st.file_uploader(
        "Upload FITS spectrum",
        type=['fits', 'fit'],
        help="SDSS or DESI format spectrum"
    )

if st.button("🔍 Fetch SDSS Spectrum", width='stretch'):
    with st.spinner("Searching for SDSS spectrum..."):
        try:
            spectrum = fetch_sdss_spectrum_by_coords(ra, dec, radius=search_radius_spec)
            
            if spectrum:
                st.session_state.spectrum_data = spectrum
                st.success(f"✓ Loaded SDSS spectrum (plate-mjd-fiber: {spectrum['plate']}-{spectrum['mjd']}-{spectrum['fiberid']})")
            else:
                st.warning("No SDSS spectrum found at this location. Try increasing the search radius.")
        
        except Exception as e:
            st.error(f"Error fetching spectrum: {e}")

# Display spectrum
if st.session_state.spectrum_data:
    spectrum = st.session_state.spectrum_data
    wave = spectrum['wavelength']
    flux = spectrum['flux']
    ivar = spectrum['ivar']
    
    st.markdown("---")
    st.markdown("### 📊 Spectrum Viewer")
    
    # Spectrum controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        smooth_spec = st.checkbox("Smooth spectrum", value=False)
        if smooth_spec:
            smooth_window = st.slider("Smoothing window", 3, 21, 11, step=2)
    
    with col2:
        show_error = st.checkbox("Show error bars", value=False)
    
    with col3:
        log_scale = st.checkbox("Log scale (y-axis)", value=False)
    
    # Wavelength range selector
    wave_min, wave_max = st.slider(
        "Wavelength range (Å)",
        float(wave.min()),
        float(wave.max()),
        (float(wave.min()), float(wave.max())),
        step=10.0
    )
    
    # Prepare flux for plotting
    mask = (wave >= wave_min) & (wave <= wave_max)
    wave_plot = wave[mask]
    flux_plot = flux[mask]
    
    if smooth_spec:
        flux_plot = smooth_spectrum(wave_plot, flux_plot, window=smooth_window)
    
    # Create plot
    fig = go.Figure()
    
    # Main spectrum
    fig.add_trace(go.Scatter(
        x=wave_plot,
        y=flux_plot,
        mode='lines',
        name='Flux',
        line=dict(color='blue', width=1)
    ))
    
    # Error bars (if requested)
    if show_error and ivar is not None:
        error = np.sqrt(1.0 / (ivar[mask] + 1e-10))
        fig.add_trace(go.Scatter(
            x=wave_plot,
            y=flux_plot + error,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=wave_plot,
            y=flux_plot - error,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(0,100,200,0.2)',
            name='±1σ',
            hoverinfo='skip'
        ))
    
    # Mark emission lines
    col_z1, col_z2 = st.columns([3, 1])
    
    with col_z1:
        z_estimate = st.number_input(
            "Redshift estimate",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.001,
            format="%.4f",
            help="Enter approximate redshift to mark emission lines"
        )
    
    with col_z2:
        show_labels = st.checkbox("Show line labels", value=True)
    
    if z_estimate > 0:
        # Find lines in visible range
        visible_lines = []
        for line_name, rest_wave in EMISSION_LINES.items():
            obs_wave = rest_wave * (1 + z_estimate)
            if wave_min <= obs_wave <= wave_max:
                priority = LINE_PRIORITIES.get(line_name, 0)
                visible_lines.append((line_name, obs_wave, priority))
        
        # Sort by wavelength
        visible_lines.sort(key=lambda x: x[1])
        
        # Determine which lines to label based on crowding
        num_lines = len(visible_lines)
        
        if num_lines <= 5:
            # Few lines: label all
            min_spacing = 10
            min_priority = 0  # Show all lines
        elif num_lines <= 10:
            # Moderate: label high priority or well-spaced
            min_spacing = 30
            min_priority = 7  # High priority only
        else:
            # Many lines: only high priority
            min_spacing = 50
            min_priority = 8  # Highest priority only
        
        # Smart labeling algorithm
        positions = ['top', 'bottom']
        last_labeled_wave = -1e6
        label_count = 0
        
        for idx, (line_name, obs_wave, priority) in enumerate(visible_lines):
            # Decide if we should show label
            should_label = False
            
            if show_labels:
                # Check spacing from last label
                spacing_ok = (obs_wave - last_labeled_wave) >= min_spacing
                
                # Check priority threshold
                priority_ok = priority >= min_priority
                
                # Label if both spacing and priority are satisfied
                should_label = spacing_ok and priority_ok
            
            # Alternate position between top and bottom
            position = positions[label_count % 2] if should_label else 'top'
            
            # Determine text angle based on crowding
            if num_lines <= 6:
                text_angle = 0
                font_size = 14
            else:
                text_angle = -90
                font_size = 12
            
            # Get line color
            line_color = LINE_COLORS.get(line_name, '#FF0000')
            line_opacity = 0.8 if priority >= 7 else 0.5
            
            fig.add_vline(
                x=obs_wave,
                line_dash="dash",
                line_color=line_color,
                opacity=line_opacity,
                annotation_text=line_name if should_label else "",
                annotation_position=position,
                annotation=dict(
                    textangle=text_angle,
                    font=dict(size=font_size, color=line_color)
                )
            )
            
            if should_label:
                last_labeled_wave = obs_wave
                label_count += 1
    
    fig.update_layout(
        title="Optical Spectrum",
        xaxis_title="Wavelength (Å)",
        yaxis_title="Flux (arbitrary units)",
        yaxis_type='log' if log_scale else 'linear',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Spectrum statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Wavelength Range", f"{wave.min():.0f}-{wave.max():.0f} Å")
    with col2:
        snr = calculate_snr(flux, ivar)
        st.metric("S/N (median)", f"{snr:.1f}")
    with col3:
        st.metric("Data Points", len(wave))
    with col4:
        st.metric("Median Flux", f"{np.median(flux):.2e}")
    
    # Emission line fitting
    st.markdown("---")
    st.markdown("### 🔬 Emission Line Fitting")
    
    st.info("Automatic Gaussian fitting of common emission lines. Adjust redshift above for better results.")
    
    # Line selection
    available_lines = list(EMISSION_LINES.keys())
    selected_lines = st.multiselect(
        "Select lines to fit",
        available_lines,
        default=['Halpha', 'Hbeta', 'OIII_5007', 'NII_6583'],
        help="Choose which emission lines to fit"
    )
    
    if st.button("⚡ Fit Selected Lines", width='stretch', type="primary"):
        with st.spinner("Fitting emission lines..."):
            try:
                line_results = fit_multiple_lines(
                    wave, flux, ivar,
                    z=z_estimate,
                    lines=selected_lines
                )
                
                st.session_state.line_fits = line_results
                
                # Count successful fits
                successful = sum(1 for r in line_results.values() if r.success)
                st.success(f"✓ Fitted {successful}/{len(selected_lines)} lines successfully")
            
            except Exception as e:
                st.error(f"Error fitting lines: {e}")
    
    # Display line fitting results
    if st.session_state.line_fits:
        st.markdown("#### Fitting Results")
        
        results_data = []
        for line_name, result in st.session_state.line_fits.items():
            if result.success:
                results_data.append({
                    'Line': line_name,
                    'Center (Å)': f"{result.center:.2f} ± {result.center_err:.2f}",
                    'Flux': f"{result.flux:.2e} ± {result.flux_err:.2e}",
                    'EW (Å)': f"{result.ew:.2f} ± {result.ew_err:.2f}",
                    'Sigma (Å)': f"{result.sigma:.2f} ± {result.sigma_err:.2f}",
                    'Velocity (km/s)': f"{result.velocity:.1f} ± {result.velocity_err:.1f}",
                    'S/N': f"{result.snr:.1f}",
                    'Success': '✓' if result.success else '✗'
                })
        
        if results_data:
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, width='stretch')
            
            # Export results
            csv = results_df.to_csv(index=False)
            st.download_button(
                "💾 Download Line Measurements (CSV)",
                csv,
                f"line_fits_{target_name.replace(' ', '_')}.csv",
                "text/csv"
            )
            
            # Line ratio calculations
            st.markdown("#### Important Line Ratios")
            
            line_fits = st.session_state.line_fits
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Halpha' in line_fits and 'Hbeta' in line_fits:
                    ha = line_fits['Halpha']
                    hb = line_fits['Hbeta']
                    if ha.success and hb.success and hb.flux > 0:
                        balmer_dec = ha.flux / hb.flux
                        st.metric(
                            "Hα/Hβ (Balmer Decrement)",
                            f"{balmer_dec:.2f}",
                            help="Theoretical = 2.86 (Case B). Higher values indicate dust extinction."
                        )
            
            with col2:
                if 'OIII_5007' in line_fits and 'Hbeta' in line_fits:
                    oiii = line_fits['OIII_5007']
                    hb = line_fits['Hbeta']
                    if oiii.success and hb.success and hb.flux > 0:
                        ratio = np.log10(oiii.flux / hb.flux)
                        st.metric(
                            "log([OIII]/Hβ)",
                            f"{ratio:.2f}",
                            help="Used in BPT diagram"
                        )
            
            with col3:
                if 'NII_6583' in line_fits and 'Halpha' in line_fits:
                    nii = line_fits['NII_6583']
                    ha = line_fits['Halpha']
                    if nii.success and ha.success and ha.flux > 0:
                        ratio = np.log10(nii.flux / ha.flux)
                        st.metric(
                            "log([NII]/Hα)",
                            f"{ratio:.2f}",
                            help="Used in BPT diagram"
                        )
        else:
            st.warning("No successful line fits to display")

else:
    st.info("👆 Load a spectrum to begin spectroscopic analysis")

# Footer
st.markdown("---")
st.markdown("*Next: Go to **BPT & Classification** page to classify your object*")
