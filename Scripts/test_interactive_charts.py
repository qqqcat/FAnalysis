import os
import sys
import pandas as pd
import traceback
import numpy as np # Import numpy for NaN handling

# Ensure the script can find other modules in the Scripts directory
# and the root directory for Data/Charts/Reports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root) # Add project root to path

try:
    # Import necessary functions after adjusting path
    from Scripts.calculate_indicators import calculate_indicators # Keep for potential direct use if needed
    from Scripts.generate_charts import generate_parameter_set_charts
    from Scripts.generate_html_report import generate_html_report
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure the script is run from the project root or necessary paths are set.")
    sys.exit(1)

def map_df_to_report_data(df):
    """Maps the latest row of the indicator DataFrame to the report data dictionary."""
    if df is None or df.empty:
        print("Warning: Indicator DataFrame is empty or None. Report will use sample data.")
        return None

    latest_data = df.iloc[-1] # Get the last row (latest data)
    report_data = {}

    # --- Map DataFrame columns to HTML template keys ---
    # Price & Basic Info
    report_data['price'] = latest_data.get('Close', None)
    # 'previous_close' needs to be calculated from the original data before indicators
    # 'change' and 'change_percent' will be calculated in generate_html_report if price/prev_close exist
    report_data['week_low'] = latest_data.get('52_Week_Low', None) # Assuming column name, adjust if needed
    report_data['week_high'] = latest_data.get('52_Week_High', None) # Assuming column name, adjust if needed

    # Moving Averages (Map SMA/EMA to ma keys)
    ma_map = {
        'SMA5': 'ma5', 'SMA10': 'ma10', 'SMA20': 'ma20', 'SMA50': 'ma50',
        'SMA100': 'ma100', 'SMA150': 'ma150', 'SMA200': 'ma200', # Add more if needed
        'EMA12': 'ema12', 'EMA26': 'ema26', 'EMA50': 'ema50', 'EMA200': 'ema200' # Add more if needed
    }
    for df_col, template_key in ma_map.items():
        report_data[template_key] = latest_data.get(df_col, None)

    # Oscillators
    report_data['rsi'] = latest_data.get('RSI', None) # Default RSI
    report_data['stoch_k'] = latest_data.get('STOCHk_14_3_3', None) # Example name, adjust if needed
    report_data['stoch_d'] = latest_data.get('STOCHd_14_3_3', None) # Example name, adjust if needed
    report_data['macd'] = latest_data.get('MACD', None) # Default MACD
    report_data['macd_signal'] = latest_data.get('MACD_Signal', None)
    report_data['macd_histogram'] = latest_data.get('MACD_Histogram', None)

    # Volatility
    report_data['bb_upper'] = latest_data.get('BB_High', None) # Default BB
    report_data['bb_middle'] = latest_data.get('BB_Mid', None)
    report_data['bb_lower'] = latest_data.get('BB_Low', None)
    report_data['bb_width'] = latest_data.get('BB_Width', None) # Assuming BB_Width is calculated
    report_data['atr'] = latest_data.get('ATR', None) # Default ATR

    # Support/Resistance (These are often calculated differently, using sample for now)
    # If calculate_indicators adds pivot points, map them here. Example:
    # report_data['support'] = latest_data.get('Pivot_S1', None)
    # report_data['resistance'] = latest_data.get('Pivot_R1', None)
    # report_data['s2'] = latest_data.get('Pivot_S2', None)
    # report_data['s3'] = latest_data.get('Pivot_S3', None)
    # report_data['r2'] = latest_data.get('Pivot_R2', None)
    # report_data['r3'] = latest_data.get('Pivot_R3', None)

    # Fibonacci (These are also calculated differently, using sample for now)
    # If calculate_indicators adds Fib levels, map them here.

    # Clean up NaN values, replacing them with None so generate_html_report uses defaults
    cleaned_report_data = {k: (v if not pd.isna(v) else None) for k, v in report_data.items()}

    return cleaned_report_data


