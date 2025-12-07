#!/usr/bin/env python3
"""
Command-line tool to fetch Gaia + SDSS + MAST data for a galaxy

Usage:
    python fetch_galaxy_data.py NGC4151
    python fetch_galaxy_data.py --ra 182.636 --dec 39.408
    python fetch_galaxy_data.py M31 --radius 10 --output m31_data.csv
"""
import argparse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetchers.gaia_fetcher import resolve_object_to_coords
from data_fetchers.multi_survey_fetcher import fetch_galaxy_multiband_data, cross_match_catalogs


def main():
    parser = argparse.ArgumentParser(
        description='Fetch multi-survey data for a galaxy from Gaia, SDSS, and MAST',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s NGC4151
  %(prog)s M31 --radius 10
  %(prog)s --ra 182.636 --dec 39.408 --name "My Galaxy"
  %(prog)s NGC4151 --output ngc4151_data --cross-match
        """
    )
    
    # Position arguments
    parser.add_argument(
        'object_name',
        nargs='?',
        help='Object name (e.g., NGC4151, M31)'
    )
    
    # Coordinate arguments
    parser.add_argument(
        '--ra',
        type=float,
        help='Right Ascension in degrees'
    )
    parser.add_argument(
        '--dec',
        type=float,
        help='Declination in degrees'
    )
    
    # Search parameters
    parser.add_argument(
        '--radius',
        type=float,
        default=5.0,
        help='Search radius in arcseconds (default: 5.0)'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        '-o',
        help='Output filename prefix (without extension)'
    )
    parser.add_argument(
        '--cross-match',
        action='store_true',
        help='Cross-match catalogs and save combined table'
    )
    parser.add_argument(
        '--match-radius',
        type=float,
        default=1.0,
        help='Cross-match radius in arcseconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Determine coordinates
    if args.ra is not None and args.dec is not None:
        ra, dec = args.ra, args.dec
        object_name = args.object_name or f"RA{ra:.4f}_Dec{dec:.4f}"
    elif args.object_name:
        print(f"Resolving object name: {args.object_name}")
        coords = resolve_object_to_coords(args.object_name)
        if coords is None:
            print(f"ERROR: Could not resolve '{args.object_name}'")
            print("Try using --ra and --dec coordinates instead")
            sys.exit(1)
        ra, dec = coords
        object_name = args.object_name
    else:
        parser.print_help()
        sys.exit(1)
    
    print()
    print("🌌 GALAXY MULTI-SURVEY DATA FETCHER")
    print()
    
    # Fetch data
    result = fetch_galaxy_multiband_data(
        ra, dec,
        object_name=object_name,
        radius=args.radius
    )
    
    catalogs = result['catalogs']
    
    # Save individual catalogs
    if args.output:
        print()
        print(f"Saving catalog data to files with prefix: {args.output}")
        print()
        
        for survey, df in catalogs.items():
            filename = f"{args.output}_{survey}.csv"
            df.to_csv(filename, index=False)
            print(f"  ✓ Saved {survey.upper():15s}: {filename} ({len(df)} sources)")
        
        # Save summary
        summary_file = f"{args.output}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("GALAXY MULTI-SURVEY DATA FETCH SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Object: {result['summary']['object_name']}\n")
            f.write(f"RA: {result['summary']['ra']:.6f}°\n")
            f.write(f"Dec: {result['summary']['dec']:.6f}°\n")
            f.write(f"Search radius: {result['summary']['radius_arcsec']} arcsec\n\n")
            
            f.write(f"Surveys queried: {result['summary']['n_surveys']}\n")
            f.write(f"Total sources: {result['summary']['total_sources']}\n")
            f.write(f"Fetch time: {result['summary']['fetch_time_sec']:.2f} seconds\n\n")
            
            f.write("Sources per survey:\n")
            for survey, df in catalogs.items():
                f.write(f"  {survey.upper():15s}: {len(df):4d}\n")
        
        print(f"  ✓ Saved summary: {summary_file}")
    
    # Cross-match if requested
    if args.cross_match and len(catalogs) > 1:
        print()
        print("Performing cross-matching...")
        
        matched = cross_match_catalogs(catalogs, match_radius=args.match_radius)
        
        if matched is not None:
            if args.output:
                matched_file = f"{args.output}_crossmatched.csv"
                matched.to_csv(matched_file, index=False)
                print(f"\n  ✓ Saved cross-matched catalog: {matched_file}")
            else:
                print("\nCross-matched catalog preview:")
                print(matched.head())
    
    print()
    print("=" * 70)
    print("✓ COMPLETE!")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    main()
