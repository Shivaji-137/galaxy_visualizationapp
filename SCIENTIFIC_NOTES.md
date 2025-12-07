# Scientific Notes & Limitations

## Overview

This document outlines the scientific methodology, limitations, and recommendations for converting this quick-look tool into a rigorous research pipeline.

## Spectroscopic Analysis

### Emission Line Fitting

**Current Implementation:**
- Simple Gaussian profile fitting
- Single-component fits
- Basic continuum estimation

**Limitations:**
- Does not handle blended lines properly
- Ignores broad-line components (important for Type 1 AGN)
- Simple continuum model may fail for complex spectra
- No absorption line fitting


1. **Multi-component fitting**: Use `pPXF` or `GANDALF` for kinematic decomposition
2. **Stellar continuum**: Fit and subtract stellar absorption features
3. **Line blending**: Use simultaneous multi-line fitting (e.g., Hα-[NII]-[SII] complex)
4. **Broad lines**: Add broad Gaussian components for Type 1 AGN
5. **Velocity structure**: Model line profiles for rotation, outflows

**Recommended Tools:**
- `pPXF` (Cappellari 2017) - Stellar kinematics and populations
- `GANDALF` (Sarzi et al. 2006) - Gas and absorption line fitting
- `MPFIT` or `lmfit` - Advanced non-linear fitting
- `IRAF/PyRAF` - Traditional spectroscopy pipeline

### Flux Calibration

**Current Implementation:**
- Uses pipeline-calibrated SDSS spectra as-is
- No additional corrections

**Limitations:**
- May have systematic offsets
- Fiber losses not accounted for
- Atmospheric extinction uncorrected

**For Research:**
1. Check and apply flux calibration using standard stars
2. Apply aperture corrections
3. Correct for Galactic extinction using E(B-V) from dust maps
4. Consider atmospheric conditions

### Redshift Determination

**Current Implementation:**
- Manual redshift input
- No automated measurement

**For Research:**
- Use cross-correlation methods (`pPXF`, `RVSAO`)
- Measure from multiple lines and check consistency
- Account for velocity structure (rotation, outflows)

## BPT Diagnostics

### Classification

**Current Implementation:**
- Uses standard Kauffmann+03, Kewley+01, Schawinski+07 demarcations
- Simple 2D classification

**Limitations:**
- Binary classification ignores transition objects
- Does not account for measurement uncertainties in classification
- No consideration of S/N requirements
- Ignores other diagnostic diagrams ([SII], [OI])

**For Research:**
1. **Multiple diagnostics**: Use all BPT variants ([NII], [SII], [OI])
2. **Uncertainty propagation**: Include errors in classification
3. **S/N cuts**: Require S/N > 3-5 for reliable classification
4. **Alternative methods**: 
   - WHAN (Cid Fernandes et al. 2011)
   - VO87 (Veilleux & Osterbrock 1987)
   - Mass-Excitation diagrams (Juneau et al. 2011)

### Dust Extinction

**Current Implementation:**
- No dust correction
- Balmer decrement reported but not applied

**For Research:**
1. Measure Balmer decrement (Hα/Hβ)
2. Calculate E(B-V) assuming Case B recombination (intrinsic = 2.86)
3. Apply Cardelli+89 or Calzetti+00 extinction curve
4. Correct all line fluxes before calculating ratios

**Formula:**
```
E(B-V) = 1.97 log10(observed Hα/Hβ / 2.86)
A_λ = R_V × E(B-V) × k(λ)
F_corr = F_obs × 10^(0.4 × A_λ)
```

## Physical Properties

### Stellar Mass

**Current Implementation:**
- Simple color-mass relations (Taylor+11, Bell+03)
- Approximate absolute magnitudes

**Limitations:**
- ~0.2-0.3 dex systematic uncertainties
- Assumes universal IMF
- No accounting for dust, age, metallicity degeneracies

**For Research - SED Fitting:**

1. **Prospector** (Johnson et al. 2021)
   - Bayesian SED fitting with FSPS
   - Flexible parameterization
   - Non-parametric SFH

2. **CIGALE** (Boquien et al. 2019)
   - Energy balance (UV-IR)
   - AGN+stellar separation
   - Dust attenuation and emission

3. **FAST** (Kriek et al. 2009)
   - Template fitting
   - Fast for large samples

4. **BAGPIPES** (Carnall et al. 2018)
   - Bayesian Analysis of Galaxies
   - Modern implementation

**Key Considerations:**
- Use broad wavelength coverage (UV to IR)
- Include nebular emission in templates
- Consider AGN contribution
- Explore IMF assumptions
- Check for AGE-metallicity-dust degeneracies

### Star Formation Rate

**Current Implementation:**
- Kennicutt+98/+12 calibrations from Hα
- No dust correction

**Limitations:**
- Hα-derived SFRs underestimate by factor 2-10 in dusty galaxies
- Assumes continuous star formation
- No AGN contribution removed

**For Research:**

1. **Dust Correction:**
   ```
   SFR_corr = SFR_obs × 10^(0.4 × A_Hα)
   ```

