"""
Script to fix the GOLD_20250503.csv data file by removing the problematic second row
and ensuring all numeric columns are properly formatted.
"""

import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_gold_data_file():
    """Fix the GOLD data file with incorrect format."""
    try:
        # File path
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')
        gold_file = os.path.join(data_dir, 'GOLD_20250503.csv')
        fixed_file = os.path.join(data_dir, 'GOLD_20250503_fixed.csv')
        
        if not os.path.exists(gold_file):
            logger.error(f"File not found: {gold_file}")
            return False
        
        logger.info(f"Reading file: {gold_file}")
        
        # Read the file with header but skip the second row
        # Read the full file first to get header
        with open(gold_file, 'r') as f:
            lines = f.readlines()
        
        # Check if there are at least two lines and the second line has 'GOLD'
        if len(lines) > 1 and 'GOLD' in lines[1]:
            logger.info("Found problematic 'GOLD' row in the second line. Removing it...")
            # Remove the second line (index 1)
            lines.pop(1)
            
            # Write the fixed content to a temporary file
            temp_file = os.path.join(data_dir, 'temp_gold.csv')
            with open(temp_file, 'w') as f:
                f.writelines(lines)
                
            # Now read with pandas
            df = pd.read_csv(temp_file)
            
            # Clean up temporary file
            os.remove(temp_file)
        else:
            # If no problematic second row, just read normally
            df = pd.read_csv(gold_file)
        
        # Convert columns to numeric
        for col in df.columns:
            if col != 'Date':  # Skip Date column
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not convert column {col} to numeric: {str(e)}")
        
        # Drop rows with NaN in essential columns
        essential_columns = ['Open', 'High', 'Low', 'Close']
        for col in essential_columns:
            if col in df.columns:
                df = df.dropna(subset=[col])
        
        # Save the fixed data
        logger.info(f"Saving fixed data to {fixed_file}")
        df.to_csv(fixed_file, index=False)
        
        logger.info("GOLD data file has been fixed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing GOLD data file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_gold_data_file()