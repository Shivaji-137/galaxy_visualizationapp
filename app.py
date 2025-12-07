"""
Galaxies & AGN Multi-Survey Explorer
Main Streamlit application entry point
"""
import streamlit as st
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Galaxy & AGN Explorer",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for galaxy-themed appearance inspired by CMB Explorer
st.markdown("""
<style>
    /* Main background with deep space gradient */
    .stApp {
        background: linear-gradient(135deg, #0A0E27 0%, #1a1f3a 50%, #0f1535 100%);
    }
    
    /* Main header styling with galaxy colors */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF6B9D, #C44569, #7B68EE, #4A90E2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        text-shadow: 0 0 20px rgba(255, 107, 157, 0.3);
    }
    
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #B8C5D6;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #0f1535 100%);
        border-right: 1px solid rgba(255, 107, 157, 0.2);
    }
    
    /* Sidebar header box */
    .sidebar-header-box {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #1a1f3a, #0f1535);
        border-radius: 10px;
        margin-bottom: 15px;
        border: 2px solid rgba(255, 107, 157, 0.4);
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FF6B9D !important;
        font-weight: 600;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #FF6B9D;
        font-weight: 700;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(26, 31, 58, 0.8);
        border: 1px solid rgba(255, 107, 157, 0.3);
        border-radius: 8px;
        color: #E0E0E0;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(26, 31, 58, 1);
        border-color: rgba(255, 107, 157, 0.5);
    }
    
    /* Button styling with stellar gradient */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B9D 0%, #C44569 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        text-shadow: none !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #C44569 0%, #FF6B9D 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 157, 0.4);
        color: #FFFFFF !important;
    }
    
    .stButton>button p, .stButton>button div {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar button specific styling */
    [data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, #FF6B9D 0%, #C44569 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        text-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg, #C44569 0%, #FF6B9D 100%);
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stButton>button p {
        color: #FFFFFF !important;
    }
    
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #7B68EE 0%, #4A90E2 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%);
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.4);
    }
    
    /* DataFrame styling */
    .dataframe {
        background-color: rgba(26, 31, 58, 0.6) !important;
        border: 1px solid rgba(255, 107, 157, 0.2);
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(74, 144, 226, 0.2);
        border-left: 4px solid #4A90E2;
        color: #E0E0E0;
    }
    
    .stWarning {
        background-color: rgba(255, 165, 0, 0.2);
        border-left: 4px solid #FFA500;
        color: #E0E0E0;
    }
    
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
        color: #E0E0E0;
    }
    
    .stError {
        background-color: rgba(255, 107, 157, 0.2);
        border-left: 4px solid #FF6B9D;
        color: #E0E0E0;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background-color: rgba(255, 107, 157, 0.2);
    }
    
    /* Text input and number input */
    input {
        background-color: rgba(26, 31, 58, 0.8) !important;
        border: 1px solid rgba(255, 107, 157, 0.3) !important;
        color: #E0E0E0 !important;
        border-radius: 5px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: rgba(26, 31, 58, 0.8);
        border: 1px solid rgba(255, 107, 157, 0.3);
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #E0E0E0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #FF6B9D !important;
    }
    
    /* Subheaders */
    h2, h3 {
        color: #FF6B9D !important;
        font-weight: 600;
    }
    
    /* Horizontal rule */
    hr {
        border-color: rgba(255, 107, 157, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(26, 31, 58, 0.5);
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #B8C5D6;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #FF6B9D !important;
        border-bottom-color: #FF6B9D !important;
    }
    
    /* Footer styling */
    .footer-style {
        text-align: center;
        color: #B8C5D6;
        padding: 30px;
        font-family: 'Inter', sans-serif;
        background: rgba(26, 31, 58, 0.5);
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    /* Info banner styling */
    .info-banner {
        background: linear-gradient(90deg, rgba(26, 31, 58, 0.8) 0%, rgba(15, 21, 53, 0.8) 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 107, 157, 0.3);
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application page"""
    st.markdown('<h1 class="main-header">🌌 Galaxies & AGN Multi-Survey Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">✨ Professional Astronomical Data Analysis • Multi-Survey Integration ✨</p>', unsafe_allow_html=True)
    
    # Add astronomy-themed info banner
    st.markdown("""
    <div class='info-banner'>
        <span style='font-size: 1.1rem; color: #FF6B9D; font-weight: 600;'>
            🔭 Explore galaxies and AGN through multi-wavelength observations from DESI, SDSS, Pan-STARRS & more 🌠
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Introduction
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📡 Data Sources")
        st.markdown("""
        - **DESI** - Deep spectroscopy
        - **SDSS** - Imaging & spectra
        - **Pan-STARRS** - Multi-band imaging
        - **2MASS** - Near-infrared data
        - **Gaia** - Astrometry & photometry
        """)
    
    with col2:
        st.markdown("### 🔬 Analysis Tools")
        st.markdown("""
        - Spectral line fitting (Hα, Hβ, [OIII], etc.)
        - BPT classification diagrams
        - SED construction & visualization
        - Stellar mass & SFR estimates
        - Cross-matching catalogs
        """)
    
    with col3:
        st.markdown("### 📊 Outputs")
        st.markdown("""
        - Multi-band thumbnail galleries
        - Interactive spectral plots
        - Emission line measurements
        - Classification results
        - Exportable data products
        """)
    
    st.markdown("---")
    
    # Getting Started
    st.markdown("## 🚀 Getting Started")
    
    st.markdown("""
    This application provides comprehensive tools for galaxy and AGN analysis using multi-survey data.
    Navigate through the pages using the sidebar to:
    
    1. **Overview** - Start here to search for objects and view basic information
    2. **Thumbnails** - Explore multi-band imaging from various surveys
    3. **Spectra & Lines** - Analyze spectra and fit emission/absorption lines
    4. **BPT & Classification** - Classify objects using diagnostic diagrams
    5. **SED Viewer** - Build and visualize spectral energy distributions
    
    ### Quick Start Guide:
    
    1. Go to the **Overview** page from the sidebar
    2. Enter an object name (e.g., "NGC 4151") or coordinates (RA, Dec)
    3. Fetch data from available surveys
    4. Navigate to specific analysis pages for detailed investigation
    5. Export results for your research
    
    ### Supported Query Types:
    - **Object names**: NGC numbers, Messier objects, common names
    - **Coordinates**: RA and Dec in decimal degrees
    - **Cone search**: Search radius around coordinates
    - **Source IDs**: Gaia source_id, SDSS objID, etc.
    """)
    
    st.markdown("---")
    
    # Scientific Context
    st.markdown("## 📚 Scientific Context")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Galaxy Properties")
        st.markdown("""
        This tool helps measure key galaxy properties:
        - **Stellar Mass**: Estimated from photometry using color-mass relations
        - **Star Formation Rate**: Derived from emission lines (Hα) or UV/IR data
        - **Metallicity**: From emission line ratios
        - **Morphology**: From imaging data analysis
        """)
    
    with col2:
        st.markdown("### AGN Detection")
        st.markdown("""
        Active Galactic Nuclei identification using:
        - **BPT Diagrams**: Emission line ratio classification
        - **WHAN Diagrams**: Alternative classification scheme
        - **Line Widths**: Broad vs narrow components
        - **X-ray Properties**: When available
        """)
    
    st.markdown("---")
    
    # About Section
    with st.expander("ℹ️ About This Tool", expanded=False):
        st.markdown("""
        <div style='color: #E0E0E0; line-height: 1.8;'>
        
        <h3 style='color: #FF6B9D; font-size: 1.5rem;'>🔬 Galaxies & AGN Multi-Survey Explorer</h3>
        
        <p style='color: #B8C5D6; font-size: 1.05rem;'>
        A comprehensive tool designed for professional astronomical research. This application 
        integrates data from multiple surveys to provide a unified platform for galaxy and AGN analysis.
        </p>
        
        <h4 style='color: #FF6B9D; margin-top: 20px;'>🎯 Key Features:</h4>
        <ul style='color: #E0E0E0;'>
            <li><span style='font-weight: 700;'>Multi-Survey Integration</span>: DESI, SDSS, Pan-STARRS, 2MASS, Gaia</li>
            <li><span style='font-weight: 700;'>Spectral Analysis</span>: Emission line fitting (Hα, Hβ, [OIII], [NII], etc.)</li>
            <li><span style='font-weight: 700;'>BPT Classification</span>: Distinguish star-forming galaxies, AGN, and composites</li>
            <li><span style='font-weight: 700;'>SED Construction</span>: Multi-wavelength spectral energy distributions</li>
            <li><span style='font-weight: 700;'>Interactive Visualizations</span>: Explore data with modern plotting tools</li>
        </ul>
        
        <h4 style='color: #FF6B9D; margin-top: 20px;'>⚠️ Important Notes:</h4>
        <ul style='color: #E0E0E0;'>
            <li><span style='font-weight: 700;'>Quick-Look Analysis</span>: This tool provides rapid analysis and approximate measurements</li>
            <li><span style='font-weight: 700;'>Data Attribution</span>: Always cite the original survey data sources in your publications</li>
        </ul>
        
        <h4 style='color: #FF6B9D; margin-top: 20px;'>📊 Data Sources:</h4>
        <ul style='color: #E0E0E0;'>
            <li><span style='color: #7B68EE; font-weight: 700;'>DESI</span>: Dark Energy Spectroscopic Instrument - Deep spectroscopy</li>
            <li><span style='color: #4A90E2; font-weight: 700;'>SDSS</span>: Sloan Digital Sky Survey - Imaging & spectra</li>
            <li><span style='color: #FF6B9D; font-weight: 700;'>Pan-STARRS</span>: Panoramic Survey Telescope - Multi-band imaging</li>
            <li><span style='color: #C44569; font-weight: 700;'>2MASS</span>: Two Micron All-Sky Survey - Near-infrared data</li>
            <li><span style='color: #FFD700; font-weight: 700;'>Gaia</span>: ESA Mission - Astrometry & photometry</li>
        </ul>
        
        </div>
        """, unsafe_allow_html=True)
    
    # References section
    with st.expander("📚 Survey References & Citations"):
        st.markdown("<h3 style='color: #FF6B9D; font-size: 1.5rem;'>📖 Survey Documentation</h3>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #FF6B9D; margin-top: 20px;'>DESI (Dark Energy Spectroscopic Instrument):</h4>", unsafe_allow_html=True)
        st.markdown("""
        - **DESI Collaboration (2016)** - "The DESI Experiment Part I: Science, Targeting, and Survey Design"  
          [arXiv:1611.00036](https://arxiv.org/abs/1611.00036)
        - **Website:** [https://www.desi.lbl.gov](https://www.desi.lbl.gov)
        """)
        
        st.markdown("<h4 style='color: #FF6B9D; margin-top: 20px;'>SDSS (Sloan Digital Sky Survey):</h4>", unsafe_allow_html=True)
        st.markdown("""
        - **York et al. (2000)** - "The Sloan Digital Sky Survey: Technical Summary"  
          *AJ 120, 1579* | [arXiv:astro-ph/0006396](https://arxiv.org/abs/astro-ph/0006396)
        - **Website:** [https://www.sdss.org](https://www.sdss.org)
        """)
        
        st.markdown("<h4 style='color: #FF6B9D; margin-top: 20px;'>Pan-STARRS:</h4>", unsafe_allow_html=True)
        st.markdown("""
        - **Chambers et al. (2016)** - "The Pan-STARRS1 Surveys"  
          [arXiv:1612.05560](https://arxiv.org/abs/1612.05560)
        - **Website:** [https://panstarrs.stsci.edu](https://panstarrs.stsci.edu)
        """)
        
        st.markdown("<h4 style='color: #FF6B9D; margin-top: 20px;'>Gaia:</h4>", unsafe_allow_html=True)
        st.markdown("""
        - **Gaia Collaboration (2016)** - "The Gaia mission"  
          *A&A 595, A1* | [arXiv:1609.04153](https://arxiv.org/abs/1609.04153)
        - **Website:** [https://www.cosmos.esa.int/gaia](https://www.cosmos.esa.int/gaia)
        """)
    
    # Footer with astronomy styling
    st.markdown("---")
    st.markdown("""
    <div class='footer-style'>
        <p style='font-size: 1.5rem; font-weight: 700; margin-bottom: 10px; color: #FF6B9D;'>
            🌌 Galaxy & AGN Explorer v1.0 🔭
        </p>
        <p style='font-size: 1rem; opacity: 0.9; color: #B8C5D6; margin-bottom: 8px;'>
            Built with ❤️ for Extragalactic Astronomy Research
        </p>
        <p style='font-size: 0.95rem; opacity: 0.85; margin-top: 8px; color: #A8B8D0;'>
            💻 Code & Analysis by <span style='color: #FF6B9D; font-weight: 600;'>Shivaji Chaulagain</span>
        </p>
        <p style='font-size: 0.9rem; opacity: 0.8; margin-top: 5px; color: #9BACC8;'>
            🤖 UI Design & Optimization with <span style='color: #00D9FF;'>Claude AI</span> using <span style='color: #7FFF00;'>GitHub Copilot</span>
        </p>
        <p style='font-size: 0.85rem; opacity: 0.7; margin-top: 10px; color: #9BACC8;'>
            🌟 Multi-Survey Integration • Spectral Analysis • BPT Diagnostics • SED Modeling 🌟
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
