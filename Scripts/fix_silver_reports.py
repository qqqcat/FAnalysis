#!/usr/bin/env python
"""
Fix SILVER Reports Script
------------------------
This script fixes the SILVER technical analysis report HTML files to correctly
display chart images by updating the chart references from interactive HTML charts
to static PNG images.
"""

import os
import re
import sys
from pathlib import Path

def fix_silver_reports():
    """Fix all SILVER_Beautiful_Report HTML files to correctly display charts."""
    # Define base workspace path
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    base_path = Path(workspace_path).parent
    
    # Define paths to search for SILVER report HTML files
    report_paths = [
        base_path / "Reports",
        base_path / "Scripts" / "Reports",
        base_path / "WebApp" / "Reports"
    ]
    
    # Find all SILVER_Beautiful_Report HTML files
    silver_reports = []
    for path in report_paths:
        if path.exists():
            for file in path.glob("SILVER_Beautiful_Report_*.html"):
                silver_reports.append(file)
    
    if not silver_reports:
        print("No SILVER report HTML files found.")
        return
    
    # Define path to Charts directory
    charts_path = base_path / "Charts"
    
    # Count of fixed files
    fixed_count = 0
    
    # Fix each SILVER report
    for report_file in silver_reports:
        print(f"Processing: {report_file}")
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get the report date from the filename
        date_match = re.search(r'_(\d{8})\.html$', report_file.name)
        if not date_match:
            print(f"  Skipping, couldn't determine date from filename: {report_file.name}")
            continue
        
        report_date = date_match.group(1)
        
        # Use relative paths for chart images - safer across different environments
        relative_path = os.path.relpath(charts_path, report_file.parent)
        relative_path = relative_path.replace('\\', '/')
        
        indicators_png = f"{relative_path}/SILVER_indicators_{report_date}.png"
        bollinger_png = f"{relative_path}/SILVER_bollinger_{report_date}.png"
        
        # Create replacement HTML for charts
        indicators_html = f'''<div class="chart-container">
                <img src="{indicators_png}" class="chart-image" alt="SILVER Indicators Chart">
                <div class="chart-caption">SILVER 价格走势及主要技术指标 (RSI、MACD)</div>
            </div>'''
        
        bollinger_html = f'''<div class="chart-container">
                <img src="{bollinger_png}" class="chart-image" alt="SILVER Bollinger Bands Chart">
                <div class="chart-caption">SILVER 价格走势及布林带指标</div>
            </div>'''
        
        # Pattern to match the existing iframe chart containers
        indicators_iframe_pattern = r'<div class="chart-container">\s*<iframe src="[^"]*?interactive_indicators[^"]*?"[^>]*?>.*?</iframe>\s*<div class="chart-caption">.*?</div>\s*</div>'
        bollinger_iframe_pattern = r'<div class="chart-container">\s*<iframe src="[^"]*?interactive_bollinger[^"]*?"[^>]*?>.*?</iframe>\s*<div class="chart-caption">.*?</div>\s*</div>'
        
        # Replace the iframe containers with image containers
        new_content = re.sub(indicators_iframe_pattern, indicators_html, content, flags=re.DOTALL)
        new_content = re.sub(bollinger_iframe_pattern, bollinger_html, new_content, flags=re.DOTALL)
        
        # Write the updated content back to the file
        if new_content != content:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ Fixed: {report_file}")
            fixed_count += 1
        else:
            print(f"  No changes needed for: {report_file}")
    
    print(f"\nFixed {fixed_count} SILVER report files.")
    print("You can now open these reports in your browser and see the charts correctly.")

if __name__ == "__main__":
    fix_silver_reports()