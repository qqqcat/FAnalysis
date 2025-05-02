#!/usr/bin/env python
"""
Market Data Fetcher Script
--------------------------
This script fetches historical market data for stocks, indices, and forex pairs.
It uses the yfinance library to download data from Yahoo Finance.
"""

import os
import argparse
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def fetch_data(symbol, period='1d', interval='1d', start_date=None, end_date=None):
    """
    Fetch historical market data for a given symbol.
    
    Args:
        symbol (str): The ticker symbol
        period (str): The period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
                     OR a date in YYYYMMDD format
        interval (str): The data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
        
    Returns:
        pandas.DataFrame: Historical market data
    """
    try:
        # Check if 'period' is in YYYYMMDD format
        if period and len(period) == 8 and period.isdigit():
            try:
                # Convert YYYYMMDD to yyyy-mm-dd
                date_obj = datetime.strptime(period, "%Y%m%d")
                
                # Check if date is in the future
                if date_obj > datetime.now():
                    raise ValueError(f"Date {period} is in the future. Cannot fetch future data.")
                
                # Set the date range for the specified date (full day)
                end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
                # 修改为收集前半年(180天)的数据，而不是之前的30天
                start_date = (date_obj - timedelta(days=180)).strftime("%Y-%m-%d")
                print(f"Fetching data for {symbol} from {start_date} to {end_date}")
                period = None  # Don't use period if we're using start_date and end_date
            except ValueError as e:
                print(f"Date error: {str(e)}")
                return None
        
        # Transform the symbol based on the type of financial product
        original_symbol = symbol
        
        # Append '=X' to symbol if it's a forex pair without it
        if (symbol.upper().startswith('EUR') or 
            symbol.upper().startswith('GBP') or 
            symbol.upper().startswith('USD') or 
            symbol.upper().startswith('JPY') or 
            symbol.upper().startswith('AUD')) and len(symbol) == 6 and not symbol.endswith('=X'):
            symbol += '=X'
        
        # For commodities, add the correct suffix
        if symbol.upper() == 'GOLD' and not '=' in symbol:
            symbol = 'GC=F'  # Gold futures
        elif symbol.upper() == 'OIL' and not '=' in symbol:
            symbol = 'CL=F'  # Crude oil futures
        elif symbol.upper() == 'SILVER' and not '=' in symbol:
            symbol = 'SI=F'  # Silver futures
        elif symbol.upper() == 'WHEAT' and not '=' in symbol:
            symbol = 'ZW=F'  # Wheat futures
        elif symbol.upper() == 'CORN' and not '=' in symbol:
            symbol = 'ZC=F'  # Corn futures
        elif symbol.upper() == 'COTTON' and not '=' in symbol:
            symbol = 'CT=F'  # Cotton futures
        elif symbol.upper() == 'COFFEE' and not '=' in symbol:
            symbol = 'KC=F'  # Coffee futures
        # For indices, add the correct suffix
        elif symbol.upper() == 'S&P500' or symbol.upper() == 'SPX':
            symbol = '^GSPC'  # S&P 500 index
        elif symbol.upper() == 'NASDAQ':
            symbol = '^IXIC'  # NASDAQ Composite
        elif symbol.upper() == 'DOW':
            symbol = '^DJI'   # Dow Jones Industrial Average
        elif symbol.upper() == 'FTSE':
            symbol = '^FTSE'  # FTSE 100
        elif symbol.upper() == 'DAX':
            symbol = '^GDAXI' # DAX
            
        print(f"Using symbol {symbol} for {original_symbol}")
        ticker = yf.Ticker(symbol)
        
        # Try to get some basic info to check if the symbol exists
        try:
            info = ticker.info
            if not info or len(info) < 5:  # Basic check if we got valid info
                print(f"Warning: Limited information available for {symbol}, data may be incomplete")
        except Exception as ticker_error:
            print(f"Error retrieving ticker info: {str(ticker_error)}")
            # Continue anyway as some tickers work even with info retrieval failures
        
        # Fetch the historical data
        if start_date and end_date:
            data = ticker.history(start=start_date, end=end_date, interval=interval)
        else:
            data = ticker.history(period=period, interval=interval)
            
        if data.empty:
            print(f"No data found for {symbol}")
            return None
        
        # Basic data validation
        if len(data) < 2:
            print(f"Insufficient data points for {symbol}: only {len(data)} records found")
            return None
            
        # Save with the original symbol name to maintain consistency
        data.attrs['original_symbol'] = original_symbol
            
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def save_data(data, symbol, output_dir, file_format="csv", date_str=None):
    """
    Save the fetched data to a file.
    
    Args:
        data (pandas.DataFrame): The data to save
        symbol (str): The ticker symbol
        output_dir (str): Directory to save the file
        file_format (str): File format to save (csv or excel)
        date_str (str): Optional specific date to use in filename (YYYYMMDD)
    
    Returns:
        str: Path to the saved file
    """
    if data is None or data.empty:
        return None
        
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format the date for the filename
    if date_str and len(date_str) == 8 and date_str.isdigit():
        current_date = date_str
    else:
        current_date = datetime.now().strftime("%Y%m%d")
    
    # Remove '=X' or '=F' from the symbol for the filename
    clean_symbol = symbol.split('=')[0]
    
    # Create the filename
    filename = f"{clean_symbol}_{current_date}.{file_format}"
    filepath = os.path.join(output_dir, filename)
    
    # Save the file
    if file_format.lower() == "csv":
        data.to_csv(filepath)
    elif file_format.lower() in ["excel", "xlsx", "xls"]:
        data.to_excel(filepath)
    else:
        print(f"Unsupported file format: {file_format}")
        return None
        
    print(f"Data saved to {filepath}")
    return filepath

def main():
    """Main function to parse command line arguments and fetch data."""
    parser = argparse.ArgumentParser(description="Fetch historical market data")
    parser.add_argument("symbol", help="Ticker symbol (e.g., AAPL, EURUSD=X)")
    parser.add_argument("--period", default="1d", help="Period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max) or date in YYYYMMDD format")
    parser.add_argument("--interval", default="1d", help="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
    parser.add_argument("--start", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", help="End date in YYYY-MM-DD format")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--format", default="csv", choices=["csv", "excel"], help="Output file format")
    
    args = parser.parse_args()
    
    # Fetch the data
    data = fetch_data(args.symbol, args.period, args.interval, args.start, args.end)
    
    if data is not None:
        # Print a summary
        print(f"\nData for {args.symbol}:")
        print(f"Date Range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"Number of records: {len(data)}")
        print("\nSummary Statistics:")
        print(data.describe())
        
        # Set default output directory if not provided
        if args.output is None:
            # Get the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Set output directory to Data folder in parent directory
            output_dir = os.path.join(os.path.dirname(script_dir), "Data")
        else:
            output_dir = args.output
        
        # Save the data
        date_str = args.period if len(args.period) == 8 and args.period.isdigit() else None
        save_data(data, args.symbol, output_dir, args.format, date_str)

if __name__ == "__main__":
    main()