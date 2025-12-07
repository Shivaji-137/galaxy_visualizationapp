# 🚀 Quick Start Guide

Get up and running with the Galaxy & AGN Explorer in 5 minutes!

## Step 1: Installation (2 minutes)

```bash
# Navigate to the project directory
cd galaxy_visualizationapp

# Install dependencies
pip install -r requirements.txt

# Verify installation (optional)
python verify_install.py
```

## Step 2: Launch Application (30 seconds)

### Option A: Using the launch script
```bash
./run_app.sh
```

### Option B: Direct command
```bash
streamlit run app.py
```

The application will automatically open in your web browser at `http://localhost:8501`

## Step 3: First Analysis (2 minutes)

### Quick Demo with NGC 4151 (well-known Seyfert galaxy)

1. **Go to Overview page** (using sidebar)
   - Enter object name: `NGC 4151`
   - Click "🔍 Resolve Name"
   - Click "🚀 Fetch Data from Surveys"
   - ✓ You should see catalog data from multiple surveys

2. **View Images** → Go to Thumbnails page
   - Click "📸 Load All Available Images"
   - ✓ You should see multi-band cutouts

3. **Analyze Spectrum** → Go to Spectra & Lines page
   - Click "🔍 Fetch SDSS Spectrum"
   - Enter redshift: `0.0033`
   - Select lines to fit (Halpha, Hbeta, OIII_5007, NII_6583)
   - Click "⚡ Fit Selected Lines"
   - ✓ You should see emission line measurements

4. **Classify Object** → Go to BPT & Classification page
   - View the BPT diagram
   - ✓ Should classify as "AGN (Seyfert)" ✓

5. **Build SED** → Go to SED Viewer page
   - Select photometric bands
   - Click "⚡ Build SED"
   - ✓ You should see a multi-wavelength SED

**Congratulations!** You've completed a full galaxy analysis workflow!

## Common First Objects to Try

### Star-forming Galaxies
- `NGC 628` - Face-on spiral, clean star formation
- `M83` - Grand design spiral
- `NGC 3184` - Well-studied star-forming galaxy

### Active Galactic Nuclei
- `NGC 4151` - Bright Seyfert 1.5 (RECOMMENDED FIRST)
- `NGC 1068` - Classic Seyfert 2
- `3C 273` - Famous quasar

### LINER Galaxies
- `NGC 4579` - LINER/Seyfert
- `NGC 4736` - LINER galaxy

### Elliptical Galaxies
- `NGC 4472` - Giant elliptical
- `NGC 4649` - Passive early-type

## Troubleshooting

### "No spectrum found"
- Try increasing search radius to 5-10 arcsec
- Not all objects have SDSS spectroscopy
- Try coordinates instead of name

### "Could not resolve object name"
- Check spelling of object name
- Try alternative names (e.g., "M31" vs "NGC 224")
- Use coordinates as fallback

### "No images available"
- Some regions aren't covered by all surveys
- Try different surveys (Pan-STARRS vs SDSS)
- Adjust image size if timing out

### Installation Issues
```bash
# If you get module not found errors:
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# If astroquery has issues:
pip install astroquery --no-cache-dir
```

## Tips for Best Results

### For Spectroscopy
- ✅ Use objects with z < 0.3 for best line detection
- ✅ Check spectrum S/N before fitting (S/N > 5 recommended)
- ✅ Adjust redshift for better line identification

### For Classification
- ✅ Require S/N > 3 for all lines used in BPT
- ✅ Check multiple diagnostic diagrams
- ✅ Compare with literature values

### For SED Analysis
- ✅ Use all available photometric bands
- ✅ Check for saturation in bright sources
- ✅ Export data for detailed SED fitting tools

## What to Do Next

### For Learning
1. Work through `notebooks/example_walkthrough.ipynb`
2. Read `SCIENTIFIC_NOTES.md` for methodology
3. Try different object types
4. Experiment with parameters

### For Research
1. Analyze your target list
2. Export measurements to CSV
3. Compare with literature
4. Use as preliminary classification

### For Development
1. Read the code structure in `README.md`
2. Check out `utils/` modules
3. Run tests: `python -m pytest tests/`
4. Contribute improvements!

## Need Help?

### Documentation
- 📖 **README.md** - Full documentation
- 🔬 **SCIENTIFIC_NOTES.md** - Scientific methodology
- 📊 **EXAMPLE_OUTPUT.md** - Expected results
- 💼 **PORTFOLIO_BLURB.md** - Project description

### Example Code
- 📓 **notebooks/example_walkthrough.ipynb** - Complete workflow
- 🧪 **tests/test_line_fitting.py** - Testing examples

### In-App Help
- Most pages have tooltips and help text
- Hover over ℹ️ icons for more information
- Check info boxes for guidance

## Performance Tips

### For Faster Loading
- Start with smaller search radii
- Fetch one survey at a time if needed
- Use cached session data (stays in memory)

### For Better Results
- Use higher resolution images when needed
- Adjust smoothing for noisy spectra
- Try different metallicity calibrations

## What's Included

**30 Files:**
- ✅ 20 Python modules
- ✅ 6 Documentation files
- ✅ 1 Jupyter notebook
- ✅ Configuration files

**3,672 Lines of Code**

**Features:**
- ✅ Multi-survey data integration
- ✅ Interactive visualizations
- ✅ Automated line fitting
- ✅ BPT classification
- ✅ SED construction
- ✅ Physical property estimation
- ✅ Exportable results

## Success Checklist

After your first run, you should be able to:

- [ ] Search for objects by name or coordinates
- [ ] Fetch catalog data from multiple surveys
- [ ] View multi-band images
- [ ] Load and display spectra
- [ ] Fit emission lines automatically
- [ ] Generate BPT diagrams
- [ ] Classify galaxies vs AGN
- [ ] Build SEDs from multi-wavelength data
- [ ] Export measurements to CSV

If you can check all boxes, you're ready to use the tool for your research!

## Getting Started Command Summary

```bash
# Clone/navigate to directory
cd galaxy_visualizationapp

# Install
pip install -r requirements.txt

# Verify (optional)
python verify_install.py

# Run
streamlit run app.py

# Or use the helper script
./run_app.sh
```

## First Analysis Command Summary

1. **Overview** → "NGC 4151" → Resolve → Fetch Data
2. **Thumbnails** → Load All Images
3. **Spectra** → Fetch Spectrum → z=0.0033 → Fit Lines
4. **BPT** → View Classification (should be AGN)
5. **SED** → Select bands → Build SED

**Total time: ~5 minutes including loading**

---

🎉 **You're ready to explore galaxies and AGN!** 🎉

For detailed documentation, see `README.md`

For scientific background, see `SCIENTIFIC_NOTES.md`

For example outputs, see `EXAMPLE_OUTPUT.md`
