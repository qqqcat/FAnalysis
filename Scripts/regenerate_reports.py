#!/usr/bin/env python
"""
Report Regenerator
-----------------
Regenerates all HTML reports with the correct image paths.
"""

import os
import glob
import sys
import traceback
from generate_html_report import generate_html_report

def main():
    """Regenerate all HTML reports."""
    print("Starting report regeneration...")
    
    # Get the Reports directory
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
    
    # Find all indicator report files
    report_files = glob.glob(os.path.join(reports_dir, "*_indicator_report_*.txt"))
    
    if not report_files:
        print("No indicator reports found.")
        return
    
    print(f"Found {len(report_files)} reports to regenerate.\n")
    
    success_count = 0
    error_count = 0
    
    # Process each report
    for i, file_path in enumerate(report_files, 1):
        try:
            filename = os.path.basename(file_path)
            symbol = filename.split('_indicator_report_')[0]
            date = filename.split('_indicator_report_')[1].replace('.txt', '')
            
            print(f"[{i}/{len(report_files)}] Regenerating {symbol} report for {date}...")
            
            # Generate HTML report
            output_path = generate_html_report(symbol, date)
            print(f"  ✓ Report generated: {os.path.basename(output_path)}")
            success_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing {os.path.basename(file_path)}: {str(e)}")
            if '--verbose' in sys.argv:
                print("  Detailed error traceback:")
                traceback.print_exc()
    
    print("\nReport regeneration complete!")
    print(f"Summary: {success_count} reports generated successfully, {error_count} failed")
    
    if error_count > 0:
        print("\nTo view detailed error information, run with the --verbose flag")
        print("Command: python regenerate_reports.py --verbose")

if __name__ == "__main__":
    main()