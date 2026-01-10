"""
Memory management utilities for Streamlit application
"""
import gc
import streamlit as st
from PIL import Image


def limit_image_size(image, max_dimension=1200):
    """
    Limit image size to prevent memory issues
    
    Parameters
    ----------
    image : PIL.Image
        Input image
    max_dimension : int
        Maximum width or height in pixels
    
    Returns
    -------
    PIL.Image
        Resized image if needed
    """
    if image.width > max_dimension or image.height > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    return image


def clean_session_state(keep_recent=10):
    """
    Clean old items from session state to free memory
    
    Parameters
    ----------
    keep_recent : int
        Number of recent items to keep
    """
    if len(st.session_state) > keep_recent:
        # Keep only essential keys
        essential_keys = {'target_coords', 'target_name', 'sdss_data', 'gaia_data'}
        keys_to_remove = [k for k in st.session_state.keys() 
                         if k not in essential_keys]
        
        # Remove old cached data
        for key in keys_to_remove[:len(keys_to_remove)//2]:
            if key in st.session_state:
                del st.session_state[key]
        
        gc.collect()


def get_memory_warning(image_size):
    """
    Display memory warning for large images
    
    Parameters
    ----------
    image_size : int
        Image dimension in pixels
    """
    if image_size > 800:
        st.warning("⚠️ Large image size may use more memory. Consider reducing size if performance is slow.")


def check_image_size_warning(image_size):
    """
    Check and warn about image size
    
    Parameters
    ----------
    image_size : int
        Image dimension in pixels
    """
    if image_size > 1000:
        st.sidebar.warning("⚠️ Very large images may be slow to process")


def clear_matplotlib_memory():
    """
    Clear matplotlib figure cache to free memory
    """
    import matplotlib.pyplot as plt
    plt.close('all')
    gc.collect()
