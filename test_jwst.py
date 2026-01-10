#!/usr/bin/env python3
"""
Test script for JWST data fetching functionality
"""

from data_fetchers.jwst_fetcher import (
    fetch_jwst_observations,
    get_jwst_preview_images,
    query_jwst_by_proposal,
    get_jwst_instruments_info,
    list_jwst_instruments,
    get_jwst_filters,
    get_jwst_famous_targets
)

def test_jwst_instruments():
    """Test getting JWST instrument information"""
    print("=" * 70)
    print("TEST 1: JWST Instrument Information")
    print("=" * 70)
    
    instruments = get_jwst_instruments_info()
    
    for inst_name, info in instruments.items():
        print(f"\n{inst_name}:")
        print(f"  Name: {info['name']}")
        print(f"  Type: {info['type']}")
        print(f"  Wavelength: {info['wavelength']}")
        print(f"  Description: {info['description']}")
    
    print("\n✓ Test passed!\n")


def test_jwst_by_proposal():
    """Test querying JWST by proposal ID"""
    print("=" * 70)
    print("TEST 2: Query JWST by Proposal ID")
    print("=" * 70)
    
    # Example: JWST Early Release Observations (ERO) - Cartwheel Galaxy
    # Proposal 2727 - NIRCam observations
    proposal_id = "2727"
    
    print(f"\nQuerying JWST proposal {proposal_id}...")
    df = query_jwst_by_proposal(proposal_id, instrument='NIRCAM', max_results=5)
    
    if df is not None and len(df) > 0:
        print(f"\n✓ Found {len(df)} observations")
        print("\nFirst few observations:")
        print(df[['obs_id', 'instrument_name', 'filters', 'target_name']].head())
    else:
        print("\n⚠ No observations found (this may be normal if proposal doesn't exist)")
    
    print("\n✓ Test completed!\n")


def test_jwst_by_coordinates():
    """Test querying JWST by sky coordinates"""
    print("=" * 70)
    print("TEST 3: Query JWST by Coordinates")
    print("=" * 70)
    
    # Example: Cartwheel Galaxy (observed by JWST)
    ra = 9.4333  # degrees
    dec = -33.7128  # degrees
    radius = 60.0  # arcseconds
    
    print(f"\nQuerying JWST at RA={ra}, Dec={dec}, radius={radius}\"...")
    df = fetch_jwst_observations(ra, dec, radius=radius, instrument='NIRCAM')
    
    if df is not None and len(df) > 0:
        print(f"\n✓ Found {len(df)} JWST observations")
        print("\nObservation details:")
        cols = ['obs_id', 'instrument_name', 'filters', 'target_name']
        available_cols = [c for c in cols if c in df.columns]
        print(df[available_cols].head())
    else:
        print("\n⚠ No observations found at these coordinates")
    
    print("\n✓ Test completed!\n")


def test_jwst_preview_images():
    """Test fetching JWST preview images"""
    print("=" * 70)
    print("TEST 4: Fetch JWST Preview Images")
    print("=" * 70)
    
    # Example: Cartwheel Galaxy
    ra = 9.4333
    dec = -33.7128
    radius = 60.0
    
    print(f"\nFetching JWST preview images at RA={ra}, Dec={dec}...")
    images = get_jwst_preview_images(ra, dec, radius=radius, max_images=3)
    
    if images is not None and len(images) > 0:
        print(f"\n✓ Found {len(images)} JWST images with previews")
        for i, img in enumerate(images, 1):
            print(f"\nImage {i}:")
            print(f"  Obs ID: {img['obs_id']}")
            print(f"  Instrument: {img['instrument']}")
            print(f"  Filters: {img['filters']}")
            print(f"  Target: {img['target']}")
            print(f"  Proposal: {img['proposal_id']}")
            print(f"  Number of previews: {len(img['preview_urls'])}")
    else:
        print("\n⚠ No JWST preview images found")
    
    print("\n✓ Test completed!\n")


def test_hst_and_jwst_combined():
    """Test fetching JWST images and famous targets"""
    print("=" * 70)
    print("TEST 5: JWST Famous Targets and Filters")
    print("=" * 70)
    
    # Get famous targets
    targets = get_jwst_famous_targets()
    print(f"\n✓ Found {len(targets)} famous JWST targets")
    print("\nSome famous targets:")
    for name, coords in list(targets.items())[:5]:
        if coords:
            print(f"  {name}: RA={coords[0]:.4f}°, Dec={coords[1]:.4f}°")
    
    # Get instrument filters
    print("\n✓ JWST Filters:")
    for instrument in list_jwst_instruments()[:3]:  # Just show first 3
        filters = get_jwst_filters(instrument)
        print(f"  {instrument}: {len(filters)} filters")
        print(f"    Examples: {', '.join(filters[:5])}")
    
    print("\n✓ Test completed!\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("JWST DATA FETCHER TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        # Test 1: Instrument info (always works, no network needed)
        test_jwst_instruments()
        
        # Test 2-5: Network-dependent tests
        print("⚠️  The following tests require network access to MAST")
        print("⚠️  Some tests may fail if specific objects haven't been observed")
        print("=" * 70 + "\n")
        
        test_jwst_by_proposal()
        test_jwst_by_coordinates()
        test_jwst_preview_images()
        test_hst_and_jwst_combined()
        
        print("=" * 70)
        print("ALL TESTS COMPLETED!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
