"""
Thumbnails page - Multi-band imaging viewer
"""
import streamlit as st
import sys
from pathlib import Path
import requests
from io import BytesIO
import base64
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import gc

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.style_utils import get_common_css, get_sidebar_header
from utils.memory_utils import (
    limit_image_size, 
    clean_session_state, 
    get_memory_warning,
    check_image_size_warning,
    clear_matplotlib_memory
)

st.set_page_config(page_title="Thumbnails", page_icon="🖼️", layout="wide")

# Clean session state periodically to prevent memory buildup
if 'page_loads' not in st.session_state:
    st.session_state.page_loads = 0
st.session_state.page_loads += 1

# Clean every 5 page loads
if st.session_state.page_loads % 5 == 0:
    clean_session_state(keep_recent=10)
    clear_matplotlib_memory()


# Helper function to display image with Plotly interactive controls
def display_image_interactive(image_url, caption, unique_key, target_name="image", width=800, height=600):
    """
    Display an image with Plotly interactive controls (zoom, pan, download)
    
    Parameters
    ----------
    image_url : str or PIL.Image
        URL to image or PIL Image object
    caption : str
        Caption for the image
    unique_key : str
        Unique key for the widgets
    target_name : str
        Name for downloaded file
    width : int
        Figure width in pixels
    height : int
        Figure height in pixels
    """
    try:
        # Load image
        if isinstance(image_url, str):
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
        elif isinstance(image_url, Image.Image):
            img = image_url
        else:
            st.error("Invalid image format")
            return
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Store original dimensions for download
        original_width = img.width
        original_height = img.height
        
        # For display, optionally limit size (but not for download)
        display_img = img
        if img.width > max_dimension or img.height > max_dimension:
            display_img = img.copy()
            display_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Convert display image to numpy array
        img_array = np.array(display_img)
        
        # Create Plotly figure with image
        fig = go.Figure()
        
        # Add image as a trace
        fig.add_trace(
            go.Image(z=img_array)
        )
        
        # Update layout for better interactivity
        fig.update_layout(
            title=dict(
                text=caption,
                x=0.5,
                xanchor='center',
                font=dict(size=14)
            ),
            plot_bgcolor='black',
            paper_bgcolor='black',
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[0, img_array.shape[1]],
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                scaleanchor="x",
                range=[img_array.shape[0], 0],
            ),
            width=width,
            height=height,
            margin=dict(l=0, r=0, t=30, b=0),
            hovermode='closest',
            # Enable all interactive features
            dragmode='pan',  # Default to pan mode
        )
        
        # Configure modebar buttons
        config = {
            'modeBarButtonsToAdd': [
                'drawline',
                'drawopenpath',
                'eraseshape',
            ],
            'modeBarButtonsToRemove': [],
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f"{target_name.replace(' ', '_')}_{unique_key}",
                'height': original_height,  # Use original full resolution
                'width': original_width,     # Use original full resolution
                'scale': 1  # Scale 1 to preserve original pixels
            }
        }
        
        # Display the interactive figure
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        # Add info about interactive controls
        with st.expander("ℹ️ Interactive Controls", expanded=False):
            st.markdown("""
            **Available controls in the image toolbar:**
            - 🏠 **Home**: Reset view to original
            - 🔍 **Zoom**: Click and drag to zoom into region
            - ↔️ **Pan**: Click and drag to move around
            - 📷 **Download**: Save image as PNG at **full original resolution** (camera icon)
            - ⚡ **Zoom In/Out**: Use +/- buttons
            - 🖱️ **Mouse wheel**: Scroll to zoom in/out
            
            **Note:** Downloaded images will be at the original full resolution from the archive,
            not the reduced size shown in the viewer.
            
            **Tip:** Double-click to reset zoom!
            """)
        
    except Exception as e:
        st.error(f"Error displaying image: {e}")
        # Fallback to regular image display
        st.image(image_url, caption=caption, use_container_width=True)


def display_image_with_download(image_url, caption, filename):
    """
    Display an image with a download button below it
    
    Parameters
    ----------
    image_url : str
        URL to the image
    caption : str
        Caption for the image
    filename : str
        Filename for download
    """
    st.image(image_url, caption=caption, use_container_width=True)
    
    try:
        response = requests.get(image_url, timeout=10)
        img_data = response.content
        
        # Determine file extension
        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = 'jpg'
            mime = 'image/jpeg'
        elif 'png' in content_type:
            ext = 'png'
            mime = 'image/png'
        elif 'gif' in content_type:
            ext = 'gif'
            mime = 'image/gif'
        else:
            ext = 'jpg'
            mime = 'image/jpeg'
        
        st.download_button(
            label="💾 Download",
            data=img_data,
            file_name=f"{filename}.{ext}",
            mime=mime,
            use_container_width=True
        )
    except Exception as e:
        st.caption(f"⚠️ Download unavailable")


# Legacy function for backward compatibility (kept for buttons)
def display_image_with_controls(image_url, caption, unique_key, target_name="image"):
    """
    Display an image with download button only (non-interactive mode)
    Use display_image_interactive for interactive experience with zoom
    """
    # Display image
    st.image(image_url, caption=caption, use_container_width=True)
    
    # Download button
    try:
        # Fetch image data for download
        if isinstance(image_url, str):
            response = requests.get(image_url, timeout=10)
            img_data = response.content
            
            # Determine file extension
            content_type = response.headers.get('Content-Type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
                mime = 'image/jpeg'
            elif 'png' in content_type:
                ext = 'png'
                mime = 'image/png'
            else:
                ext = 'jpg'
                mime = 'image/jpeg'
            
            st.download_button(
                label="💾 Download",
                data=img_data,
                file_name=f"{target_name.replace(' ', '_')}_{unique_key}.{ext}",
                mime=mime,
                use_container_width=True,
                key=f"download_{unique_key}"
            )
        elif isinstance(image_url, Image.Image):
            # PIL Image object
            buf = BytesIO()
            image_url.save(buf, format='PNG')
            img_data = buf.getvalue()
            
            st.download_button(
                label="💾 Download",
                data=img_data,
                file_name=f"{target_name.replace(' ', '_')}_{unique_key}.png",
                mime='image/png',
                key=f"download_{unique_key}"
            )
    except Exception as e:
        st.caption("⚠️ Download temporarily unavailable")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("🖼️ Image Controls", "Configure image size and filters"),
    unsafe_allow_html=True
)

st.title("🖼️ Multi-Survey Imaging Gallery")

st.markdown("""
View multi-band cutout images from various surveys in both **color composite** and **grayscale** formats.
Images help identify morphology, nearby companions, and overall structure.
""")

# Check if target is set
if 'target_coords' not in st.session_state or st.session_state.target_coords is None:
    st.warning("⚠️ No target selected. Please go to the Overview page and search for an object first.")
    st.stop()

ra, dec = st.session_state.target_coords
target_name = st.session_state.target_name

st.markdown(f"## Target: **{target_name}**")
st.markdown(f"**Position:** RA = {ra:.6f}°, Dec = {dec:.6f}°")

st.markdown("---")

# Sidebar: Image parameters
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Image Settings")

# Interactive mode toggle
use_interactive = st.sidebar.checkbox(
    "🎨 Interactive Mode (Plotly)",
    value=False,
    help="Enable interactive zoom, pan, and download with Plotly viewer (uses more memory)"
)

if use_interactive:
    st.sidebar.warning("⚠️ Interactive mode uses more memory")
else:
    st.sidebar.success("✓ Simple mode (recommended for multiple images)")

image_size = st.sidebar.slider(
    "Image Size (pixels)",
    min_value=150,
    max_value=1200,
    value=300,
    step=50,
    help="Larger sizes may take longer to load"
)

# Show warning for large images only in interactive mode
if use_interactive:
    check_image_size_warning(image_size)

arcsec_per_pixel = st.sidebar.number_input(
    "Arcsec/pixel",
    min_value=0.1,
    max_value=5.0,
    value=0.25,
    step=0.05,
    help="Typical: 0.25 arcsec/pixel"
)

fov_arcsec = image_size * arcsec_per_pixel
st.sidebar.info(f"📐 Field of View:\n{fov_arcsec:.1f}″ × {fov_arcsec:.1f}″")

# Image format options
st.sidebar.markdown("### 🎨 Display Options")
show_bw = st.sidebar.checkbox("Show grayscale images", value=True, help="Display black & white single-band images")
show_color = st.sidebar.checkbox("Show color composites", value=True, help="Display RGB color images")

# Image Enhancement Controls
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Image Enhancement")

enhance_source = st.sidebar.selectbox(
    "Image Source",
    ['SDSS', 'Legacy Survey', 'DSS'],
    index=0,
    help="Select survey for enhancement"
)

# Survey info
if enhance_source == 'SDSS':
    st.sidebar.caption("⚡ Fast & reliable")
elif enhance_source == 'Legacy Survey':
    st.sidebar.caption("🔬 Deepest images")
else:
    st.sidebar.caption("📜 Historical (slower)")

st.sidebar.markdown("#### Basic Filters")

apply_gaussian = st.sidebar.checkbox(
    "Gaussian Smoothing", 
    value=True, 
    help="Reduces noise",
    key="enh_gaussian"
)

if apply_gaussian:
    sigma = st.sidebar.slider(
        "Smoothing σ", 
        0.5, 5.0, 2.0, 0.5,
        help="Higher = more smoothing",
        key="enh_sigma"
    )
else:
    sigma = 2.0

apply_meijering = st.sidebar.checkbox(
    "Meijering Filter", 
    value=True, 
    help="Linear structures",
    key="enh_meijering"
)

apply_sato = st.sidebar.checkbox(
    "Sato Filter", 
    value=True, 
    help="Tubular structures",
    key="enh_sato"
)

st.sidebar.markdown("#### Advanced Analysis")
run_advanced = st.sidebar.checkbox(
    "Enable Advanced Analysis",
    value=False,
    help="Corners, features, edges, segmentation",
    key="enh_advanced"
)

# Survey selection
st.markdown("### 🔭 Available Surveys")

survey_tabs = st.tabs(["SDSS", "Legacy Survey", "DSS", "ESO Archive", "HST (Hubble)", "JWST", "🔬 Image Enhancement"])