def run_test(symbol, report_date):
    """Runs the chart and report generation test for a specific symbol and date."""
    print(f"--- Starting test for {symbol} on {report_date} ---")

    data_file = os.path.join(project_root, 'Data', f'{symbol}_{report_date}.csv')
    charts_dir = os.path.join(project_root, 'Charts')
    reports_dir = os.path.join(project_root, 'Reports')

    # 1. Load data
    df_loaded_data = None
    try:
        df_loaded_data = pd.read_csv(data_file, index_col='Date', parse_dates=True)
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df_loaded_data.columns for col in required_cols):
             print(f"Warning: Data file {data_file} missing one or more required columns: {required_cols}. Trying with Close only.")
             if 'Close' not in df_loaded_data.columns:
                 raise ValueError("Data file must contain at least a 'Close' column.")
        print(f"[Step 1/4] Data loaded successfully from {os.path.basename(data_file)}")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_file}")
        return None
    except Exception as e:
        print(f"Error loading data from {data_file}: {e}")
        traceback.print_exc()
        return None

    # 2. Generate interactive charts and get indicator DataFrame
    df_indicators = None
    try:
        print(f"[Step 2/4] Generating interactive charts and calculating indicators for {symbol}...")
        # Test the 'default' parameter set
        chart_files, df_indicators = generate_parameter_set_charts(symbol, df_loaded_data, charts_dir, parameter_sets=['default'])
        print(f"Generated chart files info: {chart_files}")
        if df_indicators is None or df_indicators.empty:
            print("Warning: Indicator DataFrame was not returned or is empty.")
        else:
            print("Indicator DataFrame generated successfully.")
        if not chart_files or not any(chart_files.values()):
             print("Warning: No chart files seem to have been generated.")

    except Exception as e:
        print(f"Error during chart generation/indicator calculation: {e}")
        traceback.print_exc()
        # Continue, report might use sample data

    # 3. Prepare data dictionary for the report
    report_data_dict = None
    try:
        print(f"[Step 3/4] Preparing data dictionary for HTML report...")
        report_data_dict = map_df_to_report_data(df_indicators)

        # Calculate and add 'previous_close' if possible
        if df_loaded_data is not None and len(df_loaded_data) > 1:
             # Assuming the second to last row has the previous close
             prev_close = df_loaded_data['Close'].iloc[-2]
             if not pd.isna(prev_close):
                 report_data_dict['previous_close'] = prev_close
                 print(f"Calculated previous_close: {prev_close}")
             else:
                 print("Warning: Previous day's close is NaN.")
        else:
             print("Warning: Not enough data to calculate previous_close.")

        if report_data_dict:
            print("Data dictionary prepared successfully.")
        else:
            print("Failed to prepare data dictionary, report will use sample data.")

    except Exception as e:
        print(f"Error preparing data dictionary: {e}")
        traceback.print_exc()
        # Continue, report will use sample data

    # 4. Generate HTML report using the prepared data
    try:
        print(f"[Step 4/4] Generating HTML report for {symbol}...")
        # Pass the prepared dictionary (or None if failed) to generate_html_report
        report_path = generate_html_report(symbol, report_date, data=report_data_dict, output_dir=reports_dir)
        print(f"HTML report generated: {report_path}")
        print(f"--- Test finished for {symbol} on {report_date} ---")
        return report_path
    except Exception as e:
        print(f"Error during HTML report generation: {e}")
        traceback.print_exc()
        print(f"--- Test failed for {symbol} on {report_date} ---")
        return None

if __name__ == "__main__":
    # Define the symbol and date to test
    test_symbol = 'EURUSD'
    test_date = '20250501' # Use the latest available date

    # Check if data file exists before running
    data_file_path = os.path.join(project_root, 'Data', f'{test_symbol}_{test_date}.csv')
    if not os.path.exists(data_file_path):
        print(f"Test data file not found: {data_file_path}")
        print("Please ensure the data file exists or choose a different symbol/date.")
    else:
        run_test(test_symbol, test_date)
