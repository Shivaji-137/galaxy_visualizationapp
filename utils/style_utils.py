"""
Shared styling utilities for the Galaxy & AGN Explorer application
"""

def get_common_css():
    """Return common CSS styling for all pages"""
    return """
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
    """


def get_sidebar_header(page_title, page_description):
    """Return formatted sidebar header HTML"""
    return f"""
    <div class='sidebar-header-box'>
        <h2 style='color: #FF6B9D; margin: 0; font-size: 1.5rem;'>{page_title}</h2>
        <p style='color: #B8C5D6; font-size: 0.9rem; margin: 5px 0 0 0; font-style: italic;'>
            {page_description}
        </p>
    </div>
    """


def get_footer():
    """Return formatted footer HTML"""
    return """
    <div class='footer-style'>
        <p style='font-size: 1.2rem; font-weight: 700; margin-bottom: 8px; color: #FF6B9D;'>
            🌌 Galaxy & AGN Explorer v1.0
        </p>
        <p style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px; color: #9BACC8;'>
            Built with ❤️ for Extragalactic Astronomy Research
        </p>
    </div>
    """