# SDSS
with survey_tabs[0]:
    st.markdown("#### Sloan Digital Sky Survey (SDSS)")
    st.markdown("*Optical imaging in ugriz bands*")

    
    # SDSS image URLs
    scale = arcsec_per_pixel
    width = image_size
    height = image_size
    
    # Color composite
    sdss_color_url = (
        f"http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?"
        f"ra={ra}&dec={dec}&scale={scale}&width={width}&height={height}"
    )
    
    # Individual bands (grayscale)
    sdss_bands = ['u', 'g', 'r', 'i', 'z']
    sdss_band_urls = {}
    for band in sdss_bands:
        sdss_band_urls[band] = (
            f"http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?"
            f"ra={ra}&dec={dec}&scale={scale}&width={width}&height={height}&opt=G&query=&Grid=on"
        )
    
    if st.button("🖼️ Load SDSS Images", key="fetch_sdss", width='stretch'):
        try:
            if show_color:
                st.markdown("**🎨 SDSS Color Composite (gri)**")
                if use_interactive:
                    display_image_interactive(
                        sdss_color_url, 
                        "SDSS gri color composite", 
                        "sdss_color",
                        target_name=target_name,
                        width=800,
                        height=600
                    )
                else:
                    display_image_with_controls(
                        sdss_color_url, 
                        "SDSS gri color composite", 
                        "sdss_color",
                        target_name=target_name
                    )
            
            if show_bw:
                st.markdown("**⬛ SDSS Individual Bands (Grayscale)**")
                cols = st.columns(5)
                for i, band in enumerate(sdss_bands):
                    with cols[i]:
                        # Use simple image display for grayscale bands
                        st.image(
                            sdss_color_url, 
                            caption=f"{band}-band",
                            use_container_width=True
                        )
        except Exception as e:
            st.error(f"Error loading SDSS images: {e}")
    
    with st.expander("🔗 SDSS Image URLs"):
        st.code(sdss_color_url, language="text")

# Legacy Survey
with survey_tabs[1]:
    st.markdown("#### Legacy Survey (DECaLS/BASS/MzLS)")
    st.markdown("*Deep optical imaging from ground-based surveys*")
    
    legacy_layer = st.selectbox(
        "Select data release",
        ['ls-dr10', 'ls-dr9'],
        help="Legacy Survey data release"
    )
    
    # Legacy Survey URLs
    pixscale = arcsec_per_pixel
    
    # Color composite
    legacy_color_url = (
        f"https://www.legacysurvey.org/viewer/jpeg-cutout?"
        f"ra={ra}&dec={dec}&size={int(fov_arcsec)}&layer={legacy_layer}&pixscale={pixscale}"
    )
    
    # Individual bands
    legacy_bands = {'g': 'g', 'r': 'r', 'z': 'z'}
    legacy_band_urls = {}
    for band_name, band_code in legacy_bands.items():
        legacy_band_urls[band_name] = (
            f"https://www.legacysurvey.org/viewer/jpeg-cutout?"
            f"ra={ra}&dec={dec}&size={int(fov_arcsec)}&layer={legacy_layer}-{band_code}&pixscale={pixscale}"
        )
    
    if st.button("🖼️ Load Legacy Survey Images", key="fetch_legacy", width='stretch'):
        try:
            if show_color:
                st.markdown("**🎨 Legacy Survey Color Composite (grz)**")
                if use_interactive:
                    display_image_interactive(
                        legacy_color_url, 
                        f"Legacy Survey {legacy_layer}", 
                        "legacy_color",
                        target_name=target_name,
                        width=800,
                        height=600
                    )
                else:
                    display_image_with_controls(
                        legacy_color_url, 
                        f"Legacy Survey {legacy_layer}", 
                        "legacy_color",
                        target_name=target_name
                    )
            
            if show_bw:
                st.markdown("**⬛ Legacy Survey Individual Bands (Grayscale)**")
                cols = st.columns(3)
                for i, (band_name, url) in enumerate(legacy_band_urls.items()):
                    with cols[i]:
                        # Use simple image display for grayscale bands
                        st.image(
                            url, 
                            caption=f"{band_name}-band",
                            use_container_width=True
                        )
        except Exception as e:
            st.error(f"Error loading Legacy Survey images: {e}")
    
    with st.expander("🔗 Legacy Survey URLs"):
        st.code(legacy_color_url, language="text")

# DSS (Digitized Sky Survey)
with survey_tabs[2]:
    st.markdown("#### Digitized Sky Survey (DSS)")
    st.markdown("*Historical photographic plates digitized*")
    
    dss_survey = st.selectbox(
        "Select DSS survey",
        ['poss2ukstu_red', 'poss2ukstu_blue', 'poss1_red', 'poss1_blue'],
        format_func=lambda x: {
            'poss2ukstu_red': 'DSS2 Red (deeper, modern)',
            'poss2ukstu_blue': 'DSS2 Blue (deeper, modern)',
            'poss1_red': 'DSS1 Red (historical)',
            'poss1_blue': 'DSS1 Blue (historical)'
        }[x],
        help="Different photographic surveys and plates"
    )
    
    # DSS URLs via STScI
    dss_size = fov_arcsec / 60.0  # Convert to arcminutes
    
    dss_url = (
        f"https://archive.stsci.edu/cgi-bin/dss_search?"
        f"v={dss_survey}&r={ra}&d={dec}&e=J2000&h={dss_size}&w={dss_size}&f=gif&c=none&fov=NONE&v3="
    )
    
    if st.button("🖼️ Load DSS Image", key="fetch_dss", width='stretch'):
        try:
            st.markdown(f"**⬛ DSS Grayscale Image**")
            if use_interactive:
                display_image_interactive(
                    dss_url, 
                    f"DSS - {dss_survey}", 
                    "dss_image",
                    target_name=target_name,
                    width=800,
                    height=600
                )
            else:
                display_image_with_controls(
                    dss_url, 
                    f"DSS - {dss_survey}", 
                    "dss_image",
                    target_name=target_name
                )
            st.info("💡 DSS images are grayscale (black & white) from photographic plates")
        except Exception as e:
            st.error(f"Error loading DSS image: {e}")
    
    with st.expander("🔗 DSS Image URL"):
        st.code(dss_url, language="text")
    
    with st.expander("ℹ️ About DSS"):
        st.markdown("""
        The Digitized Sky Survey consists of digitized photographic plates:
        - **DSS1**: Original survey from 1950s-1960s plates
        - **DSS2**: Deeper, more recent plates from 1980s-1990s
        - **Red plates**: ~650nm (similar to r-band)
        - **Blue plates**: ~450nm (similar to g-band)
        
        These historic images are valuable for:
        - Comparing to modern data
        - Finding transient events
        - Study of proper motions over decades
        """)

