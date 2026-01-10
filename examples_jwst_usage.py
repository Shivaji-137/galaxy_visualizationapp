#!/usr/bin/env python3
"""
Example usage of JWST data fetching functionality

This script demonstrates how to query JWST observations and retrieve preview images.
"""

from data_fetchers.jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images,
    query_jwst_by_proposal,
    get_jwst_famous_targets,
    get_jwst_filters,
    download_jwst_image
)


def example_1_query_by_coordinates():
    """Example 1: Query JWST observations by sky coordinates"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Query JWST by Coordinates")
    print("=" * 70)
    
    # Cartwheel Galaxy - famous JWST image
    ra = 9.4333  # degrees
    dec = -33.7128  # degrees
    radius = 60.0  # arcseconds
    
    print(f"\nTarget: Cartwheel Galaxy")
    print(f"Coordinates: RA={ra}°, Dec={dec}°")
    print(f"Search radius: {radius} arcsec")
    
    # Query all JWST observations
    df = fetch_jwst_observations(ra, dec, radius=radius)
    
    if df is not None:
        print(f"\nFound {len(df)} JWST observations")
        print("\nAvailable instruments:")
        print(df['instrument_name'].value_counts())
        
        # Save to CSV
        df.to_csv('jwst_cartwheel_observations.csv', index=False)
        print("\n✓ Saved observations to 'jwst_cartwheel_observations.csv'")
    else:
        print("\nNo observations found")


def example_2_query_by_proposal():
    """Example 2: Query JWST observations by proposal ID"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Query JWST by Proposal ID")
    print("=" * 70)
    
    # JWST ERO (Early Release Observations)
    proposal_id = "2727"  # Cartwheel Galaxy
    
    print(f"\nProposal ID: {proposal_id}")
    print("Target: Cartwheel Galaxy (ERO)")
    
    # Query by proposal and filter for NIRCam
    df = query_jwst_by_proposal(
        proposal_id=proposal_id,
        instrument='NIRCAM',
        filters='F277W',  # Specific filter
        max_results=10
    )
    
    if df is not None:
        print(f"\nFound {len(df)} observations with NIRCam F277W filter")
        print("\nFilters used:")
        print(df['filters'].value_counts())
    else:
        print("\nNo observations found")


def example_3_get_preview_images():
    """Example 3: Get JWST preview images"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Get JWST Preview Images")
    print("=" * 70)
    
    # Stephan's Quintet - another famous JWST target
    ra = 339.0129  # degrees
    dec = 33.9589  # degrees
    radius = 120.0  # larger radius for this extended object
    
    print(f"\nTarget: Stephan's Quintet")
    print(f"Coordinates: RA={ra}°, Dec={dec}°")
    
    # Get preview images
    images = get_jwst_preview_images(
        ra, dec,
        radius=radius,
        max_images=5,
        instrument='NIRCAM'
    )
    
    if images is not None:
        print(f"\nFound {len(images)} JWST images with previews")
        
        for i, img in enumerate(images, 1):
            print(f"\nImage {i}:")
            print(f"  Observation ID: {img['obs_id']}")
            print(f"  Instrument: {img['instrument']}")
            print(f"  Filters: {img['filters']}")
            print(f"  Target: {img['target']}")
            print(f"  Proposal: {img['proposal_id']}")
            print(f"  Preview URLs: {len(img['preview_urls'])}")
            
            # Show first preview URL
            if img['preview_urls']:
                print(f"  First preview: {img['preview_urls'][0][:80]}...")
    else:
        print("\nNo preview images found")


def example_4_compare_hst_jwst():
    """Example 4: Use famous JWST targets and filters"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Famous JWST Targets and Filters")
    print("=" * 70)
    
    # Get famous targets
    targets = get_jwst_famous_targets()
    
    print(f"\nAvailable famous JWST targets: {len(targets)}")
    print("\nTargets with coordinates:")
    for name, coords in list(targets.items())[:5]:
        if coords:
            print(f"  • {name}: RA={coords[0]:.4f}°, Dec={coords[1]:.4f}°")
    
    # Query Cartwheel Galaxy
    cartwheel_coords = targets['Cartwheel Galaxy']
    print(f"\n\nQuerying Cartwheel Galaxy...")
    df = fetch_jwst_observations(
        ra=cartwheel_coords[0],
        dec=cartwheel_coords[1],
        radius=60.0,
        instrument='NIRCAM'
    )
    
    if df is not None:
        print(f"✓ Found {len(df)} JWST observations")
        
        # Show available filters
        if 'filters' in df.columns:
            unique_filters = df['filters'].unique()
            print(f"\nFilters used: {', '.join([str(f) for f in unique_filters[:5]])}")
    
    # Show NIRCAM filters
    print("\n\nNIRCAM Available Filters:")
    nircam_filters = get_jwst_filters('NIRCAM')
    print(f"  Short wavelength: {', '.join(nircam_filters[:5])}")
    print(f"  Long wavelength: {', '.join(nircam_filters[5:8])}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("JWST DATA FETCHER - USAGE EXAMPLES")
    print("=" * 70)
    print("\nThese examples demonstrate how to:")
    print("  1. Query JWST observations by coordinates")
    print("  2. Query JWST observations by proposal ID")
    print("  3. Get JWST preview images")
    print("  4. Use famous JWST targets and filters")
    print("\n⚠️  Note: These examples require internet access to MAST archive")
    
    try:
        # Run examples
        example_1_query_by_coordinates()
        example_2_query_by_proposal()
        example_3_get_preview_images()
        example_4_compare_hst_jwst()
        
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - Modify coordinates to query your favorite objects")
        print("  - Use different filters (F150W, F200W, F356W, etc.)")
        print("  - Download preview images using the URLs")
        print("  - Integrate with the Streamlit app for visualization")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
