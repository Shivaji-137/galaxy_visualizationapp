# 🌌 Galaxies & AGN Multi-Survey Explorer

A comprehensive Streamlit web application for galaxy and AGN (Active Galactic Nuclei) science, featuring multi-survey data integration, spectral analysis, emission line fitting, BPT classification, and SED visualization.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🔗 **Live App**: [https://galaxy-visualization-analysis.streamlit.app/](https://galaxy-visualization-analysis.streamlit.app/)  
📦 **GitHub**: [https://github.com/Shivaji-137/galaxy_visualizationapp](https://github.com/Shivaji-137/galaxy_visualizationapp)

## 🎯 Overview

A comprehensive tool designed for professional astronomical research. This application integrates data from multiple surveys (Gaia, SDSS, DESI, Pan-STARRS, 2MASS) to provide a unified platform for galaxy and AGN analysis.

### Key Features:

- **Multi-Survey Integration**: DESI, SDSS, Pan-STARRS, 2MASS, Gaia, HST, ESO Archive, **JWST** ⭐ NEW!
- **JWST Data Access**: Query and retrieve James Webb Space Telescope observations and images ⭐ NEW!
- **Smart Image Filtering**: HST/JWST automatically show only i2d (drizzled) images - final science-ready products ⭐ NEW!
- **Interactive Image Viewer**: Zoom, pan, and download full-resolution images with Plotly
- **Spectral Analysis**: Emission line fitting (Hα, Hβ, [OIII], [NII], etc.)
- **BPT Classification**: Distinguish star-forming galaxies, AGN, and composites
- **SED Construction**: Multi-wavelength spectral energy distributions
- **Advanced Image Processing**: Meijering, Sato, Förstner filters for structure detection
- **One-Click Downloads**: Download images from any survey at full archive resolution
- **Interactive Visualizations**: Explore data with modern plotting tools
- **Physical Property Estimation**: Stellar mass, SFR, and metallicity calculations

### Important Notes:

- **Quick-Look Analysis**: This tool provides rapid analysis and approximate measurements
- **Data Attribution**: Always cite the original survey data sources in your publications
- **Educational Purpose**: Designed to make astronomy research accessible to students and researchers

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Shivaji-137/galaxy_visualizationapp.git
cd galaxy_visualizationapp

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Quick Start Guide:

1. Go to the **Overview** page from the sidebar
2. Enter an object name (e.g., "NGC 4151") or coordinates (RA, Dec)
3. Fetch data from available surveys
4. Navigate to specific analysis pages for detailed investigation:
   - **Thumbnails**: Explore multi-band imaging and apply advanced enhancement filters
   - **Spectra & Lines**: Analyze spectra and fit emission/absorption lines
   - **BPT & Classification**: Classify objects using diagnostic diagrams
   - **SED Viewer**: Build and visualize spectral energy distributions
5. Export results for your research

## 📚 Features

### 1. Overview & Search
- Object name resolution using Simbad
- Coordinate-based searches
- Multi-survey catalog queries (Gaia, SDSS, Pan-STARRS, 2MASS)
- Cross-matching between surveys
- Downloadable catalog data

### Supported Query Types:
- **Object names**: NGC numbers, Messier objects, common names
- **Coordinates**: RA and Dec in decimal degrees
- **Cone search**: Search radius around coordinates
- **Source IDs**: Gaia source_id, SDSS objID, etc.

### 2. Multi-Band Imaging with Advanced Enhancement
- **Thumbnail Galleries**:
  - Pan-STARRS grizy cutouts
  - SDSS ugriz imaging
  - Legacy Survey (DECaLS) images
  - HST (Hubble Space Telescope) high-resolution imaging - **i2d only** ⭐
  - **JWST (James Webb Space Telescope) infrared imaging - i2d only** ⭐ NEW!
  - ESO Archive data access
  - DSS (Digitized Sky Survey) historical plates
  - SkyView multi-wavelength surveys
  - Adjustable image size and field of view
  - Side-by-side comparison gallery
  - **Smart Filtering**: HST/JWST automatically filter to show only i2d (drizzled, combined) images for optimal quality

- **Interactive Image Viewer** (NEW):
  - **Interactive Mode Toggle**: Switch between static and interactive display
  - **Plotly-powered Zoom & Pan**: Explore images interactively with smooth zoom and pan
  - **Full-Resolution Download**: Download original uncompressed images via camera icon
  - **Drawing Tools**: Annotate images with lines and freehand drawings
  - **Real-time Controls**: Adjust view with mouse wheel zoom and toolbar controls
  - **Memory Optimized**: Smart image size management for performance

- **Advanced Image Analysis**:
  - **Gaussian Smoothing**: Reduce noise and enhance subtle features
  - **Filament Detection** (Meijering Filter): Detect linear structures and galaxy filaments
  - **Tubular Structure Detection** (Sato Filter): Identify tubular patterns in cosmic structures
  - **Multi-scale Feature Extraction**: Extract features at different scales (intensity, edges, texture)
  - **Förstner Corner Detection**: Identify keypoints and structural features
  - Interactive enhancement controls in sidebar

- **Download Features** (NEW):
  - **One-click Download**: Download button for all survey images (non-interactive mode)
  - **High-Quality Exports**: PNG/JPEG format with proper filenames
  - **Batch Access**: Download multiple images from different surveys
  - **Archive-Quality**: Full resolution from source surveys (SDSS, Pan-STARRS, HST, Legacy)

### 3. JWST (James Webb Space Telescope) Integration ⭐ NEW!

Complete support for JWST observations through a dedicated module:

- **Query JWST Observations**:
  - Query by sky coordinates (RA, Dec, radius)
  - Query by JWST proposal ID
  - Filter by instrument (NIRCAM, MIRI, NIRSPEC, NIRISS, FGS)
  - Filter by specific filters (F277W, F200W, F356W, etc.)
  
- **JWST Instruments Supported**:
  | Instrument | Type | Wavelength | Description |
  |------------|------|------------|-------------|
  | **NIRCAM** | Imager | 0.6-5.0 μm | Primary near-IR camera with 15+ filters |
  | **NIRSPEC** | Spectrograph | 0.6-5.3 μm | Multi-object spectroscopy |
  | **MIRI** | Imager/Spec | 5-28 μm | Mid-IR imaging & spectroscopy |
  | **NIRISS** | Imager/Spec | 0.8-5.0 μm | Wide-field slitless spectroscopy |
  | **FGS** | Guider | 0.6-5.0 μm | Precision pointing |

- **Preview Images**:
  - Get preview images with download URLs
  - Interactive display in Thumbnails page
  - Support for multiple previews per observation
  - **Automatic i2d filtering**: Only final drizzled science products shown (no _cal, _uncal, _rate)
  
- **Famous JWST Targets**:
  - Built-in database of iconic JWST observations
  - Cartwheel Galaxy, Stephan's Quintet, Carina Nebula, and more
  - One-click access to these targets

- **Complete Documentation**:
  - `README_JWST.md` - Module overview and API reference
  - `JWST_GUIDE.md` - User guide with examples
  - `test_jwst.py` - Comprehensive test suite
  - `examples_jwst_usage.py` - Working code examples

**Quick Example:**
```python
from data_fetchers.jwst_fetcher import fetch_jwst_observations

# Query Cartwheel Galaxy
df = fetch_jwst_observations(
    ra=9.4333, 
    dec=-33.7128, 
    radius=60.0,
    instrument='NIRCAM'
)
print(f"Found {len(df)} JWST observations")
```

### 4. Spectroscopy & Emission Lines
- SDSS spectrum retrieval and display
- Interactive spectrum viewer with zoom
- Automated emission line fitting:
  - Hα, Hβ, Hγ, Hδ (Balmer series)
  - [OIII] λλ4959,5007
  - [NII] λλ6548,6583
  - [SII] λλ6716,6731
  - [OI] λ6300
  - [OII] λλ3727,3729
- Gaussian profile fitting with error estimates
- Line flux, equivalent width, and velocity measurements
- Signal-to-noise calculations

### 5. BPT Classification
- Automatic BPT diagram generation
- Object classification:
  - Star-forming galaxies
  - Composite systems
  - AGN (Seyfert)
  - LINERs
- WHAN diagram analysis
- Physical properties:
  - Star formation rate from Hα
  - Gas-phase metallicity
  - Stellar mass estimates

### 6. SED Viewer
- Multi-survey photometry compilation
- Interactive SED plots
- Rest-frame or observed-frame display
- Photometric color calculations
- Export SED data for external fitting

## 🔬 Scientific Use Cases

### Galaxy Properties Research
This tool helps measure key galaxy properties:
- **Stellar Mass**: Estimated from photometry using color-mass relations
- **Star Formation Rate**: Derived from emission lines (Hα) or UV/IR data
- **Metallicity**: From emission line ratios
- **Morphology**: From imaging data analysis

### AGN Detection & Classification
Active Galactic Nuclei identification using:
- **BPT Diagrams**: Emission line ratio classification
- **WHAN Diagrams**: Alternative classification scheme
- **Line Widths**: Broad vs narrow components
- **Multi-wavelength Properties**: When available

### Advanced Image Analysis
- **Structure Detection**: Identify filaments, edges, and tubular structures in galaxies
- **Feature Extraction**: Multi-scale analysis reveals hidden patterns
- **Noise Reduction**: Gaussian smoothing for cleaner visualization
- **Pattern Recognition**: Förstner corners and keypoint detection

### Multi-Wavelength Analysis
- Compare UV, optical, and NIR properties
- Construct SEDs for detailed modeling
- Cross-match between surveys

## 📖 Usage Examples

### Example 1: Analyze a Known Galaxy

```python
# In the Streamlit app:
1. Go to "Overview" page
2. Enter "NGC 4151" in the object name field
3. Click "Resolve Name"
4. Click "Fetch Data from Surveys"
5. Navigate to other pages for detailed analysis
```

### Example 2: Coordinate-Based Search

```python
# In the Streamlit app:
1. Go to "Overview" page
2. Enter RA = 182.636 deg, Dec = 39.408 deg
3. Set search radius to 5 arcsec
4. Fetch data and explore
```

### Example 3: Programmatic Analysis

See `notebooks/example_walkthrough.ipynb` for a complete Python workflow.

## 📁 Project Structure

```
galaxy_visualizationapp/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── README_JWST.md              # JWST module documentation ⭐ NEW!
├── data_fetchers/             # Data acquisition modules
│   ├── __init__.py
│   ├── gaia_fetcher.py        # Gaia DR3 queries
│   ├── sdss_fetcher.py        # SDSS data & spectra
│   ├── panstarrs_fetcher.py   # Pan-STARRS imaging
│   ├── hst_fetcher.py         # Hubble Space Telescope data
│   ├── jwst_fetcher.py        # James Webb Space Telescope data ⭐ NEW!
│   ├── eso_fetcher.py         # ESO Archive access
│   ├── desi_fetcher.py        # DESI spectroscopy
│   └── twomass_fetcher.py     # 2MASS near-IR
├── pages/                     # Streamlit multi-page app
│   ├── 1_📊_Overview.py
│   ├── 2_🖼️_Thumbnails.py    # Now includes JWST tab ⭐ UPDATED!
│   ├── 3_📈_Spectra_and_Lines.py
│   ├── 4_🔬_BPT_Classification.py
│   └── 5_🌈_SED_Viewer.py
├── utils/                     # Analysis utilities
│   ├── __init__.py
│   ├── line_fitting.py        # Emission line fitting
│   ├── spectral_utils.py      # Spectrum analysis
│   ├── bpt_diagrams.py        # BPT classification
│   ├── sed_builder.py         # SED construction
│   ├── memory_utils.py        # Memory optimization for large images
│   ├── style_utils.py         # UI styling utilities
│   └── galaxy_properties.py   # Physical properties
├── test_jwst.py               # JWST module test suite ⭐ NEW!
├── examples_jwst_usage.py     # JWST usage examples ⭐ NEW!
├── JWST_GUIDE.md              # Complete JWST user guide ⭐ NEW!
├── ESO_GUIDE.md               # ESO Archive guide
├── QUICKSTART.md              # Quick start guide
└── SCIENTIFIC_NOTES.md        # Scientific methodology

```


## ⚠️ Scientific Limitations

This tool is designed for **quick-look analysis and educational purposes**.

### Spectroscopy
- Apply proper flux calibration
- Correct for Galactic extinction
- Use detailed line profile modeling
- Consider velocity structure

### SED Fitting
- Apply K-corrections
- Model dust extinction and emission
- Separate stellar and AGN components

### Physical Properties
- Stellar masses: Rough estimates from colors
- SFRs: Uncorrected for extinction; apply Balmer decrement correction
- Metallicity: Strong-line methods have systematic uncertainties

### Data Quality
- Always check data quality flags
- Verify spectral S/N is sufficient
- Cross-check measurements with literature

## 🔗 Data Sources & Attribution

When using this tool for research, please cite the appropriate survey papers:

- **Gaia**: [Gaia Collaboration et al. (2022)](https://ui.adsabs.harvard.edu/abs/2022arXiv220800211G)
- **SDSS**: [York et al. (2000)](https://ui.adsabs.harvard.edu/abs/2000AJ....120.1579Y)
- **Pan-STARRS**: [Chambers et al. (2016)](https://ui.adsabs.harvard.edu/abs/2016arXiv161205560C)
- **2MASS**: [Skrutskie et al. (2006)](https://ui.adsabs.harvard.edu/abs/2006AJ....131.1163S)
- **HST**: [Space Telescope Science Institute](https://archive.stsci.edu/)
- **JWST**: [Gardner et al. (2006)](https://ui.adsabs.harvard.edu/abs/2006SSRv..123..485G) | [MAST JWST Archive](https://mast.stsci.edu/) ⭐ NEW!
- **ESO Archive**: [European Southern Observatory](https://archive.eso.org/)
- **DESI**: [DESI Collaboration et al. (2016)](https://ui.adsabs.harvard.edu/abs/2016arXiv161100036D)

### BPT Diagnostic Papers
- Kauffmann et al. (2003): [2003MNRAS.346.1055K](https://ui.adsabs.harvard.edu/abs/2003MNRAS.346.1055K)
- Kewley et al. (2001): [2001ApJ...556..121K](https://ui.adsabs.harvard.edu/abs/2001ApJ...556..121K)
- Schawinski et al. (2007): [2007MNRAS.382.1415S](https://ui.adsabs.harvard.edu/abs/2007MNRAS.382.1415S)

## 🛠️ Development

### Adding New Features

1. **New Survey Support**: Add fetcher in `data_fetchers/`
2. **Analysis Tools**: Add utilities in `utils/`
3. **Visualization**: Add pages in `pages/`

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📧 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- AstroPy Project for fundamental astronomy tools
- Astroquery for survey data access
- Streamlit for the web framework
- SDSS, Pan-STARRS, Gaia, 2MASS, HST, JWST, ESO, and DESI teams for providing public data

---

## 👨‍🔬 Author

**Shivaji Chaulagain**

I developed this project to bridge the gap between scattered astronomical data sources and create a unified platform for exploring the beauty and physics of galaxies and active galactic nuclei. This tool represents my passion for making astronomy more accessible to researchers, students, and the public.

## 🛠️ Technical Development

- **UI and Optimization**: Built with Claude AI using GitHub Copilot
- **Core Development & Scientific Implementation**: Shivaji Chaulagain


### Research Philosophy

*"I didn't know the beauty of the astronomical objects I would see after I wrote the code. I just followed the API of library packages and wrote the code. I know the physics behind the images and spectra, but I didn't expect that aesthetic I would find in visualizing and studying these objects. I am so much surprised and amazed looking at the result of the project. I am just having goosebumps seeing the images and spectra of different astronomical objects using this app"*

This project embodies my belief that astronomy research should be:
- **Accessible**: Easy-to-use tools for everyone from students to professionals
- **Comprehensive**: Multi-wavelength, multi-survey data integration
- **Beautiful**: Revealing the aesthetic wonder of astronomical objects through advanced image processing
- **Educational**: Fostering scientific literacy and inspiring future astronomers
- **Exploratory**: Making scientific discoveries accessible and visually compelling

### Citation

If you use this tool in your research or education, please cite:

```
Chaulagain, S. (2025). Galaxy & AGN Multi-Survey Explorer. 
GitHub repository: https://github.com/Shivaji-137/galaxy_visualizationapp
Web application: https://galaxy-visualization-analysis.streamlit.app/
```

### Version History

- **v1.0** (Dec 2024): Initial release with multi-survey integration, spectroscopic analysis, BPT classification, and advanced image enhancement features
- **v1.1** (Jan 2025): Added interactive image viewer with Plotly, full-resolution downloads, HST/ESO archive integration, memory optimization, and enhanced download capabilities across all surveys
- **v1.2** (Jan 2026): **JWST Integration** - Added complete James Webb Space Telescope support with dedicated module, preview images, instrument filtering, and famous targets database ⭐ NEW!
- **v1.2.1** (Jan 11, 2026): **i2d Image Filtering** - HST/JWST now show only i2d (drizzled) images, filtering out intermediate calibration products (_cal, _uncal, _rate) for cleaner, professional display of final science-ready images

---

<div align="center">

### 🌌 Exploring the Universe, One Galaxy at a Time 🌌

**Made with ❤️ for Astronomy**

© 2025 Shivaji Chaulagain | MIT License

*"The universe presents itself not just as equations and data points, but as a tangible, visual, breathtakingly beautiful reality we can explore."*

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


</div>