# ESO Archive
with survey_tabs[3]:
    st.markdown("#### 🇪🇺 ESO Archive (VLT & VISTA Instruments)")
    st.markdown("*Ground-based imaging from ESO's telescopes in Chile*")
    
    st.info("""
    🔭 **European Southern Observatory** operates the VLT, VISTA, and VST telescopes.
    ESO provides high-quality optical and infrared imaging data.
    """)
    
    # ESO search parameters
    eso_radius = st.slider(
        "Search radius (arcsec)",
        min_value=10.0,
        max_value=120.0,
        value=30.0,
        step=10.0,
        help="Search radius for ESO observations",
        key="eso_radius"
    )
    
    eso_instruments = st.multiselect(
        "Instruments to query",
        ['FORS2', 'HAWKI', 'VIMOS', 'OMEGACAM', 'VIRCAM', 'MUSE', 'ERIS', 'SPHERE', 'GRAVITY'],
        default=['FORS2', 'HAWKI', 'MUSE'],
        help="Select ESO instruments (FORS2=optical, HAWKI=near-IR, MUSE=IFS, GRAVITY=interferometry)",
        key="eso_instruments"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Query by Position", key="eso_query_pos", width='stretch'):
            # Clear previous results
            st.session_state.pop('eso_pos_results', None)
            st.session_state.pop('eso_name_results', None)
            st.session_state['eso_query_done'] = False
            st.session_state['eso_name_query_done'] = False
            
            with st.spinner("Querying ESO archive..."):
                try:
                    from data_fetchers.eso_fetcher import query_eso_images, get_eso_instrument_info
                    
                    st.info(f"Searching at RA={ra:.6f}°, Dec={dec:.6f}° with radius={eso_radius}\"")
                    
                    results = query_eso_images(
                        ra, dec, 
                        radius_arcsec=eso_radius,
                        instruments=[inst.lower() for inst in eso_instruments],
                        max_results=100
                    )
                    
                    # Store results in session state
                    st.session_state['eso_pos_results'] = results
                    st.session_state['eso_query_done'] = True
                    st.session_state['eso_search_coords'] = (ra, dec, eso_radius)
                        
                except ImportError:
                    st.error("⚠️ Please install astroquery: `pip install astroquery`")
                except Exception as e:
                    st.error(f"Error querying ESO archive: {e}")
                    st.caption("💡 ESO archive may be temporarily unavailable")
                    import traceback
                    st.caption(f"Debug: {traceback.format_exc()}")
    
    # Display results from session state (outside button callback)
    if 'eso_pos_results' in st.session_state and st.session_state.get('eso_query_done'):
        results = st.session_state['eso_pos_results']
        search_coords = st.session_state.get('eso_search_coords', (ra, dec, eso_radius))
        
        st.caption(f"📍 Search: RA={search_coords[0]:.6f}°, Dec={search_coords[1]:.6f}°, Radius={search_coords[2]}\"")
        
        if results:
            st.success(f"✅ Found data from {len(results)} instrument(s)")
            
            for instrument, table in results.items():
                with st.expander(f"📊 {instrument} ({len(table)} observations)", expanded=True):
                    st.markdown(f"**{len(table)} observations found**")
                    
                    # Display key columns
                    display_cols = []
                    for col in ['object', 'date_obs', 'filter_path', 'exptime', 'prog_id']:
                        if col in table.colnames:
                            display_cols.append(col)
                    
                    if display_cols:
                        st.dataframe(table[display_cols].to_pandas().head(20), width='stretch')
                    else:
                        st.dataframe(table.to_pandas().head(20), width='stretch')
                    
                    # Add download/display option for FITS files
                    if 'DP.ID' in table.colnames or 'dp_id' in table.colnames:
                        st.markdown("---")
                        st.markdown("**📥 Download & View FITS Image:**")
                        
                        dp_col = 'DP.ID' if 'DP.ID' in table.colnames else 'dp_id'
                        dp_ids = [str(dp) for dp in table[dp_col][:10]]  # Limit to first 10
                        
                        selected_dp = st.selectbox(
                            "Select observation to view:",
                            options=dp_ids,
                            key=f"dp_select_pos_{instrument}",
                            help="Choose a data product to download and display"
                        )
                        
                        if st.button("🔬 Download & Display", 
                                   key=f"download_pos_{instrument}",
                                   width='stretch'):
                            
                            with st.spinner(f"Downloading and processing {selected_dp}..."):
                                from data_fetchers.eso_fetcher import download_and_display_eso_fits
                                
                                result = download_and_display_eso_fits(selected_dp)
                                
                                if result and 'error' not in result:
                                    st.success("✅ FITS file downloaded and processed!")
                                    
                                    # Display image with zoom and download controls
                                    display_image_with_controls(
                                        result['image'],
                                        f"{instrument} - {selected_dp}",
                                        f"eso_pos_{instrument}_{selected_dp.replace('.', '_')}",
                                        target_name=target_name
                                    )
                                    
                                    # Show header info
                                    with st.expander("📋 FITS Header Information"):
                                        for key, value in result['header'].items():
                                            st.text(f"{key:15s}: {value}")
                                        st.text(f"{'Image shape':15s}: {result['shape']}")
                                        st.text(f"{'File path':15s}: {result['filepath']}")
                                    
                                    st.info(f"""
                                    💡 **About this image:**
                                    - Instrument: {result.get('instrument', 'Unknown')}
                                    - Downloaded from ESO archive
                                    - Automatically scaled for display (0.5-99.5 percentile)
                                    - Original FITS file saved locally
                                    """)
                                elif result and 'error' in result:
                                    st.error(f"❌ Error: {result['error']}")
                                    st.info("""
                                    Some ESO files may not contain displayable image data:
                                    - GRAVITY: Interferometry data (not images)
                                    - Some files: Spectra or tables
                                    - Try a different DP.ID from the list
                                    """)
                                else:
                                    st.error("❌ Failed to download or process FITS file")
        else:
            st.warning("❌ No ESO observations found at this position for selected instruments")
            st.info("💡 Try increasing search radius or selecting more instruments")
    
    with col2:
        if st.button("🎯 Query by Name", key="eso_query_name", width='stretch'):
            # Clear previous results
            st.session_state.pop('eso_pos_results', None)
            st.session_state.pop('eso_name_results', None)
            st.session_state['eso_query_done'] = False
            st.session_state['eso_name_query_done'] = False
            
            with st.spinner(f"Searching ESO archive for {target_name}..."):
                try:
                    from data_fetchers.eso_fetcher import query_eso_by_target
                    
                    # Clean target name for query
                    search_name = target_name.split('(')[0].strip()
                    if '=' in search_name:
                        # If target_name is coordinates like "RA=123, Dec=45"
                        st.warning("⚠️ Target name appears to be coordinates. Use 'Query by Position' instead.")
                        search_name = None
                    
                    st.info(f"Resolving '{search_name}' via Simbad and searching ESO...")
                    
                    if search_name:
                        results = query_eso_by_target(
                            search_name,
                            instruments=[inst.lower() for inst in eso_instruments],
                            max_results=100
                        )
                        
                        # Store results in session state
                        st.session_state['eso_name_results'] = results
                        st.session_state['eso_name_query_done'] = True
                        st.session_state['eso_search_name'] = search_name
                    else:
                        st.session_state['eso_name_results'] = {}
                        st.session_state['eso_name_query_done'] = True
                        
                except ImportError:
                    st.error("⚠️ Please install astroquery: `pip install astroquery`")
                except Exception as e:
                    st.error(f"Error querying ESO archive: {e}")
                    import traceback
                    st.caption(f"Debug: {traceback.format_exc()}")
    
    # Display results from session state (outside button callback)
    if 'eso_name_results' in st.session_state and st.session_state.get('eso_name_query_done'):
        results = st.session_state['eso_name_results']
        search_name = st.session_state.get('eso_search_name', target_name)
        
        st.caption(f"🎯 Searched for: '{search_name}'")
        
        if results:
            st.success(f"✅ Found data from {len(results)} instrument(s)")
            
            for instrument, table in results.items():
                with st.expander(f"📊 {instrument} ({len(table)} observations)", expanded=True):
                    st.markdown(f"**{len(table)} observations found**")
                    
                    display_cols = []
                    for col in ['object', 'date_obs', 'filter_path', 'exptime', 'prog_id']:
                        if col in table.colnames:
                            display_cols.append(col)
                    
                    if display_cols:
                        st.dataframe(table[display_cols].to_pandas().head(20), width='stretch')
                    else:
                        st.dataframe(table.to_pandas().head(20), width='stretch')
                    
                    # Add download/display option for FITS files
                    if 'DP.ID' in table.colnames or 'dp_id' in table.colnames:
                        st.markdown("---")
                        st.markdown("**📥 Download & View FITS Image:**")
                        
                        dp_col = 'DP.ID' if 'DP.ID' in table.colnames else 'dp_id'
                        dp_ids = [str(dp) for dp in table[dp_col][:10]]  # Limit to first 10
                        
                        selected_dp = st.selectbox(
                            "Select observation to view:",
                            options=dp_ids,
                            key=f"dp_select_{instrument}",
                            help="Choose a data product to download and display"
                        )
                        
                        if st.button("🔬 Download & Display", 
                                   key=f"download_{instrument}",
                                   width='stretch'):
                            
                            with st.spinner(f"Downloading and processing {selected_dp}..."):
                                from data_fetchers.eso_fetcher import download_and_display_eso_fits
                                
                                result = download_and_display_eso_fits(selected_dp)
                                
                                if result and 'error' not in result:
                                    st.success("✅ FITS file downloaded and processed!")
                                    
                                    # Display image
                                    st.image(result['image'], 
                                            caption=f"{instrument} - {selected_dp}",
                                            width='stretch')
                                    
                                    # Show header info
                                    with st.expander("📋 FITS Header Information"):
                                        for key, value in result['header'].items():
                                            st.text(f"{key:15s}: {value}")
                                        st.text(f"{'Image shape':15s}: {result['shape']}")
                                        st.text(f"{'File path':15s}: {result['filepath']}")
                                    
                                    st.info(f"""
                                    💡 **About this image:**
                                    - Instrument: {result.get('instrument', 'Unknown')}
                                    - Downloaded from ESO archive
                                    - Automatically scaled for display (0.5-99.5 percentile)
                                    - Original FITS file saved locally
                                    """)
                                elif result and 'error' in result:
                                    st.error(f"❌ Error: {result['error']}")
                                    st.info("""
                                    Some ESO files may not contain displayable image data:
                                    - GRAVITY: Interferometry data (not images)
                                    - Some files: Spectra or tables
                                    - Try a different DP.ID from the list
                                    """)
                                else:
                                    st.error("❌ Failed to download or process FITS file")
        else:
            st.warning(f"❌ No ESO observations found for '{search_name}'")
            st.info("""
            **Possible reasons:**
            - Object name not recognized by Simbad (try alternative names)
            - No observations exist for this target in ESO archive
            - Selected instruments haven't observed this target
            
            **Tips:**
            - Try using common names (e.g., "NGC 4151" instead of "NGC4151")
            - Try "Query by Position" if you know the coordinates
            - Check Simbad directly: http://simbad.u-strasbg.fr/simbad/
            - Try different instruments or increase search radius
            """)
    
    
    with st.expander("ℹ️ About ESO Instruments"):
        try:
            from data_fetchers.eso_fetcher import get_eso_instrument_info
            
            info = get_eso_instrument_info()
            
            st.markdown("""
            ### 🔬 Major ESO Imaging Instruments
            
            ESO operates world-class telescopes at Paranal and La Silla observatories in Chile.
            """)
            
            for inst_name in eso_instruments:
                if inst_name in info:
                    inst = info[inst_name]
                    st.markdown(f"""
                    **{inst_name}** - {inst['name']}
                    - **Type:** {inst['type']}
                    - **Telescope:** {inst['telescope']}
                    - **Wavelength:** {inst['wavelength']}
                    - **Field of View:** {inst['fov']}
                    - **Status:** {inst['status']}
                    """)
                    st.markdown("---")
        except:
            st.markdown("""
            **FORS2**: Optical imager/spectrograph on VLT  
            **HAWKI**: Near-IR imager on VLT  
            **MUSE**: Integral field spectrograph on VLT  
            **GRAVITY**: Interferometric beam combiner on VLTI  
            **OMEGACAM**: Wide-field optical imager on VST  
            **VIRCAM**: Wide-field near-IR imager on VISTA  
            """)
    
    with st.expander("🔗 Direct Links to ESO Archive"):
        st.markdown(f"""
        **Search ESO Archive:**
        
        **Science Portal:**
        - [ESO Archive Science Portal](https://archive.eso.org/scienceportal/home)
        
        **TAP Interface (Advanced):**
        - [ESO Programmatic Access](https://archive.eso.org/programmatic/)
        
        **Coordinates for manual search:**
        ```
        RA:  {ra:.6f}° = {ra/15:.6f}h
        Dec: {dec:.6f}°
        ```
        
        **Search radius:** {eso_radius} arcsec
        """)

# HST (Hubble Space Telescope)
with survey_tabs[4]:
    st.markdown("#### Hubble Space Telescope (HST)")
    st.markdown("*High-resolution space-based imaging*")
    
    st.info("""
    🔭 **Hubble Space Telescope** provides the highest resolution optical/UV images available.
    HST coverage is limited - not all targets have HST observations.
    """)
    
    # HST search parameters
    hst_radius = st.slider(
        "Search radius (arcsec)",
        min_value=5.0,
        max_value=200.0,
        value=30.0,
        step=5.0,
        help="Larger radius increases chance of finding HST data",
        key="hst_radius"
    )
    
    hst_instrument = st.selectbox(
        "Preferred Instrument",
        ['Any', 'WFC3', 'ACS', 'WFPC2', 'WFC', 'NICMOS'],
        help="Select specific HST instrument (WFC3 and ACS are most common)",
        key="hst_instrument"
    )
    
    if st.button("🔭 Search for HST Images", key="fetch_hst", width='stretch'):
        with st.spinner("Searching HST archives..."):
            try:
                from data_fetchers.hst_fetcher import (
                    fetch_hst_observations, 
                    get_best_hst_image,
                    search_hla_images,
                    get_mast_hst_images,
                    get_skyview_hst_image,
                    get_hst_preview_from_obs_id
                )
                
                # Query HST observations
                instrument_filter = None if hst_instrument == 'Any' else hst_instrument
                hst_obs = fetch_hst_observations(ra, dec, radius=hst_radius, instrument=instrument_filter)
                
                # Store in session state for persistence across reruns
                st.session_state.hst_obs = hst_obs
                st.session_state.hst_search_params = {'ra': ra, 'dec': dec, 'radius': hst_radius}
                
            except ImportError as e:
                st.error("HST fetcher module not found. Please check installation.")
                st.exception(e)
                st.session_state.hst_obs = None
            except Exception as e:
                st.error(f"Error searching HST archives: {e}")
                st.info("""
                **Troubleshooting:**
                - Check your internet connection
                - ESA/MAST servers may be temporarily unavailable
                - Try again in a few moments
                """)
                st.session_state.hst_obs = None
    
    # Display HST results if available (outside button block so it persists)
    if 'hst_obs' in st.session_state and st.session_state.hst_obs is not None:
        from data_fetchers.hst_fetcher import (
            get_hst_preview_from_obs_id,
            get_best_hst_image,
            search_hla_images,
            get_mast_hst_images,
            get_skyview_hst_image
        )
        
        hst_obs = st.session_state.hst_obs
        
        if len(hst_obs) > 0:
            st.success(f"✓ Found {len(hst_obs)} HST observations!")
            
            # Display observation table
            with st.expander("📊 HST Observations Table", expanded=False):
                # Select relevant columns
                display_cols = []
                for col in ['observation_id', 'instrument_name', 'target_name', 'filter', 'exposure_time']:
                    if col in hst_obs.columns:
                        display_cols.append(col)
                
                if display_cols:
                    st.dataframe(hst_obs[display_cols].head(20), width='stretch')
                else:
                    st.dataframe(hst_obs.head(20), width='stretch')
            
            # Try to get images using multiple methods
            st.markdown("### 🖼️ HST Images")
            
            images_displayed = False
            preview_images_found = False
            
            # Add observation selection UI
            if 'observation_id' in hst_obs.columns:
                # Get unique observation IDs
                all_obs_ids = hst_obs['observation_id'].tolist()
                
                # Create a mapping of obs_id to additional info
                obs_info = {}
                for idx, row in hst_obs.iterrows():
                    obs_id = row['observation_id']
                    instrument = row.get('instrument_name', 'Unknown')
                    target = row.get('target_name', 'Unknown')
                    filters = row.get('filter', 'N/A')
                    obs_info[obs_id] = f"{obs_id} ({instrument}, {target})"
                
                # Initialize session state for selected observations (only if not exists)
                if 'hst_selected_obs' not in st.session_state:
                    st.session_state.hst_selected_obs = all_obs_ids[:3] if len(all_obs_ids) >= 3 else all_obs_ids[:1]
                
                # First check Method 1 for the default selections to see if previews exist
                st.markdown("---")
                st.markdown("#### 🔍 Checking for Preview Images...")
                
                # Cache preview checks to avoid repeated API calls
                if 'hst_preview_cache' not in st.session_state:
                    st.session_state.hst_preview_cache = {}
                
                # MEMORY FIX: Limit cache size to prevent memory buildup
                if len(st.session_state.hst_preview_cache) > 20:
                    # Keep only the 10 most recent entries
                    keys = list(st.session_state.hst_preview_cache.keys())
                    for old_key in keys[:10]:
                        del st.session_state.hst_preview_cache[old_key]
                
                with st.spinner("Checking observation preview availability (this may take a moment)..."):
                    # Quick check only FIRST observation for preview availability
                    # Don't loop through all 3 - that causes long waits
                    check_obs_ids = all_obs_ids[:1]  # Only check first one
                    for check_id in check_obs_ids:
                        # Use cached result if available
                        if check_id in st.session_state.hst_preview_cache:
                            preview_check = st.session_state.hst_preview_cache[check_id]
                        else:
                            # Make the API call
                            preview_check = get_hst_preview_from_obs_id(check_id)
                            # Cache the result
                            st.session_state.hst_preview_cache[check_id] = preview_check
                        
                        if preview_check and preview_check.get('has_previews', False):
                            preview_images_found = True
                            break
                
                # Method 1: Only show full selection UI if previews exist
                if preview_images_found:
                    # Original Method 1 - full multiselect
                    st.markdown("---")
                    st.markdown("#### 🎯 Method 1: Direct Observation Previews")
                    st.info(f"📊 Found {len(all_obs_ids)} total observations. Select which ones to display images for:")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col2:
                        # Quick select buttons
                        if st.button("Select Top 5", help="Select first 5 observations"):
                            st.session_state.hst_selected_obs = all_obs_ids[:5]
                            st.rerun()
                        if st.button("Clear All", help="Deselect all"):
                            st.session_state.hst_selected_obs = []
                            st.rerun()
                        
                        st.metric("Selected", len(st.session_state.hst_selected_obs))
                    
                    with col1:
                        # Multi-select for choosing observations
                        # Validate that default values are in options
                        valid_defaults = [obs_id for obs_id in st.session_state.hst_selected_obs if obs_id in all_obs_ids[:20]]
                        if not valid_defaults and all_obs_ids:
                            valid_defaults = all_obs_ids[:3] if len(all_obs_ids) >= 3 else all_obs_ids[:1]
                        
                        selected_obs_ids = st.multiselect(
                            "Choose observation IDs:",
                            options=all_obs_ids[:20],
                            default=valid_defaults,
                            format_func=lambda x: obs_info.get(x, x),
                            help="Select one or more observations to view their preview images",
                            key='hst_obs_multiselect'
                        )
                        
                        # Update session state with current selection
                        st.session_state.hst_selected_obs = selected_obs_ids
                    
                    if selected_obs_ids:
                        st.success(f"✓ Will fetch images for {len(selected_obs_ids)} selected observation(s)")
                    else:
                        st.warning("⚠️ No observations selected. Please select at least one observation to view images.")
                else:
                    # Collapse Method 1 - no previews found
                    with st.expander("ℹ️ Method 1: Direct Observation Previews (No preview images found)", expanded=False):
                        st.info("""
                        **No preview images available via Method 1.**
                        
                        The selected observations don't have preview JPEGs in MAST's direct observation database.
                        This is normal for some observations.
                        
                        **Please use Method 2 below** - it searches the MAST product database and often finds images that Method 1 misses.
                        """)
                        
                        # Still show which observations were checked
                        st.caption(f"Checked first {len(check_obs_ids)} observations: {', '.join(check_obs_ids)}")
                    
                    # Set selected_obs_ids to empty for Method 1
                    selected_obs_ids = []
            else:
                selected_obs_ids = []
                st.warning("No observation_id column found in results")
            
            # Method 1: Try getting previews directly from selected observation IDs
            if selected_obs_ids:
                st.markdown("---")
                st.markdown("#### Method 1: Direct Observation Previews")
                
                with st.spinner(f"Fetching preview images for {len(selected_obs_ids)} observation(s)..."):
                    for idx, obs_id in enumerate(selected_obs_ids):
                        st.markdown(f"##### Observation {idx+1}/{len(selected_obs_ids)}: `{obs_id}`")
                        
                        # Get instrument and target info if available
                        if obs_id in obs_info:
                            st.caption(obs_info[obs_id])
                        
                        # Use cached preview data if available
                        if 'hst_preview_cache' not in st.session_state:
                            st.session_state.hst_preview_cache = {}
                        
                        if obs_id in st.session_state.hst_preview_cache:
                            preview_data = st.session_state.hst_preview_cache[obs_id]
                        else:
                            preview_data = get_hst_preview_from_obs_id(obs_id)
                            st.session_state.hst_preview_cache[obs_id] = preview_data
                        
                        if preview_data and preview_data.get('has_previews', False):
                            st.markdown(f"**Found {len(preview_data['previews'])} preview image(s)**")
                            
                            # Create columns for preview images
                            num_previews = len(preview_data['previews'])
                            cols_per_row = 3
                            
                            for i in range(0, num_previews, cols_per_row):
                                cols = st.columns(cols_per_row)
                                for j in range(cols_per_row):
                                    if i + j < num_previews:
                                        preview = preview_data['previews'][i + j]
                                        with cols[j]:
                                            try:
                                                # Use interactive viewer if enabled
                                                if use_interactive:
                                                    display_image_interactive(
                                                        preview['url'],
                                                        f"{preview['filename']}\n{preview['type']}",
                                                        f"hst_preview_{obs_id}_{i+j}",
                                                        target_name=target_name,
                                                        width=400,
                                                        height=400
                                                    )
                                                else:
                                                    display_image_with_controls(
                                                        preview['url'],
                                                        f"{preview['filename']}\n{preview['type']}",
                                                        f"hst_preview_{obs_id}_{i+j}",
                                                        target_name=target_name
                                                    )
                                                images_displayed = True
                                            except Exception as e:
                                                st.caption(f"❌ {preview['filename']}")
                                                # Show error for debugging
                                                with st.expander("Error details"):
                                                    st.error(str(e))
                            
                            st.markdown("---")
                        else:
                            st.info(f"ℹ️ No preview images found for `{obs_id}`")
                            st.caption("Note: Some observations don't have preview images. Try Method 2 below or use a different observation.")
                            st.markdown("---")
                
                # Show helpful message if no images in Method 1
                if not images_displayed and selected_obs_ids:
                    st.info("""
                    💡 **Tip:** No preview images were found for the selected observations using Method 1.
                    
                    This can happen because:
                    - Some observations don't have generated preview images
                    - The observation ID format might not match MAST's database
                    - These might be spectroscopic observations (no imaging)
                    
                    **Try these solutions:**
                    1. Scroll down to **Method 2: MAST Product Search** - it often finds images that Method 1 misses
                    2. Select different observations from the dropdown
                    3. Check if the observations have imaging data in the table above
                    """)
            
            # Method 2: Try MAST product list
            if not images_displayed:
                st.markdown("---")
                st.markdown("#### Method 2: MAST Product Search")
                st.caption("Alternative search method - often finds images when Method 1 doesn't")
                
                if 'hst_search_params' in st.session_state:
                    with st.spinner("Searching MAST product database..."):
                        params = st.session_state.hst_search_params
                        mast_images = get_mast_hst_images(params['ra'], params['dec'], radius=params['radius'], max_images=5)
                    
                    if mast_images:
                        for img_info in mast_images:
                            st.markdown(f"**Observation:** {img_info['obs_id']} | **Instrument:** {img_info['instrument']} | **Filters:** {img_info['filters']}")
                            
                            # Try each preview URL
                            img_loaded = False
                            for idx, preview_url in enumerate(img_info['preview_urls']):
                                try:
                                    if use_interactive:
                                        display_image_interactive(
                                            preview_url,
                                            f"{img_info['obs_id']}",
                                            f"hst_mast_{img_info['obs_id']}_{idx}",
                                            target_name=target_name,
                                            width=600,
                                            height=500
                                        )
                                    else:
                                        display_image_with_download(
                                            preview_url, 
                                            f"{img_info['obs_id']}", 
                                            f"{target_name}_HST_{img_info['obs_id']}"
                                        )
                                    img_loaded = True
                                    images_displayed = True
                                    break
                                except Exception as e:
                                    continue
                            
                            if not img_loaded:
                                st.caption(f"Preview not available for {img_info['obs_id']}")
                    else:
                        st.info("No images found in MAST product search.")
                else:
                    st.info("Please search for HST observations first using the button above.")
            
            # Method 3: SkyView HST composite
            if not images_displayed and 'hst_search_params' in st.session_state:
                st.markdown("---")
                st.markdown("#### Method 3: SkyView HST Composite")
                st.info("SkyView generates composite images from multiple HST observations")
                
                params = st.session_state.hst_search_params
                skyview_url = get_skyview_hst_image(params['ra'], params['dec'], size=params['radius']/60.0)
                if skyview_url:
                    try:
                        if use_interactive:
                            display_image_interactive(
                                skyview_url,
                                "SkyView HST Composite",
                                "hst_skyview",
                                target_name=target_name,
                                width=800,
                                height=600
                            )
                        else:
                            display_image_with_download(
                                skyview_url, 
                                "SkyView HST Composite", 
                                f"{target_name}_HST_SkyView"
                            )
                        images_displayed = True
                    except Exception as e:
                        st.warning(f"SkyView image not available: may indicate no HST coverage at this position")
            
            # Method 4: HLA Cutout Service
            if not images_displayed and 'hst_search_params' in st.session_state:
                st.markdown("---")
                st.markdown("#### Method 4: Hubble Legacy Archive (HLA) Cutout")
                st.info("HLA provides processed mosaics if available at this position")
                
                params = st.session_state.hst_search_params
                hla_urls = search_hla_images(params['ra'], params['dec'], radius=params['radius'])
                if hla_urls:
                    # Only show first couple of URLs to avoid too many blank images
                    for i, url in enumerate(hla_urls[:2]):
                        try:
                            import requests
                            from PIL import Image as PILImage
                            from io import BytesIO
                            
                            # Try to load image and check if it's not blank
                            resp = requests.get(url, timeout=10)
                            if resp.status_code == 200:
                                img = PILImage.open(BytesIO(resp.content))
                                # Check if image is not completely black/empty
                                import numpy as np
                                img_array = np.array(img)
                                if img_array.mean() > 1:  # Not a blank image
                                    st.image(url, caption=f"HLA {['ACS-WFC', 'WFC3-UVIS', 'WFPC2', 'Combined'][i]}", width='stretch')
                                    images_displayed = True
                                else:
                                    st.caption(f"No HLA data for filter option {i+1}")
                        except Exception as e:
                            st.caption(f"HLA cutout {i+1} not available")
            
            # Show message if no images were displayed
            if not images_displayed:
                st.warning("""
                ⚠️ **No preview images could be displayed**
                
                This is common for HST data because:
                - Preview images may not be generated for all observations
                - Some observations are spectroscopy (no images)
                - The target may be at the edge of HST pointings
                
                **You can still access the data:**
                - Download full FITS files using the observation IDs below
                - Use the direct archive links provided
                """)
            
            # Method 5: ESA Archive preview (fallback)
            if 'hst_search_params' in st.session_state:
                with st.expander("🔄 Additional: ESA Archive Previews"):
                    params = st.session_state.hst_search_params
                best_img = get_best_hst_image(params['ra'], params['dec'], radius=params['radius'])
                
                if best_img and best_img.get('preview_url'):
                    st.markdown(f"**Observation ID:** {best_img['observation_id']}")
                    st.markdown(f"**Instrument:** {best_img['instrument']}")
                    st.markdown(f"**Target:** {best_img['target_name']}")
                    st.markdown(f"**Filter:** {best_img['filter']}")
                    
                    try:
                        display_image_with_download(
                            best_img['preview_url'], 
                            f"HST - {best_img['instrument']}", 
                            f"{target_name}_HST_{best_img['observation_id']}"
                        )
                    except Exception as e:
                        st.caption(f"ESA preview not available")
                else:
                    st.caption("No ESA archive previews available.")
            
            # Save selected observations and provide download options
            st.markdown("---")
            st.markdown("#### 📥 Save & Download Options")
            
            if 'hst_selected_obs' in st.session_state and st.session_state.hst_selected_obs:
                selected_obs_ids = st.session_state.hst_selected_obs
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📋 Selected Observation IDs:**")
                    
                    # Create downloadable text file with selected obs IDs
                    if 'observation_id' in hst_obs.columns:
                        obs_info = {}
                        for idx, row in hst_obs.iterrows():
                            obs_id = row['observation_id']
                            instrument = row.get('instrument_name', 'Unknown')
                            target = row.get('target_name', 'Unknown')
                            obs_info[obs_id] = f"{obs_id} ({instrument}, {target})"
                        
                        obs_ids_text = "\n".join([f"{obs_id}\t{obs_info.get(obs_id, obs_id)}" for obs_id in selected_obs_ids])
                    else:
                        obs_ids_text = "\n".join(selected_obs_ids)
                    
                    st.download_button(
                        label="💾 Download Selected IDs (TXT)",
                        data=obs_ids_text,
                        file_name=f"hst_observations_{target_name.replace(' ', '_')}.txt",
                        mime="text/plain",
                        help="Download list of selected observation IDs"
                    )
                    
                    # Show the list
                    with st.expander("View selected IDs"):
                        for obs_id in selected_obs_ids:
                            st.code(obs_id, language="text")
                
                with col2:
                    st.markdown("**🔗 Direct Archive Links:**")
                    st.markdown(f"""
                    Search for these observations:
                    
                    **ESA Hubble Archive:**
                    - [Search by coordinates](http://archives.esac.esa.int/ehst/)
                    
                    **MAST Portal:**
                    - [MAST HST Search](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)
                    
                    **Download full FITS files:**
                    1. Copy observation IDs above
                    2. Paste into archive search
                    3. Download calibrated data products
                    """)
            
            # Method 6: Show all available observation IDs for manual download
            st.markdown("---")
            st.markdown("#### 📥 All Available Observations")
            
            if 'observation_id' in hst_obs.columns:
                obs_ids = hst_obs['observation_id'].tolist()[:5]  # First 5
                
                st.markdown("**Top Observation IDs for manual retrieval:**")
                for obs_id in obs_ids:
                    st.code(obs_id, language="text")
                
                st.markdown("""
                **Download full-resolution data:**
                1. Visit [ESA Hubble Archive](http://archives.esac.esa.int/ehst/)
                2. Search by observation ID
                3. Download FITS files for detailed analysis
                
                **Or use [MAST Portal](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)**
                """)
        
        else:
            if 'hst_search_params' in st.session_state:
                st.warning(f"⚠️ No HST observations found within {st.session_state.hst_search_params.get('radius', 10.0)}\" of this target.")
                st.info("""
                **Suggestions:**
                - Increase the search radius
                - HST has limited sky coverage (~5% of the sky)
                - Try searching in MAST Portal directly: https://mast.stsci.edu
                """)
                
                # Still try HLA cutout service
                st.markdown("### Trying HLA Cutout Service...")
                params = st.session_state.hst_search_params
            hla_urls = search_hla_images(params['ra'], params['dec'], radius=params['radius'])
            if hla_urls:
                st.info("Found possible HLA image (may show blank if no data)")
                for url in hla_urls:
                    try:
                        st.image(url, caption="HLA Cutout (if available)", width='stretch')
                    except Exception as e:
                        st.warning(f"No HLA data at this position")
    
    with st.expander("ℹ️ About HST Imaging"):
        st.markdown("""
        **Hubble Space Telescope** provides the highest resolution optical and UV imaging available.
        
        ### 🔬 Key Instruments:
        - **WFC3** (Wide Field Camera 3): UV to near-IR, installed 2009
          - UVIS channel: 200-1000 nm
          - IR channel: 800-1700 nm
        - **ACS** (Advanced Camera for Surveys): Optical, installed 2002
          - Wide Field Channel: High resolution optical
        - **WFPC2** (Wide Field Planetary Camera 2): Historical, 1993-2009
        
        ### 📊 Resolution:
        - **~0.04-0.1 arcsec/pixel** (depending on instrument)
        - **10-20× better than ground-based** seeing
        
        ### 🌟 Best For:
        - Detailed galaxy morphology
        - Central AGN structure
        - Resolving stellar populations
        - Dust lane structure
        - Galaxy interactions and tidal features
        
        ### ⚠️ Limitations:
        - **Limited coverage**: ~5% of sky has HST observations
        - **Small field of view**: Arcminutes, not degrees
        - **Search radius**: May need 10-30" radius to find nearby pointings
        
        ### 📚 Data Archives:
        - **ESA Hubble**: European archive with preview images
        - **MAST**: NASA archive with full datasets
        - **HLA**: Hubble Legacy Archive with processed mosaics
        """)
    
    with st.expander("🔗 Direct Links to HST Archives"):
        st.markdown(f"""
        **Search for HST data at this position:**
        
        **ESA Hubble Science Archive:**
        - [Search RA={ra:.4f}, Dec={dec:.4f}](http://archives.esac.esa.int/ehst/)
        
        **MAST Portal:**
        - [MAST Search](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)
        - Coordinates: {ra:.6f}, {dec:.6f}
        
        **Hubble Legacy Archive (HLA):**
        - [HLA Interactive Display](https://hla.stsci.edu/hlaview.html)
        
        **Direct queries:**
        ```
        RA:  {ra:.6f}
        Dec: {dec:.6f}
        ```
        """)

# JWST (James Webb Space Telescope)
with survey_tabs[5]:
    st.markdown("#### James Webb Space Telescope (JWST)")
    st.markdown("*Infrared space observatory - Launched December 2021*")
    
    st.info("""
    🛰️ **James Webb Space Telescope** provides unprecedented infrared observations.
    JWST data is still being released - famous targets and recent observations available.
    """)
    
    # Initialize JWST session state if not present
    if 'jwst_search_params' not in st.session_state:
        st.session_state.jwst_search_params = None
    if 'jwst_obs' not in st.session_state:
        st.session_state.jwst_obs = None
    if 'jwst_images' not in st.session_state:
        st.session_state.jwst_images = None
    
    # JWST search parameters
    st.markdown("---")
    st.markdown("**Search Parameters:**")
    
    col1, col2 = st.columns(2)
    with col1:
        jwst_radius = st.slider(
            "Search Radius (arcsec)",
            min_value=5.0,
            max_value=300.0,
            value=60.0,
            step=5.0,
            key="jwst_radius",
            help="Larger radius increases chance of finding JWST data"
        )
    
    with col2:
        jwst_instrument = st.selectbox(
            "Instrument",
            options=["All", "NIRCAM", "MIRI", "NIRSPEC", "NIRISS"],
            index=0,
            key="jwst_instrument",
            help="Select specific JWST instrument"
        )
    
    if st.button("🛰️ Search for JWST Images", key="fetch_jwst", use_container_width=True):
        # Create progress container
        progress_container = st.empty()
        status_text = st.empty()
        
        try:
            # Step 1: Query observations
            status_text.info("Step 1/2: Querying MAST for JWST observations...")
            with st.spinner("Searching JWST archives..."):
                # Store search parameters
                st.session_state.jwst_search_params = {
                    'ra': ra,
                    'dec': dec,
                    'radius': jwst_radius,
                    'instrument': None if jwst_instrument == "All" else jwst_instrument
                }
                
                # Query JWST observations
                try:
                    from data_fetchers.jwst_fetcher import fetch_jwst_observations
                    
                    jwst_obs = fetch_jwst_observations(
                        ra=ra,
                        dec=dec,
                        radius=jwst_radius,
                        instrument=None if jwst_instrument == "All" else jwst_instrument,
                        timeout=20  # Reduced timeout
                    )
                    
                    st.session_state.jwst_obs = jwst_obs
                    
                    if jwst_obs is not None and len(jwst_obs) > 0:
                        status_text.success(f"✓ Found {len(jwst_obs)} JWST observations!")
                    else:
                        status_text.warning("No JWST observations found at this location.")
                    
                except ImportError:
                    status_text.error("JWST fetcher module not found. Please check installation.")
                    jwst_obs = None
                    
        except Exception as e:
            status_text.error(f"Error searching JWST archives: {e}")
            st.session_state.jwst_obs = None
        finally:
            # Clear progress indicators after a moment
            import time
            time.sleep(1)
            progress_container.empty()
    
    # Display JWST results if available
    if 'jwst_obs' in st.session_state and st.session_state.jwst_obs is not None:
        jwst_obs = st.session_state.jwst_obs
        
        if len(jwst_obs) > 0:
            st.success(f"✓ Found {len(jwst_obs)} JWST observations!")
            
            # Show observations table
            with st.expander("📊 JWST Observations Table", expanded=False):
                # Select useful columns
                display_cols = []
                for col in ['obs_id', 'instrument_name', 'filters', 'target_name', 'proposal_id', 'exposure_time']:
                    if col in jwst_obs.columns:
                        display_cols.append(col)
                
                if display_cols:
                    st.dataframe(jwst_obs[display_cols], use_container_width=True)
                else:
                    st.dataframe(jwst_obs, use_container_width=True)
            
            # Get and display preview images
            st.markdown("### 🖼️ JWST Images")
            
            # Add button to load images
            if st.button("📷 Load Preview Images", key="load_jwst_images", use_container_width=True):
                # Check if search params exist
                if st.session_state.jwst_search_params is None:
                    st.error("⚠️ Please search for JWST observations first using the button above.")
                else:
                    with st.spinner("Loading preview images from MAST..."):
                        try:
                            from data_fetchers.jwst_fetcher import get_jwst_preview_images
                            
                            params = st.session_state.jwst_search_params
                            
                            images = get_jwst_preview_images(
                                ra=params['ra'],
                                dec=params['dec'],
                                radius=params['radius'],
                                max_images=10,  # Show 10 images
                                instrument=params.get('instrument')
                            )
                            
                            # Store images in session state
                            st.session_state.jwst_images = images
                        except Exception as e:
                            st.error(f"Error loading preview images: {e}")
            
            # Display images if they exist in session state
            if 'jwst_images' in st.session_state and st.session_state.jwst_images:
                images = st.session_state.jwst_images
                
                if images and len(images) > 0:
                    st.success(f"✓ Found {len(images)} images with previews")
                    
                    # Display images
                    for i, img_info in enumerate(images):
                        st.markdown(f"---")
                        st.markdown(f"**Image {i+1}:** {img_info['obs_id']}")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            - **Instrument:** {img_info['instrument']}
                            - **Filters:** {img_info['filters']}
                            - **Target:** {img_info['target']}
                            - **Proposal:** {img_info['proposal_id']}
                            """)
                        
                        with col2:
                            st.markdown(f"**{len(img_info['preview_urls'])}** preview(s) available")
                        
                        # Display preview images
                        if img_info['preview_urls']:
                            for j, preview_url in enumerate(img_info['preview_urls'][:2]):  # Show 2 previews
                                try:
                                    if use_interactive:
                                        display_image_interactive(
                                            preview_url,
                                            f"JWST {img_info['instrument']} - {img_info['filters']}",
                                            f"jwst_{i}_{j}",
                                            target_name=target_name,
                                            width=800,
                                            height=600
                                        )
                                    else:
                                        display_image_with_download(
                                            preview_url,
                                            f"JWST {img_info['instrument']} - {img_info['filters']}",
                                            f"{target_name}_JWST_{img_info['obs_id']}_{j}"
                                        )
                                except Exception as e:
                                    st.warning(f"Could not load preview {j+1}: {e}")
                else:
                    st.warning("⚠️ No preview images found for these observations")
                    st.info("""
                    Preview images may not be available yet for:
                    - Very recent observations
                    - Spectroscopic observations
                    - Some data products still in processing
                    
                    **You can still access the data using the observation IDs above**
                    """)
            
            # Download options
            st.markdown("---")
            st.markdown("#### 📥 Download Options")
            
            if 'obs_id' in jwst_obs.columns:
                obs_ids = jwst_obs['obs_id'].tolist()[:10]
                
                obs_ids_text = "\n".join([str(obs_id) for obs_id in obs_ids])
                
                st.download_button(
                    label="💾 Download Observation IDs (TXT)",
                    data=obs_ids_text,
                    file_name=f"jwst_observations_{target_name.replace(' ', '_')}.txt",
                    mime="text/plain",
                    help="Download list of JWST observation IDs"
                )
                
                st.markdown("**Top Observation IDs:**")
                for obs_id in obs_ids[:5]:
                    st.code(obs_id, language="text")
        
        else:
            if 'jwst_search_params' in st.session_state:
                st.warning(f"⚠️ No JWST observations found within {st.session_state.jwst_search_params.get('radius', 60.0)}\" of this target.")
            else:
                st.warning("⚠️ No JWST observations found.")
            st.info("""
            **Suggestions:**
            - Increase the search radius
            - JWST has observed ~1000 targets so far (growing rapidly!)
            - Try famous targets: Cartwheel Galaxy, Stephan's Quintet, Carina Nebula
            - Search MAST Portal directly: https://mast.stsci.edu
            """)
    
    # Information about JWST
    with st.expander("ℹ️ About JWST Imaging"):
        st.markdown("""
        **James Webb Space Telescope** is the premier infrared space observatory.
        
        ### 🔬 Key Instruments:
        - **NIRCam** (Near Infrared Camera): 0.6-5.0 μm
          - Primary imager with 15+ filters
          - Short and long wavelength channels
        - **MIRI** (Mid-Infrared Instrument): 5-28 μm
          - Mid-IR imaging and spectroscopy
          - 9 imaging filters
        - **NIRSpec** (Near Infrared Spectrograph): 0.6-5.3 μm
          - Multi-object spectroscopy
        - **NIRISS** (Near Infrared Imager/Slitless Spectrograph): 0.8-5.0 μm
          - Wide-field imaging and spectroscopy
        
        ### 📊 Resolution:
        - **~0.031-0.11 arcsec/pixel** (depending on instrument/mode)
        - **Diffraction-limited** in infrared
        
        ### 🌟 Best For:
        - High-redshift galaxies
        - Dusty regions (invisible to Hubble)
        - Stellar populations through dust
        - Protoplanetary disks
        - Exoplanet atmospheres
        
        ### 🚀 Mission Info:
        - **Launched**: December 25, 2021
        - **Location**: L2 Lagrange point (~1.5 million km from Earth)
        - **Mirror**: 6.5 meters (3× larger than Hubble)
        - **Data Release**: Science observations ongoing
        
        ### 📚 Data Archive:
        - **MAST Portal**: Main archive for all JWST data
        - Data is public 12 months after observation (some sooner)
        """)
    
    # Famous JWST targets helper
    with st.expander("🌟 Famous JWST Targets"):
        st.markdown("""
        Try searching these famous JWST targets:
        
        - **Cartwheel Galaxy**: RA=9.4333°, Dec=-33.7128°
        - **Stephan's Quintet**: RA=339.0129°, Dec=33.9589°
        - **Carina Nebula**: RA=161.265°, Dec=-59.866°
        - **Southern Ring Nebula**: RA=151.761°, Dec=-40.444°
        - **SMACS 0723 (Deep Field)**: RA=110.841°, Dec=-73.453°
        - **NGC 628 (Phantom Galaxy)**: RA=24.1739°, Dec=15.7839°
        - **Tarantula Nebula**: RA=84.678°, Dec=-69.103°
        
        **Tip**: Use the "Overview" page to search by name, then come here for images!
        """)
    
    with st.expander("🔗 Direct Links to JWST Archives"):
        st.markdown(f"""
        **Search for JWST data at this position:**
        
        **MAST Portal (Main Archive):**
        - [MAST JWST Search](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)
        - Coordinates: {ra:.6f}, {dec:.6f}
        
        **JWST Science:**
        - [JWST Official Website](https://jwst.nasa.gov/)
        - [Approved Programs](https://www.stsci.edu/jwst/science-execution/approved-programs)
        
        **Direct queries:**
        ```
        RA:  {ra:.6f}
        Dec: {dec:.6f}
        ```
        """)

# Image Enhancement
with survey_tabs[6]:
    st.markdown("#### 🔬 Image Enhancement & Analysis")
    st.markdown("*Reveal hidden structures using advanced filters*")
    
    st.info(f"""
    💡 **Current Settings** (adjust in sidebar):
    - **Source**: {enhance_source}
    - **Gaussian**: {'✓' if apply_gaussian else '✗'} {f'(σ={sigma})' if apply_gaussian else ''}
    - **Meijering**: {'✓' if apply_meijering else '✗'}
    - **Sato**: {'✓' if apply_sato else '✗'}
    - **Advanced**: {'✓' if run_advanced else '✗'}
    """)
    
    if st.button("🔬 Enhance Image", key="enhance_img", width='stretch'):
        try:
            # Progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⏳ Downloading image...")
            progress_bar.progress(10)
            
            import numpy as np
            from PIL import Image
            import requests
            from io import BytesIO
            from skimage import color, filters
            from skimage.filters import meijering, sato, gaussian
            import matplotlib.pyplot as plt
            
            # Get image URL based on source
            if enhance_source == 'SDSS':
                img_url = f"https://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?ra={ra}&dec={dec}&scale=0.4&width={image_size}&height={image_size}"
            elif enhance_source == 'Legacy Survey':
                img_url = f"https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size={int(fov_arcsec)}&layer=ls-dr10&pixscale=0.262"
            else:  # DSS
                size_arcmin = fov_arcsec / 60.0
                img_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra}&d={dec}&e=J2000&h={size_arcmin}&w={size_arcmin}&f=gif"
            
            # Download image with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(img_url, timeout=60)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        st.warning(f"Timeout on attempt {attempt + 1}/{max_retries}. Retrying...")
                        continue
                    else:
                        st.error(f"Image download timed out after {max_retries} attempts. Try a different survey or smaller image size.")
                        raise
                except Exception as e:
                    if attempt < max_retries - 1:
                        st.warning(f"Error on attempt {attempt + 1}/{max_retries}: {e}. Retrying...")
                        continue
                    else:
                        raise
            
            status_text.text("✓ Image downloaded. Processing...")
            progress_bar.progress(30)
            
            # Convert to grayscale numpy array
            # MEMORY FIX: Downsample large images before processing
            if img.width > 800 or img.height > 800:
                img = img.resize((min(800, img.width), min(800, img.height)), Image.Resampling.LANCZOS)
            
            img_gray = color.rgb2gray(np.array(img.convert('RGB')))
            
            status_text.text("🔬 Applying filters...")
            progress_bar.progress(40)
            
            # Apply Gaussian smoothing if selected
            if apply_gaussian:
                img_smooth = gaussian(img_gray, sigma=sigma)
            else:
                img_smooth = img_gray
            
            progress_bar.progress(50)
            status_text.text("📊 Generating visualizations...")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display original
            st.markdown("### 📸 Original Image")
            st.image(img, caption=f"{enhance_source} - Original", width='stretch')
            
            # Apply and display filters
            results = []
            titles = []
            
            if apply_gaussian:
                results.append(img_smooth)
                titles.append(f"Gaussian Smoothed (σ={sigma})")
            
            if apply_meijering:
                st.markdown("### 🌟 Meijering Filter - Linear Structures")
                st.info("**Meijering filter** detects linear structures in different directions - perfect for galaxy arms, filaments, and edges")
                meij = meijering(img_smooth)
                results.append(meij)
                titles.append("Meijering - Filaments")
                
                # Display Meijering result
                fig1, ax1 = plt.subplots(figsize=(8, 8), dpi=80)
                im1 = ax1.imshow(meij, cmap='magma', origin='lower')
                ax1.set_title("Meijering Filter - Linear Structures", fontsize=14, fontweight='bold')
                ax1.axis('off')
                plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
                st.pyplot(fig1, clear_figure=True)
                plt.close('all')
            
            if apply_sato:
                st.markdown("### 🧬 Sato Filter - Tubular Structures")
                st.info("**Sato filter** detects tubular shapes - ideal for thread-like structures and matter filaments")
                sato_img = sato(img_smooth)
                results.append(sato_img)
                titles.append("Sato - Tubular")
                
                # Display Sato result
                fig2, ax2 = plt.subplots(figsize=(8, 8), dpi=80)
                im2 = ax2.imshow(sato_img, cmap='magma', origin='lower')
                ax2.set_title("Sato Filter - Tubular Structures", fontsize=14, fontweight='bold')
                ax2.axis('off')
                plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
                st.pyplot(fig2, clear_figure=True)
                plt.close('all')
            
            # Side-by-side comparison if both filters applied
            if apply_meijering and apply_sato:
                st.markdown("### 🔍 Side-by-Side Comparison")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig3, ax3 = plt.subplots(figsize=(5, 5), dpi=80)
                    ax3.imshow(meijering(img_smooth), cmap='magma', origin='lower')
                    ax3.set_title("Meijering - Linear", fontweight='bold')
                    ax3.axis('off')
                    st.pyplot(fig3, clear_figure=True)
                    plt.close('all')
                
                with col2:
                    fig4, ax4 = plt.subplots(figsize=(5, 5), dpi=80)
                    ax4.imshow(sato(img_smooth), cmap='magma', origin='lower')
                    ax4.set_title("Sato - Tubular", fontweight='bold')
                    ax4.axis('off')
                    st.pyplot(fig4, clear_figure=True)
                    plt.close('all')
                
                # Advanced Analysis Section
                if run_advanced:
                    st.markdown("---")
                    st.markdown("### 🎯 Advanced Feature Analysis")
                    
                    with st.spinner("Performing advanced image analysis..."):
                        from skimage.feature import corner_foerstner, multiscale_basic_features
                        from skimage.segmentation import slic, mark_boundaries
                        from skimage.filters import sobel
                        
                        # 1. Corner Detection (Foerstner)
                        st.markdown("#### 📍 Förstner Corner Detection")
                        st.info("**Förstner detector** identifies reliable keypoints - corners and features with high information content")
                            
                        try:
                            corners = corner_foerstner(img_smooth)
                            corner_response = corners[0]  # Corner strength
                            corner_roundness = corners[1]  # Roundness measure
                            
                            fig_corners, axes_corners = plt.subplots(1, 3, figsize=(12, 4), dpi=80)
                            
                            axes_corners[0].imshow(img_gray, cmap='gray', origin='lower')
                            axes_corners[0].set_title("Original Image", fontweight='bold')
                            axes_corners[0].axis('off')
                            
                            im1 = axes_corners[1].imshow(corner_response, cmap='hot', origin='lower')
                            axes_corners[1].set_title("Corner Strength", fontweight='bold')
                            axes_corners[1].axis('off')
                            plt.colorbar(im1, ax=axes_corners[1], fraction=0.046)
                            
                            im2 = axes_corners[2].imshow(corner_roundness, cmap='viridis', origin='lower')
                            axes_corners[2].set_title("Corner Roundness", fontweight='bold')
                            axes_corners[2].axis('off')
                            plt.colorbar(im2, ax=axes_corners[2], fraction=0.046)
                            
                            plt.tight_layout()
                            st.pyplot(fig_corners, clear_figure=True)
                            plt.close('all')
                            
                        except Exception as e:
                            st.warning(f"Corner detection: {e}")
                        
                        # 2. Multi-scale Features
                        st.markdown("---")
                        st.markdown("#### 🔬 Multi-Scale Feature Extraction")
                        st.info("**Multi-scale features** capture textures, edges, and patterns at different scales - like using multiple magnifying glasses")
                        
                        try:
                            # Prepare clean image
                            img_clean = np.asarray(img_smooth, dtype=float)
                            img_clean = np.nan_to_num(img_clean, nan=0.0, posinf=0.0, neginf=0.0)
                            
                            # Extract features
                            features = multiscale_basic_features(
                                img_clean,
                                intensity=True,
                                edges=True,
                                texture=True
                            )
                            
                            H, W, C = features.shape
                            st.write(f"**Extracted {C} feature channels** ({H}×{W} pixels each)")
                            
                            # Show 6 representative channels
                            n_show = min(6, C)
                            fig_feat, axes_feat = plt.subplots(2, 3, figsize=(12, 8), dpi=80)
                            axes_feat = axes_feat.ravel()
                            
                            channel_names = [
                                "Intensity (Fine)", "Intensity (Coarse)", 
                                "Edge Detection 1", "Edge Detection 2",
                                "Texture Pattern 1", "Texture Pattern 2"
                            ]
                            
                            for i in range(n_show):
                                ch = features[:, :, i]
                                ch_v = (ch - ch.min()) / (ch.max() - ch.min() + 1e-9)
                                axes_feat[i].imshow(ch_v, cmap='nipy_spectral', origin='lower')
                                name = channel_names[i] if i < len(channel_names) else f"Feature {i}"
                                axes_feat[i].set_title(name, fontweight='bold')
                                axes_feat[i].axis('off')
                            
                            plt.tight_layout()
                            st.pyplot(fig_feat, clear_figure=True)
                            plt.close('all')
                            
                            st.success(f"✓ Extracted {C} feature channels showing intensity, edges, and textures at multiple scales")
                            
                        except Exception as e:
                            st.warning(f"Multi-scale features: {e}")
                        
                        # 3. Edge Detection
                        st.markdown("---")
                        st.markdown("#### 📐 Edge Detection (Sobel)")
                        st.info("**Sobel filter** highlights edges and boundaries in the image")
                        
                        try:
                            edges_sobel = sobel(img_smooth)
                            
                            fig_edge, axes_edge = plt.subplots(1, 2, figsize=(10, 4), dpi=80)
                            
                            axes_edge[0].imshow(img_gray, cmap='gray', origin='lower')
                            axes_edge[0].set_title("Original", fontweight='bold')
                            axes_edge[0].axis('off')
                            
                            im_edge = axes_edge[1].imshow(edges_sobel, cmap='plasma', origin='lower')
                            axes_edge[1].set_title("Sobel Edges", fontweight='bold')
                            axes_edge[1].axis('off')
                            plt.colorbar(im_edge, ax=axes_edge[1], fraction=0.046)
                            
                            plt.tight_layout()
                            st.pyplot(fig_edge, clear_figure=True)
                            plt.close('all')
                            
                        except Exception as e:
                            st.warning(f"Edge detection: {e}")
                        
                        # 4. Image Segmentation (SLIC)
                        st.markdown("---")
                        st.markdown("#### 🎨 Image Segmentation (SLIC)")
                        st.info("**SLIC segmentation** divides the image into superpixels - groups of similar pixels")
                        
                        try:
                            # Convert to 3-channel for SLIC
                            img_rgb = np.stack([img_gray, img_gray, img_gray], axis=2)
                            
                            # Apply SLIC
                            segments = slic(img_rgb, n_segments=100, compactness=10, 
                                          sigma=1, start_label=1)
                            
                            # Mark boundaries
                            img_with_boundaries = mark_boundaries(img_rgb, segments, color=(1, 1, 0))
                            
                            fig_seg, axes_seg = plt.subplots(1, 3, figsize=(12, 4), dpi=80)
                            
                            axes_seg[0].imshow(img_gray, cmap='gray', origin='lower')
                            axes_seg[0].set_title("Original", fontweight='bold')
                            axes_seg[0].axis('off')
                            
                            axes_seg[1].imshow(segments, cmap='nipy_spectral', origin='lower')
                            axes_seg[1].set_title(f"Segments (n={segments.max()})", fontweight='bold')
                            axes_seg[1].axis('off')
                            
                            axes_seg[2].imshow(img_with_boundaries, origin='lower')
                            axes_seg[2].set_title("Boundaries Overlay", fontweight='bold')
                            axes_seg[2].axis('off')
                            
                            plt.tight_layout()
                            st.pyplot(fig_seg, clear_figure=True)
                            plt.close('all')
                            
                            st.success(f"✓ Image segmented into {segments.max()} superpixels")
                            
                        except Exception as e:
                            st.warning(f"Segmentation: {e}")
                        
                        st.markdown("---")
                        st.success("✓ Advanced analysis complete!")
                        
                        # Clean up memory after intensive operations
                        clear_matplotlib_memory()
                
                st.success("✓ Image enhancement complete!")
                
                # Force garbage collection after processing
                gc.collect()
                
        except Exception as e:
            st.error(f"Error enhancing image: {e}")
            st.info("""
            💡 **Troubleshooting:**
            - Try **SDSS** (fastest and most reliable)
            - Check your internet connection
            - Reduce image size in sidebar
            - Try coordinates closer to your location
            - Some regions may not be covered by all surveys
            """)
            
            # Suggest alternative
            if enhance_source == 'DSS':
                st.warning("⚠️ DSS can be slow. Try **SDSS** or **Legacy Survey** instead.")
    
    with st.expander("ℹ️ About Image Enhancement"):
        st.markdown("""
        **Image enhancement reveals hidden structures that are barely visible in raw images.**
        
        ### 🌟 Meijering Filter
        - **Purpose**: Detects linear structures in different directions
        - **Best for**: 
          - Galaxy spiral arms
          - Filaments connecting galaxies
          - Linear edges and boundaries
          - Cosmic web structures
        - **How it works**: Mathematically searches for lines and curves at multiple orientations
        
        ### 🧬 Sato Filter
        - **Purpose**: Detects tubular (thread-like) shapes
        - **Best for**:
          - Filamentary structures in nebulae
          - Matter threads in space
          - Elongated features
          - Bridge structures between galaxies
        - **How it works**: Uses eigenvalues of the Hessian matrix to find tube-like patterns
        
        ### 🎯 Advanced Analysis Features
        
        **📍 Förstner Corner Detection:**
        - Identifies reliable keypoints in the image
        - Measures corner strength and roundness
        - Highlights features with high information content
        - Perfect for finding galaxy nuclei and bright regions
        
        **🔬 Multi-Scale Features:**
        - Extracts ~24 feature channels
        - Captures intensity, edges, textures at multiple scales
        - Like using different magnifying glasses on the image
        - Reveals patterns invisible at single scales
        
        **📐 Edge Detection (Sobel):**
        - Highlights all edges and boundaries
        - Shows gradients in brightness
        - Useful for galaxy morphology studies
        
        **🎨 Image Segmentation (SLIC):**
        - Divides image into superpixels
        - Groups similar pixels together
        - Creates natural regions for analysis
        - Useful for identifying distinct structures
        
        ### 📊 Workflow
        1. **Gaussian Smoothing**: Reduces noise for cleaner detection
        2. **Basic Filters**: Meijering/Sato reveal structures
        3. **Advanced Analysis**: Corners, features, edges, segmentation
        4. **Visualization**: Professional colormaps and layouts
        
        ### 💡 Tips
        - Start with **Gaussian smoothing** (σ=2.0)
        - Use **Meijering** for linear filaments
        - Use **Sato** for tube-like structures
        - Try **Advanced Analysis** for comprehensive feature extraction
        - Use **Legacy Survey** for deepest images
        - Compare results across different surveys
        
        ### 🔬 Scientific Applications
        - Detect faint tidal tails in galaxy interactions
        - Reveal dust lanes in edge-on galaxies
        - Find filaments in galaxy clusters
        - Study cosmic web structures
        - Identify faint spiral arms
        - Extract keypoints for image registration
        - Segment galaxies into structural components
        - Analyze multi-scale morphological features
        """)
    
    with st.expander("🔗 Additional Resources"):
        st.markdown(f"""
        **For UV and Infrared wavelengths:**
        
        **UV Images (GALEX):**
        - [MAST GALEX Portal](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)
        - Coordinates: RA={ra:.4f}, Dec={dec:.4f}
        
        **Infrared (2MASS, WISE):**
        - [IRSA Portal](https://irsa.ipac.caltech.edu/)
        - Near-IR and Mid-IR imaging
        
        **Multi-wavelength:**
        - [NASA SkyView](https://skyview.gsfc.nasa.gov/)
        """)

# Gallery view
st.markdown("---")
st.markdown("### 🖼️ Multi-Survey Gallery")

col1, col2 = st.columns(2)

with col1:
    gallery_type = st.radio(
        "Gallery view type",
        ["Color Composites", "Grayscale Comparison", "Both"],
        help="Choose how to display the multi-survey gallery"
    )

with col2:
    auto_load = st.checkbox("Auto-load on button click", value=True)

if st.button("📸 Load Multi-Survey Gallery", type="primary", width='stretch'):
    with st.spinner("Loading images from all surveys..."):
        
        # Color composites
        if gallery_type in ["Color Composites", "Both"]:
            st.markdown("#### 🎨 Color Composite Comparison")
            cols = st.columns(2)
            
            # SDSS Color
            with cols[0]:
                try:
                    scale = arcsec_per_pixel
                    sdss_color_url = (
                        f"http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?"
                        f"ra={ra}&dec={dec}&scale={scale}&width={image_size}&height={image_size}"
                    )
                    display_image_with_download(
                        sdss_color_url, 
                        "SDSS Color (gri)", 
                        f"{target_name}_SDSS_color"
                    )
                except:
                    st.warning("SDSS color unavailable")
            
            # Legacy Survey Color
            with cols[1]:
                try:
                    pixscale = arcsec_per_pixel
                    legacy_color_url = (
                        f"https://www.legacysurvey.org/viewer/jpeg-cutout?"
                        f"ra={ra}&dec={dec}&size={int(fov_arcsec)}&layer=ls-dr10&pixscale={pixscale}"
                    )
                    display_image_with_download(
                        legacy_color_url, 
                        "Legacy Survey Color (grz)", 
                        f"{target_name}_Legacy_color"
                    )
                except:
                    st.warning("Legacy Survey unavailable")
        
        # Grayscale comparison
        if gallery_type in ["Grayscale Comparison", "Both"]:
            st.markdown("---")
            st.markdown("#### ⬛ Grayscale Single-Band Comparison")
            
            # DSS vs Modern
            st.markdown("**Historical vs Modern**")
            cols = st.columns(3)
            
            # DSS (Historical)
            with cols[0]:
                try:
                    dss_size = fov_arcsec / 60.0
                    dss_url = (
                        f"https://archive.stsci.edu/cgi-bin/dss_search?"
                        f"v=poss2ukstu_red&r={ra}&d={dec}&e=J2000&h={dss_size}&w={dss_size}&f=gif&c=none&fov=NONE&v3="
                    )
                    display_image_with_download(
                        dss_url, 
                        "DSS2 Red (Historical)", 
                        f"{target_name}_DSS2_red"
                    )
                except:
                    st.warning("DSS unavailable")
            
            # SDSS r-band
            with cols[1]:
                try:
                    display_image_with_download(
                        sdss_color_url, 
                        "SDSS r-band (Modern)", 
                        f"{target_name}_SDSS_r"
                    )
                except:
                    st.warning("SDSS unavailable")
            
            # Legacy r-band
            with cols[2]:
                try:
                    pixscale = arcsec_per_pixel
                    legacy_r_url = (
                        f"https://www.legacysurvey.org/viewer/jpeg-cutout?"
                        f"ra={ra}&dec={dec}&size={int(fov_arcsec)}&layer=ls-dr10-r&pixscale={pixscale}"
                    )
                    display_image_with_download(
                        legacy_r_url, 
                        "Legacy r-band (Deep)", 
                        f"{target_name}_Legacy_r"
                    )
                except:
                    st.warning("Legacy r-band unavailable")
        
        st.success("✓ Gallery loaded successfully!")

# Image analysis tools
st.markdown("---")
st.markdown("### 🔍 Image Analysis & Comparison")

col1, col2 = st.columns(2)

with col1:
    with st.expander("Visual Inspection Checklist"):
        st.markdown("""
        **Morphology:**
        - [ ] Spiral structure visible?
        - [ ] Disk + bulge components?
        - [ ] Elliptical/spheroidal?
        - [ ] Irregular features?
        
        **Environment:**
        - [ ] Isolated or in group/cluster?
        - [ ] Nearby companions?
        - [ ] Tidal features?
        
        **Activity Indicators:**
        - [ ] Bright nucleus (potential AGN)?
        - [ ] Star-forming regions (HII regions)?
        - [ ] Dust lanes visible?
        """)

with col2:
    with st.expander("🎨 Color vs Grayscale Benefits"):
        st.markdown("""
        **Color Images:**
        - Distinguish star-forming regions (blue) from old stars (red)
        - Identify dust lanes (reddening)
        - Better for morphology classification
        - More intuitive visualization
        
        **Grayscale Images:**
        - Higher dynamic range visibility
        - Better for faint structure detection
        - Easier to compare different wavelengths
        - Historical comparison (DSS)
        - Less affected by color calibration issues
        """)

notes = st.text_area(
    "📝 Your observations:",
    placeholder="Enter notes about the object's appearance, morphology, or interesting features...",
    height=150
)

if notes:
    if st.button("💾 Save Notes"):
        if 'image_notes' not in st.session_state:
            st.session_state.image_notes = {}
        st.session_state.image_notes[target_name] = notes
        st.success("✓ Notes saved!")

# Survey comparison info
st.markdown("---")
st.markdown("### 📊 Survey Comparison")

with st.expander("🔭 Survey Characteristics"):
    comparison_data = {
        'Survey': ['SDSS', 'Legacy Survey', 'DSS2'],
        'Wavelength': ['Optical (ugriz)', 'Optical (grz)', 'Optical (B/R)'],
        'Coverage': ['11,000 deg²', '14,000 deg²', 'Full sky'],
        'Depth': ['r~22.5', 'r~24', 'R~20'],
        'Resolution': ['~1.4"', '~1.3"', '~1-2"'],
        'Era': ['2000-2008', '2014-2023', '1980s-90s'],
        'Best For': ['Quick-look', 'Deep imaging', 'Historical'],
        'Access': ['Direct', 'Direct', 'Direct']
    }
    
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, hide_index=True, width='stretch')
    
    st.markdown("""
    **Enhancement Tab**: Apply Meijering & Sato filters to reveal hidden structures in any survey image.
    
    **UV/IR Access**: External portals linked in Image Enhancement tab.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #B8C5D6; padding: 20px;'>
    <p><b>💡 Tip:</b> Use grayscale images to detect faint structures, and color images for morphology classification</p>
    <p><i>Next: Go to <b>Spectra & Lines</b> page for spectroscopic analysis</i></p>
</div>
""", unsafe_allow_html=True)
