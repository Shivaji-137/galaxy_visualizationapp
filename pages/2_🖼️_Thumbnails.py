"""
Thumbnails page - Multi-band imaging viewer
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="Thumbnails", page_icon="🖼️", layout="wide")

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

image_size = st.sidebar.slider(
    "Image Size (pixels)",
    min_value=150,
    max_value=1200,
    value=300,
    step=50,
    help="Larger sizes may take longer to load"
)

arcsec_per_pixel = st.sidebar.number_input(
    "Arcsec/pixel",
    min_value=0.1,
    max_value=2.0,
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

survey_tabs = st.tabs(["SDSS", "Legacy Survey", "DSS", "🔬 Image Enhancement"])

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
    
    if st.button("🖼️ Load SDSS Images", key="fetch_sdss", use_container_width=True):
        try:
            if show_color:
                st.markdown("**🎨 SDSS Color Composite (gri)**")
                st.image(sdss_color_url, caption="SDSS gri color composite", use_container_width=True)
            
            if show_bw:
                st.markdown("**⬛ SDSS Individual Bands (Grayscale)**")
                cols = st.columns(5)
                for i, band in enumerate(sdss_bands):
                    with cols[i]:
                        st.image(sdss_color_url, caption=f"{band}-band", use_container_width=True)
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
    
    if st.button("🖼️ Load Legacy Survey Images", key="fetch_legacy", use_container_width=True):
        try:
            if show_color:
                st.markdown("**🎨 Legacy Survey Color Composite (grz)**")
                st.image(legacy_color_url, caption=f"Legacy Survey {legacy_layer}", use_container_width=True)
            
            if show_bw:
                st.markdown("**⬛ Legacy Survey Individual Bands (Grayscale)**")
                cols = st.columns(3)
                for i, (band_name, url) in enumerate(legacy_band_urls.items()):
                    with cols[i]:
                        st.image(url, caption=f"{band_name}-band", use_container_width=True)
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
    
    if st.button("🖼️ Load DSS Image", key="fetch_dss", use_container_width=True):
        try:
            st.markdown(f"**⬛ DSS Grayscale Image**")
            st.image(dss_url, caption=f"DSS - {dss_survey}", use_container_width=True)
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

# Image Enhancement
with survey_tabs[3]:
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
    
    if st.button("🔬 Enhance Image", key="enhance_img", use_container_width=True):
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
            st.image(img, caption=f"{enhance_source} - Original", use_container_width=True)
            
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
                fig1, ax1 = plt.subplots(figsize=(10, 10))
                im1 = ax1.imshow(meij, cmap='magma', origin='lower')
                ax1.set_title("Meijering Filter - Linear Structures", fontsize=14, fontweight='bold')
                ax1.axis('off')
                plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
                st.pyplot(fig1)
                plt.close()
            
            if apply_sato:
                st.markdown("### 🧬 Sato Filter - Tubular Structures")
                st.info("**Sato filter** detects tubular shapes - ideal for thread-like structures and matter filaments")
                sato_img = sato(img_smooth)
                results.append(sato_img)
                titles.append("Sato - Tubular")
                
                # Display Sato result
                fig2, ax2 = plt.subplots(figsize=(10, 10))
                im2 = ax2.imshow(sato_img, cmap='magma', origin='lower')
                ax2.set_title("Sato Filter - Tubular Structures", fontsize=14, fontweight='bold')
                ax2.axis('off')
                plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
                st.pyplot(fig2)
                plt.close()
            
            # Side-by-side comparison if both filters applied
            if apply_meijering and apply_sato:
                st.markdown("### 🔍 Side-by-Side Comparison")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig3, ax3 = plt.subplots(figsize=(6, 6))
                    ax3.imshow(meijering(img_smooth), cmap='magma', origin='lower')
                    ax3.set_title("Meijering - Linear", fontweight='bold')
                    ax3.axis('off')
                    st.pyplot(fig3)
                    plt.close()
                
                with col2:
                    fig4, ax4 = plt.subplots(figsize=(6, 6))
                    ax4.imshow(sato(img_smooth), cmap='magma', origin='lower')
                    ax4.set_title("Sato - Tubular", fontweight='bold')
                    ax4.axis('off')
                    st.pyplot(fig4)
                    plt.close()
                
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
                            
                            fig_corners, axes_corners = plt.subplots(1, 3, figsize=(15, 5))
                            
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
                            st.pyplot(fig_corners)
                            plt.close()
                            
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
                            fig_feat, axes_feat = plt.subplots(2, 3, figsize=(15, 10))
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
                            st.pyplot(fig_feat)
                            plt.close()
                            
                            st.success(f"✓ Extracted {C} feature channels showing intensity, edges, and textures at multiple scales")
                            
                        except Exception as e:
                            st.warning(f"Multi-scale features: {e}")
                        
                        # 3. Edge Detection
                        st.markdown("---")
                        st.markdown("#### 📐 Edge Detection (Sobel)")
                        st.info("**Sobel filter** highlights edges and boundaries in the image")
                        
                        try:
                            edges_sobel = sobel(img_smooth)
                            
                            fig_edge, axes_edge = plt.subplots(1, 2, figsize=(12, 5))
                            
                            axes_edge[0].imshow(img_gray, cmap='gray', origin='lower')
                            axes_edge[0].set_title("Original", fontweight='bold')
                            axes_edge[0].axis('off')
                            
                            im_edge = axes_edge[1].imshow(edges_sobel, cmap='plasma', origin='lower')
                            axes_edge[1].set_title("Sobel Edges", fontweight='bold')
                            axes_edge[1].axis('off')
                            plt.colorbar(im_edge, ax=axes_edge[1], fraction=0.046)
                            
                            plt.tight_layout()
                            st.pyplot(fig_edge)
                            plt.close()
                            
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
                            
                            fig_seg, axes_seg = plt.subplots(1, 3, figsize=(15, 5))
                            
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
                            st.pyplot(fig_seg)
                            plt.close()
                            
                            st.success(f"✓ Image segmented into {segments.max()} superpixels")
                            
                        except Exception as e:
                            st.warning(f"Segmentation: {e}")
                        
                        st.markdown("---")
                        st.success("✓ Advanced analysis complete!")
                
                st.success("✓ Image enhancement complete!")
                
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

if st.button("📸 Load Multi-Survey Gallery", type="primary", use_container_width=True):
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
                    st.image(sdss_color_url, caption="SDSS Color (gri)", use_container_width=True)
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
                    st.image(legacy_color_url, caption="Legacy Survey Color (grz)", use_container_width=True)
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
                    st.image(dss_url, caption="DSS2 Red (Historical)", use_container_width=True)
                except:
                    st.warning("DSS unavailable")
            
            # SDSS r-band
            with cols[1]:
                try:
                    st.image(sdss_color_url, caption="SDSS r-band (Modern)", use_container_width=True)
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
                    st.image(legacy_r_url, caption="Legacy r-band (Deep)", use_container_width=True)
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
    st.dataframe(df, hide_index=True, use_container_width=True)
    
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