2. **Multi-Indicator SFRs:**
   - UV + IR (Kennicutt & Evans 2012)
   - Hα + 24μm (Calzetti et al. 2007)
   - SED-derived (from fitting)

3. **Remove AGN Contribution:**
   - Subtract narrow-line region AGN contribution
   - Use resolved spectroscopy if available

4. **Timescales:**
   - Hα: ~10 Myr
   - FUV: ~100 Myr
   - Consider for interpretation

### Metallicity

**Current Implementation:**
- Strong-line methods (O3N2, N2)
- Pettini & Pagel 2004 calibrations

**Limitations:**
- ~0.1-0.2 dex systematic uncertainties
- Calibration-dependent
- Sensitive to ionization parameter
- Not reliable at high metallicity

**For Research:**

1. **Multiple Calibrations:**
   - Compare O3N2, N2, R23, N2S2
   - Use appropriate calibration for metallicity regime

2. **Direct Method (Te-based):**
   - Requires [OIII]λ4363 detection
   - Most accurate but requires high S/N

3. **Bayesian Methods:**
   - `IZI` (Blanc et al. 2015)
   - Accounts for ionization parameter

4. **Considerations:**
   - Check for AGN contamination
   - Aperture effects in integrated spectra
   - Radial gradients in resolved spectroscopy

## SED Analysis

### Photometry

**Current Implementation:**
- Simple magnitude-to-flux conversion
- Assumes AB system
- No color corrections

**Limitations:**
- Different apertures between surveys
- PSF variations
- Systematic offsets between surveys

**For Research:**

1. **Aperture Matching:**
   - Use aperture corrections
   - Or perform forced photometry

2. **Color Transformations:**
   - Apply filter transmission corrections
   - Match to common system

3. **Systematic Uncertainties:**
   - Add systematic errors (~3-5%)
   - Check zero-point calibrations

### K-Corrections

**Current Implementation:**
- Simple (1+z) corrections
- No proper K-corrections

**For Research:**
- Use `kcorrect` (Blanton & Roweis 2007)
- Or calculate from SED fitting
- Essential for comparing galaxies at different redshifts

## Data Quality Checks

### Before Analysis:

1. **Spectroscopy:**
   - [ ] Check S/N per pixel (require S/N > 3 per Å)
   - [ ] Verify redshift measurement
   - [ ] Check for bad pixels / cosmic rays
   - [ ] Confirm wavelength calibration

2. **Photometry:**
   - [ ] Check saturation flags
   - [ ] Verify PSF quality
   - [ ] Check for blending
   - [ ] Confirm astrometry

3. **Classification:**
   - [ ] Require S/N > 3 for all lines in BPT
   - [ ] Check line detections are real (not artifacts)
   - [ ] Verify continuum placement
   - [ ] Cross-check with alternative diagnostics

## Recommended Workflow for Publication

1. **Data Collection:**
   - Query all available surveys
   - Download raw data when possible
   - Check data quality flags

2. **Spectroscopic Analysis:**
   - Measure redshift with cross-correlation
   - Fit stellar continuum (pPXF)
   - Fit emission lines (GANDALF)
   - Correct for dust extinction
   - Propagate uncertainties

3. **Classification:**
   - Apply S/N cuts
   - Use multiple diagnostic diagrams
   - Consider measurement uncertainties
   - Compare with literature

4. **Physical Properties:**
   - Perform full SED fitting (Prospector/CIGALE)
   - Derive stellar mass, age, SFH
   - Calculate dust-corrected SFR
   - Measure metallicity with multiple methods

5. **Quality Control:**
   - Visual inspection of spectra
   - Check for AGN contamination
   - Verify results with literature values
   - Assess systematic uncertainties

6. **Publication:**
   - Report all assumptions
   - Provide uncertainties
   - Cite all data sources
   - Make data products available

## References

### Key Papers

**Spectroscopy:**
- Cappellari M., 2017, MNRAS, 466, 798 (pPXF)
- Sarzi M. et al., 2006, MNRAS, 366, 1151 (GANDALF)

**BPT Diagrams:**
- Kauffmann G. et al., 2003, MNRAS, 346, 1055
- Kewley L. et al., 2001, ApJ, 556, 121
- Schawinski K. et al., 2007, MNRAS, 382, 1415

**SED Fitting:**
- Johnson B. et al., 2021, ApJS, 254, 22 (Prospector)
- Boquien M. et al., 2019, A&A, 622, A103 (CIGALE)
- Carnall A. et al., 2018, MNRAS, 480, 4379 (BAGPIPES)

**Star Formation:**
- Kennicutt R. & Evans N., 2012, ARA&A, 50, 531
- Calzetti D. et al., 2007, ApJ, 666, 870

**Metallicity:**
- Pettini M. & Pagel B., 2004, MNRAS, 348, L59
- Blanc G. et al., 2015, ApJ, 798, 99 (IZI)

**Dust:**
- Cardelli J. et al., 1989, ApJ, 345, 245
- Calzetti D. et al., 2000, ApJ, 533, 682

## Conclusion

This application provides a solid foundation for exploratory analysis and educational purposes. For research-grade work, follow the recommendations above and always validate results against established literature and alternative methods.
