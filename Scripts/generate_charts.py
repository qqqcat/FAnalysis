#!/usr/bin/env python
"""
Chart Generation Module for Financial Analysis
----------------------------------------------
This module generates various chart types for financial data including:
- Static charts with matplotlib
- Interactive charts with plotly
- Parameter set optimized charts for different trading strategies
"""

import os
import pandas as pd
import numpy as np
import matplotlib
# Set the backend to a non-interactive backend before importing pyplot
# This fixes the "main thread is not in main loop" error in web threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Importing indicator calculation functions
from calculate_indicators import calculate_indicators

# Chart configuration constants
CHART_CONFIG = {
    "default": {
        "moving_averages": ["SMA20", "SMA50", "SMA200"],
        "oscillators": ["RSI", "MACD"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Default Analysis"
    },
    "short_term": {
        "moving_averages": ["SMA9", "SMA21", "EMA12", "EMA26"],
        "oscillators": ["RSI7", "MACD_HF"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Short-Term Trading"
    },
    "medium_term": {
        "moving_averages": ["SMA50", "SMA200", "EMA50", "EMA200"],
        "oscillators": ["RSI", "MACD"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Medium-Term Trading"
    },
    "trend_following": {
        "moving_averages": ["SMA50", "SMA200", "EMA12", "EMA26"],
        "oscillators": ["ADX", "MACD"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Trend Following"
    },
    "momentum": {
        "moving_averages": ["SMA20", "SMA50"],
        "oscillators": ["RSI", "MACD", "STOCH_K", "STOCH_D"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Momentum Strategy"
    },
    "volatility": {
        "moving_averages": ["SMA20"],
        "oscillators": ["RSI"],
        "bands": ["BB_High", "BB_Mid", "BB_Low"],
        "title": "Volatility Strategy"
    },
    "tight_channel": {
        "moving_averages": ["SMA20"],
        "oscillators": ["RSI"],
        "bands": ["BB_Tight_High", "BB_Tight_Mid", "BB_Tight_Low"],
        "title": "Tight Channel Trading"
    },
    "wide_channel": {
        "moving_averages": ["SMA20"], 
        "oscillators": ["RSI"],
        "bands": ["BB_Wide_High", "BB_Wide_Mid", "BB_Wide_Low"],
        "title": "Wide Channel Trading"
    },
    "ichimoku": {
        "moving_averages": [],
        "oscillators": ["RSI"],
        "bands": [],
        "ichimoku_components": ["Ichimoku_Tenkan", "Ichimoku_Kijun", "Ichimoku_SpanA", "Ichimoku_SpanB", "Ichimoku_Chikou"],
        "secondary_indicators": ["SAR", "OBV", "OBV_MA"],
        "title": "Ichimoku Cloud Analysis"
    }
}

# Chart style configuration
CHART_STYLES = {
    "colors": {
        "price": "black",
        "sma": "blue",
        "ema": "purple",
        "rsi": "purple",
        "macd": "blue",
        "signal": "red",
        "histogram_positive": "green",
        "histogram_negative": "red",
        "bb_upper": "blue",
        "bb_mid": "blue",
        "bb_lower": "blue",
        "stoch_k": "green",
        "stoch_d": "red",
        "adx": "orange",
        "ichimoku_tenkan": "red",
        "ichimoku_kijun": "blue",
        "ichimoku_spana": "green",
        "ichimoku_spanb": "red",
        "ichimoku_chikou": "purple",
        "sar": "blue",
        "obv": "purple",
        "obv_ma": "orange"
    },
    "line_styles": {
        "solid": "-",
        "dashed": "--",
        "dotted": ":"
    },
    "alpha": {
        "fill": 0.1,
        "line": 0.7,
        "histogram": 0.5
    },
    "thresholds": {
        "rsi_upper": 70,
        "rsi_lower": 30,
        "stoch_upper": 80,
        "stoch_lower": 20,
        "adx_strong": 25,
        "adx_moderate": 20
    }
}

def generate_parameter_set_charts(symbol, data, output_dir, parameter_sets=None, chart_date=None):
    """
    Generate charts for multiple parameter sets
    
    Args:
        symbol (str): Symbol being analyzed
        data (pandas.DataFrame): Raw price data
        output_dir (str): Directory to save the charts
        parameter_sets (list): List of parameter sets to generate charts for
        chart_date (str): Date in YYYYMMDD format for the chart filenames
        
    Returns:
        dict: Dictionary with chart file paths grouped by parameter set
        dict: Dictionary with processed indicator data for each parameter set
    """
    if parameter_sets is None:
        parameter_sets = ['default']
    
    # Format the date for the filename
    if chart_date is None:
        chart_date = datetime.now().strftime("%Y%m%d")
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store chart file paths and processed data
    chart_files = {}
    indicator_data = {}
    
    # Generate charts for each parameter set
    for param_set in parameter_sets:
        # Calculate indicators for this parameter set
        with_indicators = calculate_indicators(data, parameter_set=param_set)
        
        # Store the processed data
        indicator_data[param_set] = with_indicators
        
        # Plot and save static charts
        static_charts = plot_indicators(with_indicators, symbol, output_dir, chart_date, param_set)
        chart_files[param_set] = static_charts
        
        # Generate interactive charts if it's the default parameter set
        if param_set == 'default':
            # Create interactive indicator chart
            interactive_indicator_path = plot_interactive_indicators(
                with_indicators, symbol, output_dir, chart_date
            )
            if interactive_indicator_path:
                if 'interactive' not in chart_files:
                    chart_files['interactive'] = []
                chart_files['interactive'].append(interactive_indicator_path)
            
            # Create interactive Bollinger Bands chart
            interactive_bb_path = plot_interactive_bollinger(
                with_indicators, symbol, output_dir, chart_date
            )
            if interactive_bb_path:
                if 'interactive' not in chart_files:
                    chart_files['interactive'] = []
                chart_files['interactive'].append(interactive_bb_path)
    
    return chart_files, indicator_data

def plot_indicators(data, symbol, output_dir, chart_date=None, strategy="default"):
    """
    Generate plots of key indicators.
    
    Args:
        data (pandas.DataFrame): Data with indicators
        symbol (str): Symbol being analyzed
        output_dir (str): Directory to save the charts
        chart_date (str): Date in YYYYMMDD format for the chart filename
        strategy (str): Trading strategy parameter set
        
    Returns:
        list: Paths to the generated chart files
    """
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format the date for the filename
    if chart_date is None:
        chart_date = datetime.now().strftime("%Y%m%d")
        
    chart_files = []
    
    try:
        # Get configuration for this strategy
        config = CHART_CONFIG.get(strategy, CHART_CONFIG["default"])
        styles = CHART_STYLES
        
        # Generate primary indicator chart
        indicator_chart_path = generate_indicator_chart(
            data, symbol, output_dir, chart_date, strategy, config, styles
        )
        if indicator_chart_path:
            chart_files.append(indicator_chart_path)
        
        # Generate Bollinger Bands chart
        bollinger_chart_path = generate_bollinger_chart(
            data, symbol, output_dir, chart_date, strategy, config, styles
        )
        if bollinger_chart_path:
            chart_files.append(bollinger_chart_path)
        
        # Generate Ichimoku chart if applicable
        if strategy == "ichimoku" and has_ichimoku_data(data):
            ichimoku_chart_path = generate_ichimoku_chart(
                data, symbol, output_dir, chart_date, styles
            )
            if ichimoku_chart_path:
                chart_files.append(ichimoku_chart_path)
        
        # Generate strategy-specific combination charts
        if strategy in ["trend_following", "momentum", "volatility"]:
            strategy_chart_path = generate_strategy_chart(
                data, symbol, output_dir, chart_date, strategy, styles
            )
            if strategy_chart_path:
                chart_files.append(strategy_chart_path)
        
    except Exception as e:
        print(f"Error generating charts: {str(e)}")
        import traceback
        traceback.print_exc()
        # Create a simple error chart as a fallback
        try:
            fallback_path = generate_fallback_chart(
                data, symbol, output_dir, chart_date
            )
            if fallback_path:
                chart_files.append(fallback_path)
        except Exception as fallback_error:
            print(f"Failed to create even fallback chart: {str(fallback_error)}")
    
    finally:
        plt.close('all')  # Close all figures to free memory
    
    print(f"Charts saved to {output_dir}")
    return chart_files

def generate_indicator_chart(data, symbol, output_dir, chart_date, strategy, config, styles):
    """Helper function to generate the main indicator chart with price, MAs, RSI/ADX, and MACD/Stoch"""
    plt.figure(figsize=(12, 8))
    
    # Price with Moving Averages plot
    plt.subplot(3, 1, 1)
    plt.plot(data.index, data['Close'], label='Close Price', color=styles["colors"]["price"])
    
    # Plot moving averages based on strategy configuration
    for ma in config.get("moving_averages", []):
        if ma in data.columns:
            color = styles["colors"]["sma"] if ma.startswith("SMA") else styles["colors"]["ema"]
            plt.plot(data.index, data[ma], label=ma, color=color)
    
    plt.title(f'{symbol} Price with Moving Averages - {config.get("title", "")}')
    plt.legend()
    plt.grid(True)
    
    # Second plot: RSI or ADX based on configuration
    plt.subplot(3, 1, 2)
    oscillators = config.get("oscillators", [])
    
    if "ADX" in oscillators and "ADX" in data.columns:
        plt.plot(data.index, data['ADX'], label='ADX(14)', color=styles["colors"]["adx"])
        plt.axhline(y=styles["thresholds"]["adx_strong"], color='r', linestyle='--', alpha=0.7, label='Strong Trend')
        plt.axhline(y=styles["thresholds"]["adx_moderate"], color='y', linestyle='--', alpha=0.7, label='Moderate Trend')
        plt.title('ADX - Trend Strength')
    elif "RSI7" in oscillators and "RSI7" in data.columns:
        plt.plot(data.index, data['RSI7'], label='RSI(7)', color=styles["colors"]["rsi"])
        plt.axhline(y=styles["thresholds"]["rsi_upper"], color='r', linestyle='--', alpha=0.7)
        plt.axhline(y=styles["thresholds"]["rsi_lower"], color='g', linestyle='--', alpha=0.7)
        plt.title('RSI(7)')
    else:
        rsi_col = [col for col in data.columns if col.startswith('RSI') and col != 'RSI7']
        if rsi_col and rsi_col[0] in data.columns:
            plt.plot(data.index, data[rsi_col[0]], label=rsi_col[0], color=styles["colors"]["rsi"])
            plt.axhline(y=styles["thresholds"]["rsi_upper"], color='r', linestyle='--', alpha=0.7)
            plt.axhline(y=styles["thresholds"]["rsi_lower"], color='g', linestyle='--', alpha=0.7)
            plt.title(f'{rsi_col[0]}')
    
    plt.legend()
    plt.grid(True)
    
    # Third plot: MACD or Stochastic
    plt.subplot(3, 1, 3)
    
    if "STOCH_K" in oscillators and "STOCH_D" in oscillators and all(col in data.columns for col in ['STOCH_K', 'STOCH_D']):
        plt.plot(data.index, data['STOCH_K'], label='%K', color=styles["colors"]["stoch_k"])
        plt.plot(data.index, data['STOCH_D'], label='%D', color=styles["colors"]["stoch_d"])
        plt.axhline(y=styles["thresholds"]["stoch_upper"], color='r', linestyle='--', alpha=0.7)
        plt.axhline(y=styles["thresholds"]["stoch_lower"], color='g', linestyle='--', alpha=0.7)
        plt.title('Stochastic Oscillator')
    elif "MACD_HF" in oscillators and all(col in data.columns for col in ['MACD_HF', 'MACD_HF_Signal', 'MACD_HF_Histogram']):
        plt.plot(data.index, data['MACD_HF'], label='MACD(5,35,5)', color=styles["colors"]["macd"])
        plt.plot(data.index, data['MACD_HF_Signal'], label='Signal', color=styles["colors"]["signal"])
        plt.bar(data.index, data['MACD_HF_Histogram'], color='gray', alpha=styles["alpha"]["histogram"], label='Histogram')
        plt.title('High-Frequency MACD')
    else:
        if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            plt.plot(data.index, data['MACD'], label='MACD(12,26,9)', color=styles["colors"]["macd"])
            plt.plot(data.index, data['MACD_Signal'], label='Signal', color=styles["colors"]["signal"])
            
            # Color-coded histogram
            colors = [styles["colors"]["histogram_positive"] if val > 0 else styles["colors"]["histogram_negative"] 
                     for val in data['MACD_Histogram']]
            plt.bar(data.index, data['MACD_Histogram'], color=colors, alpha=styles["alpha"]["histogram"], label='Histogram')
            plt.title('MACD')
    
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    
    # Save the chart
    chart_filename = f"{symbol}_indicators_{chart_date}.png"
    chart_path = os.path.join(output_dir, chart_filename)
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path

def generate_bollinger_chart(data, symbol, output_dir, chart_date, strategy, config, styles):
    """Helper function to generate the Bollinger Bands chart"""
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Close Price', color=styles["colors"]["price"])
    
    bands = config.get("bands", [])
    
    # High, Mid, Low band column names based on strategy
    high_band = next((band for band in bands if "High" in band), "BB_High")
    mid_band = next((band for band in bands if "Mid" in band), "BB_Mid")
    low_band = next((band for band in bands if "Low" in band), "BB_Low")
    
    if all(band in data.columns for band in [high_band, mid_band, low_band]):
        plt.plot(data.index, data[high_band], label=high_band, color=styles["colors"]["bb_upper"])
        plt.plot(data.index, data[mid_band], label=mid_band, color=styles["colors"]["bb_mid"], linestyle='--')
        plt.plot(data.index, data[low_band], label=low_band, color=styles["colors"]["bb_lower"])
        plt.fill_between(data.index, data[high_band], data[low_band], alpha=styles["alpha"]["fill"])
        
        if "tight" in strategy:
            plt.title(f'{symbol} Tight Channel Bollinger Bands (14, 1.5σ)')
        elif "wide" in strategy:
            plt.title(f'{symbol} Wide Channel Bollinger Bands (30, 2.5σ)')
        else:
            plt.title(f'{symbol} Bollinger Bands (20, 2σ)')
    
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the chart
    chart_filename = f"{symbol}_bollinger_{chart_date}.png"
    chart_path = os.path.join(output_dir, chart_filename)
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path

def has_ichimoku_data(data):
    """Check if data contains Ichimoku cloud components"""
    required_columns = ['Ichimoku_SpanA', 'Ichimoku_SpanB']
    return all(col in data.columns for col in required_columns)

def generate_ichimoku_chart(data, symbol, output_dir, chart_date, styles):
    """Helper function to generate the Ichimoku Cloud chart"""
    try:
        plt.figure(figsize=(12, 8))
        
        # Create a DataFrame with only the columns we need, ensuring they share the same index
        ichimoku_columns = ['Close', 'Ichimoku_Tenkan', 'Ichimoku_Kijun', 'Ichimoku_SpanA', 'Ichimoku_SpanB']
        valid_columns = [col for col in ichimoku_columns if col in data.columns]
        
        # Create a temporary dataframe with valid columns and drop any rows with NaN values
        ichimoku_data = pd.DataFrame({col: data[col] for col in valid_columns})
        ichimoku_data = ichimoku_data.dropna(subset=['Ichimoku_SpanA', 'Ichimoku_SpanB'])
        
        if len(ichimoku_data) > 0:
            # Subplot 1: Price with Ichimoku Cloud
            plt.subplot(2, 1, 1)
            
            # Pre-compute comparison mask for fill_between
            comparison_mask = ichimoku_data['Ichimoku_SpanA'] >= ichimoku_data['Ichimoku_SpanB']
            
            # Fill green area (SpanA >= SpanB)
            plt.fill_between(
                ichimoku_data.index, 
                ichimoku_data['Ichimoku_SpanA'].values, 
                ichimoku_data['Ichimoku_SpanB'].values, 
                where=comparison_mask.values,
                color='lightgreen', alpha=0.3
            )
            
            # Fill red area (SpanA < SpanB)
            plt.fill_between(
                ichimoku_data.index, 
                ichimoku_data['Ichimoku_SpanA'].values, 
                ichimoku_data['Ichimoku_SpanB'].values, 
                where=~comparison_mask.values,
                color='lightcoral', alpha=0.3
            )
            
            # Plot price and Ichimoku components
            plt.plot(ichimoku_data.index, ichimoku_data['Close'], 
                    label='Close', color=styles["colors"]["price"])
            plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_Tenkan'], 
                    label='Tenkan-sen (9)', color=styles["colors"]["ichimoku_tenkan"])
            plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_Kijun'], 
                    label='Kijun-sen (26)', color=styles["colors"]["ichimoku_kijun"])
            plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_SpanA'], 
                    label='Span A', color=styles["colors"]["ichimoku_spana"])
            plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_SpanB'], 
                    label='Span B', color=styles["colors"]["ichimoku_spanb"], alpha=0.5)
            
            # Plot Chikou Span if available
            if 'Ichimoku_Chikou' in data.columns:
                chikou_data = pd.DataFrame({'Ichimoku_Chikou': data['Ichimoku_Chikou']})
                chikou_valid = chikou_data.dropna()
                if len(chikou_valid) > 0:
                    plt.plot(chikou_valid.index, chikou_valid['Ichimoku_Chikou'], 
                            label='Chikou Span', color=styles["colors"]["ichimoku_chikou"])
            
            plt.title(f'{symbol} Ichimoku Cloud')
            plt.legend()
            plt.grid(True)
            
            # Subplot 2: SAR and OBV
            plt.subplot(2, 1, 2)
            
            # Create a dataframe for SAR and OBV plotting
            plot_data = data[['Close']].copy()
            secondary_indicators = ["SAR", "OBV", "OBV_MA"]
            for indicator in secondary_indicators:
                if indicator in data.columns:
                    plot_data[indicator] = data[indicator]
            
            plot_data = plot_data.dropna()
            
            # Twin axes for price and OBV
            ax1 = plt.gca()
            ax2 = ax1.twinx()
            
            # Plot price and SAR on primary axis
            ax1.plot(plot_data.index, plot_data['Close'], label='Close', color=styles["colors"]["price"], alpha=0.5)
            if 'SAR' in plot_data.columns:
                ax1.scatter(plot_data.index, plot_data['SAR'], label='SAR', marker='.', color=styles["colors"]["sar"], s=15)
            
            # Plot OBV and OBV MA on secondary axis
            if 'OBV' in plot_data.columns:
                ax2.plot(plot_data.index, plot_data['OBV'], label='OBV', color=styles["colors"]["obv"], alpha=0.7)
            if 'OBV_MA' in plot_data.columns:
                ax2.plot(plot_data.index, plot_data['OBV_MA'], label='OBV MA(20)', color=styles["colors"]["obv_ma"])
            
            # Set labels and legend
            ax1.set_ylabel('Price', color='black')
            ax2.set_ylabel('OBV', color=styles["colors"]["obv"])
            
            # Add legends for both axes
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.title(f'{symbol} Parabolic SAR and On-Balance Volume')
            ax1.grid(True)
            
            plt.tight_layout()
            
            # Save the Ichimoku chart
            chart_filename = f"{symbol}_ichimoku_{chart_date}.png"
            chart_path = os.path.join(output_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            return chart_path
        else:
            print("No valid Ichimoku data available after filtering NaN values")
            return None
    
    except Exception as e:
        print(f"Error creating Ichimoku chart: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_strategy_chart(data, symbol, output_dir, chart_date, strategy, styles):
    """Helper function to generate strategy-specific combination charts"""
    plt.figure(figsize=(12, 8))
    
    if strategy == "trend_following":
        # Trend Following Combo: SMA(50,200) + EMA(12,26) + ADX(14)
        plt.subplot(3, 1, 1)
        plt.plot(data.index, data['Close'], label='Close', color=styles["colors"]["price"])
        plt.plot(data.index, data['SMA50'], label='SMA50', color='blue')
        plt.plot(data.index, data['SMA200'], label='SMA200', color='red')
        plt.title(f'{symbol} - SMA50/200 Golden/Death Cross')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(data.index, data['Close'], label='Close', color=styles["colors"]["price"])
        plt.plot(data.index, data['EMA12'], label='EMA12', color='green')
        plt.plot(data.index, data['EMA26'], label='EMA26', color='purple')
        plt.title(f'{symbol} - EMA12/26 Crossover')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(data.index, data['ADX'], label='ADX(14)', color=styles["colors"]["adx"])
        plt.axhline(y=styles["thresholds"]["adx_strong"], color='r', linestyle='--', alpha=0.7, label='Strong Trend')
        plt.axhline(y=styles["thresholds"]["adx_moderate"], color='y', linestyle='--', alpha=0.7, label='Moderate Trend')
        plt.title(f'{symbol} - ADX Trend Strength')
        plt.legend()
        plt.grid(True)
        
        chart_filename = f"{symbol}_trend_strategy_{chart_date}.png"
        
    elif strategy == "momentum":
        # Momentum Validation Combo: RSI(14) + MACD(12,26,9) + Stochastic(14,3)
        plt.subplot(3, 1, 1)
        plt.plot(data.index, data['RSI'], label='RSI(14)', color=styles["colors"]["rsi"])
        plt.axhline(y=styles["thresholds"]["rsi_upper"], color='r', linestyle='--', alpha=0.7, label='Overbought')
        plt.axhline(y=styles["thresholds"]["rsi_lower"], color='g', linestyle='--', alpha=0.7, label='Oversold')
        plt.title(f'{symbol} - RSI(14)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(data.index, data['MACD'], label='MACD', color=styles["colors"]["macd"])
        plt.plot(data.index, data['MACD_Signal'], label='Signal', color=styles["colors"]["signal"])
        plt.bar(data.index, data['MACD_Histogram'], color='gray', alpha=styles["alpha"]["histogram"], label='Histogram')
        plt.title(f'{symbol} - MACD(12,26,9)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(data.index, data['STOCH_K'], label='%K', color=styles["colors"]["stoch_k"])
        plt.plot(data.index, data['STOCH_D'], label='%D', color=styles["colors"]["stoch_d"])
        plt.axhline(y=styles["thresholds"]["stoch_upper"], color='r', linestyle='--', alpha=0.7, label='Overbought')
        plt.axhline(y=styles["thresholds"]["stoch_lower"], color='g', linestyle='--', alpha=0.7, label='Oversold')
        plt.title(f'{symbol} - Stochastic(14,3)')
        plt.legend()
        plt.grid(True)
        
        chart_filename = f"{symbol}_momentum_strategy_{chart_date}.png"
        
    elif strategy == "volatility":
        # Volatility Trading Combo: Bollinger Bands
        plt.subplot(3, 1, 1)
        plt.plot(data.index, data['Close'], label='Close', color=styles["colors"]["price"])
        plt.plot(data.index, data['BB_High'], label='BB Upper', color=styles["colors"]["bb_upper"])
        plt.plot(data.index, data['BB_Mid'], label='BB Middle', color=styles["colors"]["bb_mid"], linestyle='--')
        plt.plot(data.index, data['BB_Low'], label='BB Lower', color=styles["colors"]["bb_lower"])
        plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=styles["alpha"]["fill"], color='blue')
        plt.title(f'{symbol} - Bollinger Bands(20,2)')
        plt.legend()
        plt.grid(True)
        
        # Add additional volatility indicators if available
        if 'ATR' in data.columns:
            plt.subplot(3, 1, 2)
            plt.plot(data.index, data['ATR'], label='ATR(14)', color='purple')
            plt.title(f'{symbol} - Average True Range')
            plt.legend()
            plt.grid(True)
            
            # Add normalized ATR as percentage of price
            if 'ATR_Percent' in data.columns:
                plt.subplot(3, 1, 3)
                plt.plot(data.index, data['ATR_Percent'], label='ATR%', color='green')
                plt.title(f'{symbol} - ATR as % of Price')
                plt.legend()
                plt.grid(True)
        
        chart_filename = f"{symbol}_volatility_strategy_{chart_date}.png"
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, chart_filename)
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def generate_fallback_chart(data, symbol, output_dir, chart_date):
    """Generate a simple price chart as fallback when full chart generation fails"""
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], 'b-', label='Price')
    plt.title(f"{symbol} Price Chart (Fallback Chart)")
    plt.grid(True)
    plt.legend()
    
    # Save the fallback chart
    fallback_filename = f"{symbol}_basic_{chart_date}.png"
    fallback_path = os.path.join(output_dir, fallback_filename)
    plt.savefig(fallback_path)
    plt.close()
    print(f"Created fallback chart: {fallback_path}")
    return fallback_path

def plot_interactive_indicators(data, symbol, output_dir, chart_date=None):
    """
    Generate an interactive plotly chart with key indicators
    
    Args:
        data (pandas.DataFrame): Data with indicators
        symbol (str): Symbol being analyzed
        output_dir (str): Directory to save the html file
        chart_date (str): Date in YYYYMMDD format for the chart filename
    
    Returns:
        str: Path to the generated html file or None if error
    """
    # Format the date for the filename
    if chart_date is None:
        chart_date = datetime.now().strftime("%Y%m%d")
    
    try:
        # Create subplot
        fig = make_subplots(rows=3, cols=1, 
                         shared_xaxes=True,
                         vertical_spacing=0.05,
                         row_heights=[0.5, 0.25, 0.25],
                         subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'))
        
        # Add price and moving averages to row 1
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price', line=dict(color=CHART_STYLES["colors"]["price"])), row=1, col=1)
        
        # Add moving averages
        for ma in ['SMA20', 'SMA50', 'SMA200']:
            if ma in data.columns:
                fig.add_trace(go.Scatter(x=data.index, y=data[ma], name=ma, line=dict(color=CHART_STYLES["colors"]["sma"])), row=1, col=1)
        
        # Add RSI to row 2
        if 'RSI' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color=CHART_STYLES["colors"]["rsi"])), row=2, col=1)
            
            # Add RSI overbought/oversold lines
            fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=70, y1=70,
                       line=dict(color="red", width=2, dash="dash"), row=2, col=1)
            fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=30, y1=30,
                       line=dict(color="green", width=2, dash="dash"), row=2, col=1)
        
        # Add MACD to row 3
        if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color=CHART_STYLES["colors"]["macd"])), row=3, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD_Signal'], name='Signal', line=dict(color=CHART_STYLES["colors"]["signal"])), row=3, col=1)
            
            # Create MACD histogram with custom colors
            try:
                # Safely get MACD histogram values and handle potential 2D arrays
                macd_hist_vals = data['MACD_Histogram']
                if hasattr(macd_hist_vals, 'values'):
                    macd_hist_vals = macd_hist_vals.values
                
                # Ensure it's a flat 1D array
                macd_hist_vals = np.asarray(macd_hist_vals).flatten()
                
                # Create custom colors
                colors = [CHART_STYLES["colors"]["histogram_positive"] if val > 0 else CHART_STYLES["colors"]["histogram_negative"] for val in macd_hist_vals]
                
                fig.add_trace(go.Bar(
                    x=data.index, 
                    y=macd_hist_vals,
                    name='Histogram', 
                    marker=dict(color=colors, opacity=CHART_STYLES["alpha"]["histogram"])
                ), row=3, col=1)
            except Exception as hist_error:
                print(f"Error plotting MACD histogram: {hist_error}")
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Technical Indicators',
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        # Add time range selector
        fig.update_xaxes(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            row=1, col=1
        )
        
        # Add Y axis labels
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        # Save interactive chart
        filepath = os.path.join(output_dir, f"{symbol}_interactive_indicators_{chart_date}.html")
        fig.write_html(filepath)
        print(f"Interactive indicators chart saved to {filepath}")
        
        return filepath
    
    except Exception as e:
        print(f"Error creating interactive indicators chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def plot_interactive_bollinger(data, symbol, output_dir, chart_date=None):
    """
    Generate an interactive plotly chart with Bollinger Bands
    
    Args:
        data (pandas.DataFrame): Data with indicators
        symbol (str): Symbol being analyzed  
        output_dir (str): Directory to save the html file
        chart_date (str): Date in YYYYMMDD format for the chart filename
    
    Returns:
        str: Path to the generated html file or None if error
    """
    # Format the date for the filename
    if chart_date is None:
        chart_date = datetime.now().strftime("%Y%m%d")
    
    try:
        # Create figure
        fig = go.Figure()
        
        # Add price
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Close'], 
            name='Price',
            line=dict(color=CHART_STYLES["colors"]["price"])
        ))
        
        # Add Bollinger Bands
        if 'BB_High' in data.columns:
            # Ensure data is one-dimensional
            bb_high_values = np.asarray(data['BB_High']).flatten()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_high_values, 
                name='Upper Band',
                line=dict(color=CHART_STYLES["colors"]["bb_upper"], width=1)
            ))
        
        if 'BB_Mid' in data.columns:
            # Ensure data is one-dimensional
            bb_mid_values = np.asarray(data['BB_Mid']).flatten()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_mid_values, 
                name='Middle Band',
                line=dict(color=CHART_STYLES["colors"]["bb_mid"], width=1, dash='dash')
            ))
        
        if 'BB_Low' in data.columns:
            # Ensure data is one-dimensional
            bb_low_values = np.asarray(data['BB_Low']).flatten()
            # Add Bollinger Lower Band with fill area
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_low_values, 
                name='Lower Band',
                line=dict(color=CHART_STYLES["colors"]["bb_lower"], width=1),
                fill='tonexty',  # Fill to previous trace
                fillcolor=f'rgba(0, 0, 255, {CHART_STYLES["alpha"]["fill"]})'
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Bollinger Bands',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        # Add time range selector
        fig.update_xaxes(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        # Save interactive chart
        filepath = os.path.join(output_dir, f"{symbol}_interactive_bollinger_{chart_date}.html")
        fig.write_html(filepath)
        print(f"Interactive Bollinger chart saved to {filepath}")
        
        return filepath
    
    except Exception as e:
        print(f"Error creating interactive Bollinger chart: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to create a simple price chart as fallback
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data['Close'], 
                name='Price',
                line=dict(color=CHART_STYLES["colors"]["price"])
            ))
            fig.update_layout(
                title=f'{symbol} Price (Fallback Chart)',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white'
            )
            filepath = os.path.join(output_dir, f"{symbol}_basic_price_{chart_date}.html")
            fig.write_html(filepath)
            print(f"Created fallback interactive chart: {filepath}")
            return filepath
        except Exception as fallback_error:
            print(f"Failed to create even fallback chart: {fallback_error}")
            return None

if __name__ == "__main__":
    print("This module provides chart generation functionality for the Financial Analysis Platform.")
    print("It should be imported and used by other scripts, not run directly.")
