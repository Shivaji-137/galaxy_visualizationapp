"""
Overview page - Object search and basic information
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_fetchers.gaia_fetcher import fetch_gaia_data, resolve_object_to_coords
from data_fetchers.sdss_fetcher import fetch_sdss_data
from data_fetchers.panstarrs_fetcher import fetch_panstarrs_data
from data_fetchers.twomass_fetcher import fetch_2mass_data
from data_fetchers.mast_fetcher import fetch_mast_observations
from data_fetchers.multi_survey_fetcher import fetch_all_surveys
from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("🔍 Search Controls", "Find objects by name or coordinates"),
    unsafe_allow_html=True
)

st.title("📊 Object Overview & Search")

st.markdown("""
Search for astronomical objects by name or coordinates and view cross-matched data from multiple surveys.
""")

with st.expander("ℹ️ Available Surveys", expanded=False):
    st.markdown("""
    **Gaia DR3**: Astrometry (positions, proper motions, parallaxes) and optical photometry (G, BP, RP bands)
    
    **SDSS DR17**: Optical imaging (ugriz) and spectroscopy with redshifts
    
    **MAST**: Mikulski Archive for Space Telescopes
    - **HST**: Hubble Space Telescope imaging and spectra
    - **JWST**: James Webb Space Telescope (latest infrared observations)
    - **GALEX**: UV imaging (NUV and FUV bands)
    
    **Pan-STARRS DR2**: Optical imaging (grizy bands) with better coverage than SDSS
    
    **2MASS**: Near-infrared survey (J, H, K bands)
    """)

# Initialize session state
if 'target_coords' not in st.session_state:
    st.session_state.target_coords = None
if 'target_name' not in st.session_state:
    st.session_state.target_name = None
if 'catalog_data' not in st.session_state:
    st.session_state.catalog_data = {}

# Search interface
st.markdown("## 🔍 Object Search")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Search by Name")
    object_name = st.text_input(
        "Object Name",
        placeholder="e.g., NGC 4151, M31, 3C 273",
        help="Enter object name (Simbad resolvable)"
    )
    
    if st.button("🔍 Resolve Name", width='stretch'):
        with st.spinner("Resolving object name..."):
            coords = resolve_object_to_coords(object_name)
            if coords:
                st.session_state.target_coords = coords
                st.session_state.target_name = object_name
                st.success(f"✓ Resolved: RA={coords[0]:.6f}°, Dec={coords[1]:.6f}°")
            else:
                st.error("Could not resolve object name. Try coordinates instead.")

with col2:
    st.markdown("### Search by Coordinates")
    coord_ra = st.number_input(
        "Right Ascension (deg)",
        min_value=0.0,
        max_value=360.0,
        value=180.0,
        format="%.6f"
    )
    coord_dec = st.number_input(
        "Declination (deg)",
        min_value=-90.0,
        max_value=90.0,
        value=0.0,
        format="%.6f"
    )
    
    if st.button("📍 Use Coordinates", width='stretch'):
        st.session_state.target_coords = (coord_ra, coord_dec)
        st.session_state.target_name = f"RA={coord_ra:.4f}, Dec={coord_dec:.4f}"
        st.success(f"✓ Coordinates set: RA={coord_ra:.6f}°, Dec={coord_dec:.6f}°")

# Search parameters
st.markdown("### Search Parameters")
search_radius = st.slider(
    "Search Radius (arcsec)",
    min_value=1.0,
    max_value=30.0,
    value=5.0,
    step=0.5
)

# Data fetching
if st.session_state.target_coords:
    st.markdown("---")
    st.markdown(f"## 📡 Data for: **{st.session_state.target_name}**")
    
    ra, dec = st.session_state.target_coords
    
    st.markdown(f"**Position:** RA = {ra:.6f}°, Dec = {dec:.6f}°")
    
    # Survey selection
    st.markdown("### Select Surveys to Query")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        query_gaia = st.checkbox("Gaia DR3", value=True)
    with col2:
        query_sdss = st.checkbox("SDSS DR17", value=True)
    with col3:
        query_mast = st.checkbox("MAST", value=True, help="HST, JWST, GALEX")
    with col4:
        query_panstarrs = st.checkbox("Pan-STARRS", value=False)
    with col5:
        query_2mass = st.checkbox("2MASS", value=False)
    
    if st.button("🚀 Fetch Data from Surveys", width='stretch', type="primary"):
        # Build list of surveys
        surveys_to_query = []
        if query_gaia:
            surveys_to_query.append('gaia')
        if query_sdss:
            surveys_to_query.append('sdss')
        if query_mast:
            surveys_to_query.append('mast')
        if query_panstarrs:
            surveys_to_query.append('panstarrs')
        if query_2mass:
            surveys_to_query.append('2mass')
        
        if not surveys_to_query:
            st.warning("Please select at least one survey to query")
        else:
            with st.spinner(f"Fetching data from {len(surveys_to_query)} surveys..."):
                # Use parallel fetching
                try:
                    catalogs = fetch_all_surveys(
                        ra, dec,
                        object_name=st.session_state.target_name,
                        radius=search_radius,
                        surveys=surveys_to_query,
                        parallel=True
                    )
                    
                    # Store in session state
                    st.session_state.catalog_data = catalogs
                    
                    if catalogs:
                        st.success(f"✓ Successfully fetched data from {len(catalogs)} surveys!")
                    else:
                        st.warning("No data found in any of the selected surveys")
                        
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
            


# Display results
if st.session_state.catalog_data:
    st.markdown("---")
    st.markdown("## 📊 Catalog Data")
    
    tabs = st.tabs(list(st.session_state.catalog_data.keys()))
    
    for tab, (survey, data) in zip(tabs, st.session_state.catalog_data.items()):
        with tab:
            st.markdown(f"### {survey.upper()} Data")
            st.markdown(f"**Number of sources:** {len(data)}")
            
            # Display dataframe
            st.dataframe(data, width='stretch', height=300)
            
            # Download button
            csv = data.to_csv(index=False)
            st.download_button(
                label=f"💾 Download {survey.upper()} data as CSV",
                data=csv,
                file_name=f"{survey}_data.csv",
                mime="text/csv"
            )
            
            # Basic statistics and survey-specific info
            if len(data) > 0:
                st.markdown("#### Quick Statistics")
                
                # Select first source
                first_source = data.iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Position (first source):**")
                    if 'ra' in first_source:
                        st.write(f"RA: {first_source['ra']:.6f}°")
                        st.write(f"Dec: {first_source['dec']:.6f}°")
                    elif 's_ra' in first_source:  # MAST
                        st.write(f"RA: {first_source['s_ra']:.6f}°")
                        st.write(f"Dec: {first_source['s_dec']:.6f}°")
                
                with col2:
                    st.markdown("**Available columns:**")
                    st.write(f"Total: {len(data.columns)} columns")
                    with st.expander("Show all columns"):
                        st.write(list(data.columns))
                
                # Special display for MAST data
                if survey == 'mast':
                    st.markdown("#### 🔭 Observations by Mission")
                    if 'obs_collection' in data.columns:
                        mission_counts = data['obs_collection'].value_counts()
                        for mission, count in mission_counts.items():
                            st.write(f"- **{mission}**: {count} observations")
                        
                        # Show instruments
                        if 'instrument_name' in data.columns:
                            st.markdown("**Instruments:**")
                            instruments = data['instrument_name'].value_counts()
                            for inst, count in instruments.items():
                                st.write(f"  - {inst}: {count}")
                
                # Special display for Gaia
                elif survey == 'gaia':
                    st.markdown("#### 🌟 Photometry")
                    if 'phot_g_mean_mag' in first_source:
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("G mag", f"{first_source.get('phot_g_mean_mag', 'N/A'):.2f}")
                        with col_b:
                            st.metric("BP mag", f"{first_source.get('phot_bp_mean_mag', 'N/A'):.2f}")
                        with col_c:
                            st.metric("RP mag", f"{first_source.get('phot_rp_mean_mag', 'N/A'):.2f}")
                
                # Special display for SDSS
                elif survey == 'sdss':
                    st.markdown("#### 📷 Photometry")
                    if 'u' in first_source:
                        cols = st.columns(5)
                        for i, band in enumerate(['u', 'g', 'r', 'i', 'z']):
                            with cols[i]:
                                val = first_source.get(band, None)
                                if val is not None and pd.notna(val):
                                    st.metric(f"{band} mag", f"{val:.2f}")
                    
                    # Check for spectrum
                    if 'specObjID' in first_source or 'z' in first_source:
                        st.info("✓ This object has SDSS spectroscopy available!")
    
    # Summary
    st.markdown("---")
    st.markdown("## 📝 Summary")
    
    summary_data = []
    for survey, data in st.session_state.catalog_data.items():
        summary_data.append({
            'Survey': survey.upper(),
            'Sources Found': len(data),
            'Columns': len(data.columns)
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
    
    # Next steps
    st.info("""
    **Next Steps:**
    - Navigate to **Thumbnails** page to view imaging data
    - Go to **Spectra & Lines** page for spectroscopic analysis
    - Use **BPT & Classification** for object classification
    - Visit **SED Viewer** to build spectral energy distributions
    """)

else:
    st.info("👆 Enter an object name or coordinates above and fetch data to begin exploration.")

# Footer
st.markdown("---")
st.markdown("*Use the sidebar to navigate to other analysis pages*")
