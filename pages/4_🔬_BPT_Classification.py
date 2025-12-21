"""
BPT & Classification page - Galaxy/AGN diagnostic diagrams
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.bpt_diagrams import create_bpt_diagram, calculate_line_ratios, classify_object_bpt
from utils.galaxy_properties import estimate_stellar_mass, estimate_sfr, calculate_metallicity
from utils.style_utils import get_common_css, get_sidebar_header

st.set_page_config(page_title="BPT Classification", page_icon="🔬", layout="wide")

# Apply common styling
st.markdown(get_common_css(), unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown(
    get_sidebar_header("🔬 Diagnostic Tools", "BPT classification & analysis"),
    unsafe_allow_html=True
)

st.title("🔬 BPT Classification & Galaxy Diagnostics")

st.markdown("""
Use emission line ratios to classify objects as star-forming galaxies, composite systems,
AGN (Seyfert), or LINERs using the BPT diagnostic diagram.
""")

# Check prerequisites
if 'target_coords' not in st.session_state or st.session_state.target_coords is None:
    st.warning("⚠️ No target selected. Please go to the Overview page first.")
    st.stop()

target_name = st.session_state.target_name

st.markdown(f"## Target: **{target_name}**")

# Check for line fits
if 'line_fits' not in st.session_state or st.session_state.line_fits is None:
    st.warning("⚠️ No emission line measurements available. Please go to the **Spectra & Lines** page and fit emission lines first.")
    
    st.info("""
    **Required lines for BPT classification:**
    - Hα (6562.8 Å)
    - Hβ (4861.3 Å)
    - [OIII] λ5007
    - [NII] λ6583
    """)
    st.stop()

line_fits = st.session_state.line_fits

# Calculate line ratios
ratios = calculate_line_ratios(line_fits)

st.markdown("---")
st.markdown("### 📊 Line Ratios")

if len(ratios) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'NII_Ha' in ratios:
            st.metric(
                "log([NII]/Hα)",
                f"{ratios['NII_Ha']:.3f}",
                delta=f"±{ratios.get('NII_Ha_err', 0):.3f}" if 'NII_Ha_err' in ratios else None
            )
    
    with col2:
        if 'OIII_Hb' in ratios:
            st.metric(
                "log([OIII]/Hβ)",
                f"{ratios['OIII_Hb']:.3f}",
                delta=f"±{ratios.get('OIII_Hb_err', 0):.3f}" if 'OIII_Hb_err' in ratios else None
            )
    
    with col3:
        if 'SII_Ha' in ratios:
            st.metric(
                "log([SII]/Hα)",
                f"{ratios['SII_Ha']:.3f}"
            )
    
    # Classification
    if 'NII_Ha' in ratios and 'OIII_Hb' in ratios:
        classification = classify_object_bpt(ratios['NII_Ha'], ratios['OIII_Hb'])
        
        st.markdown("---")
        st.markdown("### 🏷️ Classification Result")
        
        # Display classification with color coding
        class_colors = {
            'Star-forming': 'blue',
            'Composite': 'green',
            'AGN (Seyfert)': 'red',
            'LINER': 'orange'
        }
        
        color = class_colors.get(classification, 'gray')
        
        st.markdown(
            f"<h2 style='text-align: center; color: {color};'>{classification}</h2>",
            unsafe_allow_html=True
        )
        
        # Interpretation
        interpretations = {
            'Star-forming': """
            **Star-forming Galaxy**: The emission lines are consistent with ionization by young,
            massive stars (O and B stars) in HII regions. This is typical of actively star-forming
            galaxies where stellar photoionization dominates.
            """,
            'Composite': """
            **Composite System**: The emission line ratios fall between pure star-forming galaxies
            and AGN. This could indicate a mixture of star formation and AGN activity, or a
            transition phase between these states.
            """,
            'AGN (Seyfert)': """
            **Active Galactic Nucleus (Seyfert)**: The high ionization emission line ratios indicate
            the presence of an active supermassive black hole. The emission is powered by accretion
            onto the central black hole, producing a hard ionizing spectrum.
            """,
            'LINER': """
            **LINER (Low-Ionization Nuclear Emission-line Region)**: Shows AGN-like line ratios
            but with weaker [OIII]. Could be a low-luminosity AGN, shock-heated gas, or ionization
            by old post-AGB stars. Common in early-type galaxies.
            """
        }
        
        st.info(interpretations.get(classification, "Classification uncertain."))
    
    else:
        st.warning("Cannot classify: Missing required line ratios ([NII]/Hα and [OIII]/Hβ)")

else:
    st.warning("No line ratios could be calculated. Check that emission lines were successfully fitted.")

# BPT Diagram
st.markdown("---")
st.markdown("### 📈 BPT Diagram")

st.markdown("""
The **Baldwin-Phillips-Terlevich (BPT) diagram** uses emission line ratios to distinguish
between different ionization mechanisms:
- **[NII]/Hα** vs **[OIII]/Hβ** (classical BPT)
""")

try:
    fig = create_bpt_diagram(
        line_results=line_fits,
        show_object=True,
        interactive=True
    )
    
    if fig:
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Could not create BPT diagram.")

except Exception as e:
    st.error(f"Error creating BPT diagram: {e}")

# Additional diagnostics
st.markdown("---")
st.markdown("### 📐 Additional Diagnostic Diagrams")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### WHAN Diagram")
    st.markdown("""
    **W**HAα **E**quivalent width vs **[NII]/Hα**
    
    Alternative classification scheme using:
    - EW(Hα) > 3 Å: Star-forming
    - EW(Hα) < 3 Å & log([NII]/Hα) > -0.4: weak AGN/LINER
    - EW(Hα) < 3 Å & log([NII]/Hα) < -0.4: retired galaxies
    """)
    
    if 'Halpha' in line_fits and 'NII_Ha' in ratios:
        ha_ew = abs(line_fits['Halpha'].ew)
        nii_ha = ratios['NII_Ha']
        
        st.metric("EW(Hα)", f"{ha_ew:.2f} Å")
        st.metric("log([NII]/Hα)", f"{nii_ha:.3f}")
        
        if ha_ew > 3:
            whan_class = "Star-forming (SF)"
        elif ha_ew < 3 and nii_ha > -0.4:
            whan_class = "Weak AGN or LINER"
        else:
            whan_class = "Retired/Passive"
        
        st.success(f"**WHAN Classification:** {whan_class}")

with col2:
    st.markdown("#### [SII] BPT")
    st.markdown("""
    **[SII]/Hα** vs **[OIII]/Hβ**
    
    Alternative BPT diagram using [SII] instead of [NII].
    Helps distinguish between Seyferts and LINERs.
    """)
    
    if 'SII_Ha' in ratios and 'OIII_Hb' in ratios:
        st.metric("log([SII]/Hα)", f"{ratios['SII_Ha']:.3f}")
        st.metric("log([OIII]/Hβ)", f"{ratios['OIII_Hb']:.3f}")
    else:
        st.info("Requires [SII] λλ6716,6731 measurements")

# Physical properties
st.markdown("---")
st.markdown("### 🌌 Derived Physical Properties")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Star Formation Rate")
    
    if 'Halpha' in line_fits:
        ha_result = line_fits['Halpha']
        
        if ha_result.success and ha_result.flux > 0:
            # Get redshift
            z = st.number_input(
                "Redshift (for SFR calculation)",
                min_value=0.0,
                max_value=2.0,
                value=0.01,
                step=0.001,
                format="%.4f",
                key="z_sfr"
            )
            
            sfr_result = estimate_sfr(
                ha_result.flux,
                ha_result.flux_err,
                z=z,
                method='kennicutt12'
            )
            
            st.metric(
                "SFR (M☉/yr)",
                f"{sfr_result['sfr']:.2f}",
                delta=f"±{sfr_result['sfr_err']:.2f}"
            )
            
            st.caption("⚠️ Uncorrected for dust extinction. Actual SFR may be higher.")
        else:
            st.info("Hα measurement required for SFR estimate")

with col2:
    st.markdown("#### Gas-Phase Metallicity")
    
    metallicity = calculate_metallicity(line_fits, method='pp04_o3n2')
    
    if metallicity:
        st.metric(
            "12 + log(O/H)",
            f"{metallicity['12+log(O/H)']:.2f}",
            help=f"Method: {metallicity['method']}"
        )
        
        # Solar metallicity reference
        solar_metal = 8.69  # Asplund et al. 2009
        metal_diff = metallicity['12+log(O/H)'] - solar_metal
        
        if metal_diff > 0:
            st.caption(f"⬆️ {metal_diff:.2f} dex above solar")
        elif metal_diff < 0:
            st.caption(f"⬇️ {abs(metal_diff):.2f} dex below solar")
        else:
            st.caption("≈ Solar metallicity")
    else:
        st.info("Requires [OIII], Hβ, [NII], and Hα for metallicity estimate")

# Stellar mass estimation
if 'catalog_data' in st.session_state and 'sdss' in st.session_state.catalog_data:
    st.markdown("---")
    st.markdown("### ⭐ Stellar Mass Estimate")
    
    sdss_data = st.session_state.catalog_data['sdss']
    
    if len(sdss_data) > 0:
        obj = sdss_data.iloc[0]
        
        if 'g' in obj and 'r' in obj and 'z' in obj:
            z_phot = obj['z'] if 'z' in obj and obj['z'] > 0 else 0.01
            
            log_mass = estimate_stellar_mass(
                obj['g'], obj['r'],
                z=z_phot,
                method='taylor11'
            )
            
            st.metric(
                "log(M*/M☉)",
                f"{log_mass:.2f}",
                help="Estimated from g-r color and r-band absolute magnitude"
            )
            
            st.caption("⚠️ Approximate estimate from photometry. Use SED fitting for accurate masses.")

# Summary
st.markdown("---")
st.markdown("### 📝 Classification Summary")

summary_text = f"""
**Object:** {target_name}

**Classification:**
- BPT: {classification if 'classification' in locals() else 'N/A'}
"""

if 'whan_class' in locals():
    summary_text += f"- WHAN: {whan_class}\n"

summary_text += "\n**Key Properties:**\n"

if 'sfr_result' in locals():
    summary_text += f"- SFR: {sfr_result['sfr']:.2f} ± {sfr_result['sfr_err']:.2f} M☉/yr\n"

if metallicity:
    summary_text += f"- 12+log(O/H): {metallicity['12+log(O/H)']:.2f}\n"

if 'log_mass' in locals():
    summary_text += f"- log(M*/M☉): {log_mass:.2f}\n"

st.text_area("Summary", summary_text, height=250)

if st.button("💾 Save Summary"):
    st.session_state.classification_summary = summary_text
    st.success("Summary saved to session!")

# Footer
st.markdown("---")
st.markdown("*Next: Go to **SED Viewer** page to build spectral energy distributions*")
