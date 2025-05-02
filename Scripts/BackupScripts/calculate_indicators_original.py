#!/usr/bin/env python
"""
Technical Analysis Indicators Calculator
---------------------------------------
This script calculates various technical indicators on market data.
It uses pandas-ta library for calculations.

Includes indicator combinations for different trading strategies:
- Trend Following: SMA, EMA, ADX
- Momentum Validation: RSI, MACD, Stochastic
- Volatility Trading: Bollinger Bands, ATR, Keltner Channels
- Multi-timeframe: Ichimoku Cloud, Parabolic SAR, OBV
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib
# Set the backend to a non-interactive backend before importing pyplot
# This fixes the "main thread is not in main loop" error in web threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas_ta as ta

# Check if we have pandas_ta installed
try:
    import pandas_ta as ta
except ImportError:
    print("pandas_ta not installed. Please install it using: pip install pandas-ta")
    sys.exit(1)


def load_data(file_path):
    """
    Load market data from a CSV or Excel file.
    
    Args:
        file_path (str): Path to the data file
        
    Returns:
        pandas.DataFrame: Market data
    """
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")
        
    # Convert Date column to datetime if it exists
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
    
    # Handle case when loading from yfinance CSV that already has DatetimeIndex
    if isinstance(data.index, pd.DatetimeIndex):
        pass
    
    return data


def calculate_indicators(df, parameter_set='default'):
    """
    Calculate various technical indicators
    
    Args:
        df (pandas.DataFrame): Price data with at least OHLC columns
        parameter_set (str): Parameter set to use
                            Options: 'default', 'short_term', 'medium_term', 
                                     'high_freq', 'tight_channel', 'wide_channel',
                                     'trend_following', 'momentum', 'volatility', 'ichimoku'
    Returns:
        pandas.DataFrame: DataFrame with technical indicators
    """
    # Make a copy of the dataframe to avoid modifying the original
    data = df.copy()
    
    # Ensure we have the required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in data.columns:
            if col == 'Volume':
                data[col] = 0  # Default volume if not available
            else:
                raise ValueError(f"Required column {col} not found in dataframe")
    
    # Moving Averages - Default parameters
    # SMA
    ma_windows = [5, 10, 20, 50, 100, 150]
    for window in ma_windows:
        data[f'SMA{window}'] = ta.sma(data['Close'], length=window)
    
    # EMA
    for window in ma_windows:
        data[f'EMA{window}'] = ta.ema(data['Close'], length=window)
    
    # Add short-term trading parameters
    if parameter_set in ['default', 'short_term']:
        # Short-term SMA and EMA
        data['SMA9'] = ta.sma(data['Close'], length=9)
        data['SMA21'] = ta.sma(data['Close'], length=21)
        data['EMA12'] = ta.ema(data['Close'], length=12)
        data['EMA26'] = ta.ema(data['Close'], length=26)
    
    # Add medium-term trend parameters
    if parameter_set in ['default', 'medium_term']:
        # Medium-term SMA and EMA (some already calculated in default)
        # SMA50 and EMA50 already calculated above
        data['SMA200'] = ta.sma(data['Close'], length=200)
        data['EMA200'] = ta.ema(data['Close'], length=200)
    
    # RSI - 14 period (default)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # Add high-frequency trading RSI(7)
    if parameter_set in ['default', 'high_freq']:
        data['RSI7'] = ta.rsi(data['Close'], length=7)
    
    # MACD - default parameters (12, 26, 9)
    macd = ta.macd(data['Close'], fast=12, slow=26, signal=9)
    data['MACD'] = macd['MACD_12_26_9']
    data['MACD_Signal'] = macd['MACDs_12_26_9']
    data['MACD_Histogram'] = macd['MACDh_12_26_9']
    
    # Add high-frequency MACD (5, 35, 5)
    if parameter_set in ['default', 'high_freq']:
        macd_hf = ta.macd(data['Close'], fast=5, slow=35, signal=5)
        data['MACD_HF'] = macd_hf['MACD_5_35_5']
        data['MACD_HF_Signal'] = macd_hf['MACDs_5_35_5']
        data['MACD_HF_Histogram'] = macd_hf['MACDh_5_35_5']
    
    # Bollinger Bands - default parameters (20, 2)
    bb = ta.bbands(data['Close'], length=20, std=2)
    data['BB_High'] = bb['BBU_20_2.0']
    data['BB_Mid'] = bb['BBM_20_2.0']
    data['BB_Low'] = bb['BBL_20_2.0']
    
    # Add tight channel Bollinger Bands (14, 1.5)
    if parameter_set in ['default', 'tight_channel', 'volatility']:
        bb_tight = ta.bbands(data['Close'], length=14, std=1.5)
        data['BB_Tight_High'] = bb_tight['BBU_14_1.5']
        data['BB_Tight_Mid'] = bb_tight['BBM_14_1.5']
        data['BB_Tight_Low'] = bb_tight['BBL_14_1.5']
    
    # Add wide channel Bollinger Bands (30, 2.5)
    if parameter_set in ['default', 'wide_channel']:
        bb_wide = ta.bbands(data['Close'], length=30, std=2.5)
        data['BB_Wide_High'] = bb_wide['BBU_30_2.5']
        data['BB_Wide_Mid'] = bb_wide['BBM_30_2.5']
        data['BB_Wide_Low'] = bb_wide['BBL_30_2.5']
    
    # Calculate ATR
    data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)
    
    # Calculate Parabolic SAR
    sar = ta.psar(data['High'], data['Low'], data['Close'], af=0.02, max_af=0.2)
    data['SAR'] = sar['PSARl_0.02_0.2']  # Using the long PSAR values
    
    # Calculate Stochastic Oscillator
    stoch = ta.stoch(data['High'], data['Low'], data['Close'], k=14, d=3, smooth_k=3)
    data['STOCH_K'] = stoch['STOCHk_14_3_3']
    data['STOCH_D'] = stoch['STOCHd_14_3_3']
    
    ###############################
    # New Indicators Start Here
    ###############################
    
    # ADX (Average Directional Index) - For trend strength
    adx = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    data['ADX'] = adx['ADX_14']
    
    # On-Balance Volume (OBV)
    data['OBV'] = ta.obv(data['Close'], data['Volume'])
    
    # Calculate Keltner Channels
    if parameter_set in ['default', 'volatility']:
        # Get the EMA20 as middle band (should already be calculated above)
        midline = data['EMA20']
        # Calculate the Keltner Channel bands
        atr = data['ATR']
        data['Keltner_High'] = midline + (2 * atr)
        data['Keltner_Mid'] = midline
        data['Keltner_Low'] = midline - (2 * atr)
    
    # Calculate Ichimoku Cloud components
    if parameter_set in ['default', 'ichimoku']:
        # Use pandas_ta's Ichimoku implementation
        ichimoku = ta.ichimoku(data['High'], data['Low'], data['Close'], 
                             tenkan=9, kijun=26, senkou=52)
        
        # Extract components with proper names
        data['Ichimoku_Tenkan'] = ichimoku['ITS_9']  # Conversion Line
        data['Ichimoku_Kijun'] = ichimoku['IKS_26']  # Base Line
        data['Ichimoku_SpanA'] = ichimoku['ISA_9']   # Leading Span A
        data['Ichimoku_SpanB'] = ichimoku['ISB_26']  # Leading Span B
        data['Ichimoku_Chikou'] = ichimoku['ICS_26'] # Lagging Span
    
    # Strategy-specific indicator combinations
    
    # STRATEGY 1: Trend Following Combination
    if parameter_set in ['default', 'trend_following']:
        # SMA(50,200) + EMA(12,26) + ADX(14)
        # Most of these are already calculated above
        # Add a signal column for golden cross / death cross detection
        data['SMA_Cross_Signal'] = np.where(data['SMA50'] > data['SMA200'], 1, -1)
        
        # Add a column for EMA crossover signal
        data['EMA_Cross_Signal'] = np.where(data['EMA12'] > data['EMA26'], 1, -1)
        
        # Add a trend strength classification based on ADX
        data['Trend_Strength'] = np.where(data['ADX'] > 25, 'Strong', 
                             np.where(data['ADX'] > 20, 'Moderate', 'Weak'))
    
    # STRATEGY 2: Momentum Validation Combination
    if parameter_set in ['default', 'momentum']:
        # RSI(14) + MACD(12,26,9) + Stochastic(14,3)
        # Already calculated above
        
        # Add RSI overbought/oversold signal
        data['RSI_Signal'] = np.where(data['RSI'] > 70, -1,  # Overbought
                         np.where(data['RSI'] < 30, 1, 0))   # Oversold
        
        # Add MACD signal (positive = bullish, negative = bearish)
        data['MACD_Cross_Signal'] = np.where(data['MACD'] > data['MACD_Signal'], 1, -1)
        
        # Add Stochastic signal
        data['Stoch_Signal'] = np.where((data['STOCH_K'] > data['STOCH_D']) & 
                                    (data['STOCH_K'] < 80), 1,  # Bullish
                                np.where((data['STOCH_K'] < data['STOCH_D']) & 
                                        (data['STOCH_D'] > 20), -1, 0))  # Bearish
        
        # Combined momentum signal (sum of the 3 signals)
        data['Momentum_Score'] = data['RSI_Signal'] + data['MACD_Cross_Signal'] + data['Stoch_Signal']
    
    # STRATEGY 3: Volatility Trading Combination
    if parameter_set in ['default', 'volatility']:
        # Bollinger Bands(20,2) + ATR(14) + Keltner Channels
        # Already calculated above
        
        # Calculate Bollinger Band Squeeze (when BBs are inside Keltner Channels)
        data['BB_Squeeze'] = np.where((data['BB_High'] < data['Keltner_High']) & 
                                   (data['BB_Low'] > data['Keltner_Low']), 1, 0)
        
        # Calculate Bollinger Band width for volatility measurement
        data['BB_Width'] = (data['BB_High'] - data['BB_Low']) / data['BB_Mid']
        
        # Normalized ATR (ATR divided by close price) for percentage volatility
        data['ATR_Percent'] = data['ATR'] / data['Close'] * 100
    
    # STRATEGY 4: Multi-timeframe Combination with Ichimoku
    if parameter_set in ['default', 'ichimoku']:
        # Ichimoku Cloud + Parabolic SAR + On-Balance Volume
        # Already calculated above
        
        # Ichimoku Cloud direction (Above cloud = bullish, Below cloud = bearish)
        data['Cloud_Direction'] = np.where(data['Close'] > data['Ichimoku_SpanA'], 1,
                                np.where(data['Close'] < data['Ichimoku_SpanB'], -1, 0))
        
        # Parabolic SAR trend direction
        data['SAR_Signal'] = np.where(data['Close'] > data['SAR'], 1, -1)
        
        # Calculate OBV Moving Average for trend confirmation
        data['OBV_MA'] = ta.sma(data['OBV'], length=20)
        data['OBV_Signal'] = np.where(data['OBV'] > data['OBV_MA'], 1, -1)
    
    return data


def generate_report(data, symbol, output_dir, report_date=None):
    """
    Generate a simple text report summarizing the indicators.
    
    Args:
        data (pandas.DataFrame): Data with indicators
        symbol (str): Symbol being analyzed
        output_dir (str): Directory to save the report
        report_date (str): Date in YYYYMMDD format for the report filename
        
    Returns:
        str: Path to the report file
    """
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the latest data point
    latest = data.iloc[-1]
    
    # Format the date for the filename
    if report_date:
        current_date = report_date
    else:
        current_date = pd.Timestamp.now().strftime("%Y%m%d")
    
    # Create the report filename
    filename = f"{symbol}_indicator_report_{current_date}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(f"Technical Indicator Report for {symbol}\n")
        f.write(f"Date: {current_date}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("PRICE DATA:\n")
        f.write(f"Last Close: {latest['Close']:.4f}\n")
        f.write(f"Previous Close: {data.iloc[-2]['Close']:.4f}\n")
        f.write(f"Change: {(latest['Close'] - data.iloc[-2]['Close']):.4f} ")
        f.write(f"({(latest['Close'] / data.iloc[-2]['Close'] - 1) * 100:.2f}%)\n\n")
        
        f.write("MOVING AVERAGES:\n")
        f.write(f"SMA5: {latest['SMA5']:.4f}\n")
        f.write(f"SMA10: {latest['SMA10']:.4f}\n")
        f.write(f"SMA20: {latest['SMA20']:.4f}\n")
        f.write(f"SMA50: {latest['SMA50']:.4f}\n")
        f.write(f"SMA100: {latest['SMA100']:.4f}\n")
        f.write(f"SMA150: {latest['SMA150']:.4f}\n\n")
        
        f.write(f"EMA5: {latest['EMA5']:.4f}\n")
        f.write(f"EMA10: {latest['EMA10']:.4f}\n")
        f.write(f"EMA20: {latest['EMA20']:.4f}\n")
        f.write(f"EMA50: {latest['EMA50']:.4f}\n")
        f.write(f"EMA100: {latest['EMA100']:.4f}\n")
        f.write(f"EMA150: {latest['EMA150']:.4f}\n\n")
        
        f.write("OSCILLATORS:\n")
        f.write(f"RSI(14): {latest['RSI']:.2f}\n")
        f.write(f"Stochastic %K: {latest['STOCH_K']:.2f}\n")
        f.write(f"Stochastic %D: {latest['STOCH_D']:.2f}\n")
        f.write(f"MACD: {latest['MACD']:.4f}\n")
        f.write(f"MACD Signal: {latest['MACD_Signal']:.4f}\n")
        f.write(f"MACD Histogram: {latest['MACD_Histogram']:.4f}\n\n")
        
        f.write("VOLATILITY:\n")
        f.write(f"Bollinger Upper: {latest['BB_High']:.4f}\n")
        f.write(f"Bollinger Middle: {latest['BB_Mid']:.4f}\n")
        f.write(f"Bollinger Lower: {latest['BB_Low']:.4f}\n")
        f.write(f"ATR(14): {latest['ATR']:.4f}\n")
        
        # Add Keltner Channels if they exist
        if 'Keltner_High' in latest:
            f.write(f"Keltner Channel Upper: {latest['Keltner_High']:.4f}\n")
            f.write(f"Keltner Channel Middle: {latest['Keltner_Mid']:.4f}\n")
            f.write(f"Keltner Channel Lower: {latest['Keltner_Low']:.4f}\n")
            
            # Add BB squeeze analysis
            if 'BB_Squeeze' in latest:
                f.write(f"Bollinger Band Squeeze: {'Yes' if latest['BB_Squeeze'] == 1 else 'No'}\n")
        
        f.write("\n")
        
        f.write("TREND INDICATORS:\n")
        f.write(f"Parabolic SAR: {latest['SAR']:.4f}\n")
        
        # Add ADX if it exists
        if 'ADX' in latest:
            f.write(f"ADX(14): {latest['ADX']:.2f}\n")
            if 'Trend_Strength' in latest:
                f.write(f"Trend Strength: {latest['Trend_Strength']}\n")
        
        # Add Ichimoku Cloud components if they exist
        if 'Ichimoku_Tenkan' in latest:
            f.write("\n")
            f.write("ICHIMOKU CLOUD:\n")
            f.write(f"Tenkan-sen (Conversion Line): {latest['Ichimoku_Tenkan']:.4f}\n")
            f.write(f"Kijun-sen (Base Line): {latest['Ichimoku_Kijun']:.4f}\n")
            f.write(f"Senkou Span A (Leading Span A): {latest['Ichimoku_SpanA']:.4f}\n")
            f.write(f"Senkou Span B (Leading Span B): {latest['Ichimoku_SpanB']:.4f}\n")
            
            # Add cloud direction analysis
            if 'Cloud_Direction' in latest:
                cloud_dir = "Bullish" if latest['Cloud_Direction'] == 1 else ("Bearish" if latest['Cloud_Direction'] == -1 else "Neutral")
                f.write(f"Cloud Direction: {cloud_dir}\n")
        
        # Add On-Balance Volume if it exists
        if 'OBV' in latest:
            f.write("\n")
            f.write("VOLUME INDICATORS:\n")
            f.write(f"On-Balance Volume: {latest['OBV']:.0f}\n")
            if 'OBV_MA' in latest:
                f.write(f"OBV 20-period MA: {latest['OBV_MA']:.0f}\n")
                obv_trend = "Bullish" if latest['OBV'] > latest['OBV_MA'] else "Bearish"
                f.write(f"OBV Trend: {obv_trend}\n")
        
        f.write("\n")
        f.write("STRATEGY ANALYSIS:\n")
        
        # Add Trend Following Strategy
        if 'SMA_Cross_Signal' in latest and 'EMA_Cross_Signal' in latest and 'ADX' in latest:
            f.write("TREND FOLLOWING STRATEGY:\n")
            sma_signal = "Bullish" if latest['SMA_Cross_Signal'] == 1 else "Bearish"
            ema_signal = "Bullish" if latest['EMA_Cross_Signal'] == 1 else "Bearish"
            
            f.write(f"SMA(50,200) Cross Signal: {sma_signal}\n")
            f.write(f"EMA(12,26) Cross Signal: {ema_signal}\n")
            f.write(f"ADX(14) Trend Strength: {latest['ADX']:.2f} ({latest['Trend_Strength']})\n")
            
            # Overall trend following signal
            if latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == 1 and latest['ADX'] > 25:
                f.write("Overall Trend Signal: STRONG BULLISH\n")
            elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == -1 and latest['ADX'] > 25:
                f.write("Overall Trend Signal: STRONG BEARISH\n")
            elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == 1:
                f.write("Overall Trend Signal: BULLISH\n")
            elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == -1:
                f.write("Overall Trend Signal: BEARISH\n")
            else:
                f.write("Overall Trend Signal: MIXED/NEUTRAL\n")
            f.write("\n")
        
        # Add Momentum Strategy
        if 'RSI_Signal' in latest and 'MACD_Cross_Signal' in latest and 'Stoch_Signal' in latest:
            f.write("MOMENTUM VALIDATION STRATEGY:\n")
            
            rsi_signal = "Bullish" if latest['RSI_Signal'] == 1 else ("Bearish" if latest['RSI_Signal'] == -1 else "Neutral")
            macd_signal = "Bullish" if latest['MACD_Cross_Signal'] == 1 else "Bearish"
            stoch_signal = "Bullish" if latest['Stoch_Signal'] == 1 else ("Bearish" if latest['Stoch_Signal'] == -1 else "Neutral")
            
            f.write(f"RSI(14) Signal: {rsi_signal}\n")
            f.write(f"MACD Cross Signal: {macd_signal}\n")
            f.write(f"Stochastic Signal: {stoch_signal}\n")
            
            # Overall momentum signal
            f.write(f"Momentum Score: {latest['Momentum_Score']}\n")
            if latest['Momentum_Score'] >= 2:
                f.write("Overall Momentum Signal: STRONG BULLISH\n")
            elif latest['Momentum_Score'] <= -2:
                f.write("Overall Momentum Signal: STRONG BEARISH\n")
            elif latest['Momentum_Score'] > 0:
                f.write("Overall Momentum Signal: BULLISH\n")
            elif latest['Momentum_Score'] < 0:
                f.write("Overall Momentum Signal: BEARISH\n")
            else:
                f.write("Overall Momentum Signal: NEUTRAL\n")
            f.write("\n")
        
        # Add Volatility Strategy
        if 'BB_Squeeze' in latest and 'ATR_Percent' in latest:
            f.write("VOLATILITY TRADING STRATEGY:\n")
            
            # BB Squeeze status
            f.write(f"Bollinger Band Squeeze: {'Yes' if latest['BB_Squeeze'] == 1 else 'No'}\n")
            f.write(f"Bollinger Band Width: {latest['BB_Width']:.4f}\n")
            f.write(f"ATR(14) Percentage: {latest['ATR_Percent']:.2f}%\n")
            
            # Volatility assessment
            if latest['BB_Squeeze'] == 1:
                f.write("Volatility Status: LOW - Potential breakout setup\n")
            elif latest['ATR_Percent'] > 2.0:
                f.write("Volatility Status: HIGH - Trending market\n")
            else:
                f.write("Volatility Status: NORMAL\n")
            f.write("\n")
            
        # Add Ichimoku Strategy
        if 'Cloud_Direction' in latest and 'SAR_Signal' in latest and 'OBV_Signal' in latest:
            f.write("ICHIMOKU MULTI-TIMEFRAME STRATEGY:\n")
            
            cloud_dir = "Bullish" if latest['Cloud_Direction'] == 1 else ("Bearish" if latest['Cloud_Direction'] == -1 else "Neutral")
            sar_signal = "Bullish" if latest['SAR_Signal'] == 1 else "Bearish"
            obv_signal = "Bullish" if latest['OBV_Signal'] == 1 else "Bearish"
            
            f.write(f"Ichimoku Cloud: {cloud_dir}\n")
            f.write(f"Parabolic SAR: {sar_signal}\n")
            f.write(f"On-Balance Volume: {obv_signal}\n")
            
            # Overall Ichimoku signal
            score = (1 if latest['Cloud_Direction'] == 1 else (-1 if latest['Cloud_Direction'] == -1 else 0)) + \
                    latest['SAR_Signal'] + latest['OBV_Signal']
                    
            if score >= 2:
                f.write("Overall Ichimoku Signal: STRONG BULLISH\n")
            elif score <= -2:
                f.write("Overall Ichimoku Signal: STRONG BEARISH\n")
            elif score > 0:
                f.write("Overall Ichimoku Signal: BULLISH\n")
            elif score < 0:
                f.write("Overall Ichimoku Signal: BEARISH\n")
            else:
                f.write("Overall Ichimoku Signal: NEUTRAL\n")
        
        # Add a simple trend analysis based on MA crossovers
        f.write("\n")
        f.write("TRADITIONAL TREND ANALYSIS:\n")
        if latest['Close'] > latest['SMA20'] and latest['SMA20'] > latest['SMA50']:
            f.write("Short-term trend: BULLISH\n")
        elif latest['Close'] < latest['SMA20'] and latest['SMA20'] < latest['SMA50']:
            f.write("Short-term trend: BEARISH\n")
        else:
            f.write("Short-term trend: NEUTRAL\n")
            
        if latest['SMA50'] > latest['SMA150']:
            f.write("Long-term trend: BULLISH\n")
        elif latest['SMA50'] < latest['SMA150']:
            f.write("Long-term trend: BEARISH\n")
        else:
            f.write("Long-term trend: NEUTRAL\n")
            
    print(f"Report saved to {filepath}")
    return filepath


def plot_indicators(data, symbol, output_dir, chart_date=None, strategy="default"):
    """
    Generate plots of key indicators.
    
    Args:
        data (pandas.DataFrame): Data with indicators
        symbol (str): Symbol being analyzed
        output_dir (str): Directory to save the charts
        chart_date (str): Date in YYYYMMDD format for the chart filename
        strategy (str): Trading strategy parameter set ('default', 'short_term', 'medium_term', 'high_freq',
                        'trend_following', 'momentum', 'volatility', 'ichimoku')
        
    Returns:
        list: Paths to the generated chart files
    """
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format the date for the filename
    if chart_date:
        current_date = chart_date
    else:
        current_date = pd.Timestamp.now().strftime("%Y%m%d")
        
    chart_files = []
    
    try:
        # Plot 1: Price with Moving Averages - based on strategy
        plt.figure(figsize=(12, 8))
        plt.subplot(3, 1, 1)
        plt.plot(data.index, data['Close'], label='Close Price')
        
        if strategy == "short_term":
            # Short-term trading MAs
            plt.plot(data.index, data['SMA9'], label='SMA9')
            plt.plot(data.index, data['SMA21'], label='SMA21')
            plt.plot(data.index, data['EMA12'], label='EMA12')
            plt.plot(data.index, data['EMA26'], label='EMA26')
            plt.title(f'{symbol} Price with Short-Term MAs')
        elif strategy == "medium_term":
            # Medium-term trading MAs
            plt.plot(data.index, data['SMA50'], label='SMA50')
            plt.plot(data.index, data['SMA200'], label='SMA200')  
            plt.plot(data.index, data['EMA50'], label='EMA50')
            plt.plot(data.index, data['EMA200'], label='EMA200')
            plt.title(f'{symbol} Price with Medium-Term MAs')
        elif strategy == "trend_following":
            # Trend following strategy MAs
            plt.plot(data.index, data['SMA50'], label='SMA50')
            plt.plot(data.index, data['SMA200'], label='SMA200')
            plt.plot(data.index, data['EMA12'], label='EMA12')
            plt.plot(data.index, data['EMA26'], label='EMA26')
            plt.title(f'{symbol} Trend Following - SMA/EMA Crossovers')
        else:
            # Default MA parameters
            plt.plot(data.index, data['SMA20'], label='SMA20')
            plt.plot(data.index, data['SMA50'], label='SMA50')
            plt.plot(data.index, data['SMA200'], label='SMA200')
            plt.title(f'{symbol} Price with Moving Averages')
        
        plt.legend()
        plt.grid(True)
        
        # Plot 2: RSI or ADX based on strategy
        plt.subplot(3, 1, 2)
        
        if strategy == "high_freq":
            plt.plot(data.index, data['RSI7'], label='RSI(7)')
            plt.axhline(y=70, color='r', linestyle='-', alpha=0.3)
            plt.axhline(y=30, color='g', linestyle='-', alpha=0.3)
            plt.title('RSI(7)')
        elif strategy == "trend_following":
            plt.plot(data.index, data['ADX'], label='ADX(14)')
            plt.axhline(y=25, color='r', linestyle='-', alpha=0.3, label='Strong Trend')
            plt.axhline(y=20, color='y', linestyle='-', alpha=0.3, label='Moderate Trend')
            plt.title('ADX - Trend Strength')
        else:
            plt.plot(data.index, data['RSI'], label='RSI(14)')
            plt.axhline(y=70, color='r', linestyle='-', alpha=0.3)
            plt.axhline(y=30, color='g', linestyle='-', alpha=0.3)
            plt.title('RSI(14)')
            
        plt.legend()
        plt.grid(True)
        
        # Plot 3: MACD or Stochastic based on strategy
        plt.subplot(3, 1, 3)
        
        if strategy == "high_freq":
            plt.plot(data.index, data['MACD_HF'], label='MACD(5,35,5)')
            plt.plot(data.index, data['MACD_HF_Signal'], label='Signal')
            plt.bar(data.index, data['MACD_HF_Histogram'], color='gray', alpha=0.3, label='Histogram')
            plt.title('High-Frequency MACD')
        elif strategy == "momentum":
            plt.plot(data.index, data['STOCH_K'], label='%K')
            plt.plot(data.index, data['STOCH_D'], label='%D')
            plt.axhline(y=80, color='r', linestyle='-', alpha=0.3)
            plt.axhline(y=20, color='g', linestyle='-', alpha=0.3)
            plt.title('Stochastic Oscillator')
        else:
            plt.plot(data.index, data['MACD'], label='MACD(12,26,9)')
            plt.plot(data.index, data['MACD_Signal'], label='Signal')
            plt.bar(data.index, data['MACD_Histogram'], color='gray', alpha=0.3, label='Histogram')
            plt.title('MACD')
            
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        # Save the chart
        chart1_filename = f"{symbol}_indicators_{current_date}.png"
        chart1_path = os.path.join(output_dir, chart1_filename)
        plt.savefig(chart1_path)
        chart_files.append(chart1_path)
        
        # Plot 2: Volatility indicators based on strategy
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Close'], label='Close Price')
        
        if strategy == "tight_channel":
            # Tight channel Bollinger Bands
            plt.plot(data.index, data['BB_Tight_High'], label='BB Upper (14, 1.5σ)')
            plt.plot(data.index, data['BB_Tight_Mid'], label='BB Middle (14)')
            plt.plot(data.index, data['BB_Tight_Low'], label='BB Lower (14, 1.5σ)')
            plt.fill_between(data.index, data['BB_Tight_High'], data['BB_Tight_Low'], alpha=0.1)
            plt.title(f'{symbol} Tight Channel Bollinger Bands (14, 1.5σ)')
        elif strategy == "wide_channel":
            # Wide channel Bollinger Bands
            plt.plot(data.index, data['BB_Wide_High'], label='BB Upper (30, 2.5σ)')
            plt.plot(data.index, data['BB_Wide_Mid'], label='BB Middle (30)')
            plt.plot(data.index, data['BB_Wide_Low'], label='BB Lower (30, 2.5σ)')
            plt.fill_between(data.index, data['BB_Wide_High'], data['BB_Wide_Low'], alpha=0.1)
            plt.title(f'{symbol} Wide Channel Bollinger Bands (30, 2.5σ)')
        elif strategy == "volatility":
            # Bollinger Bands and Keltner Channels together
            plt.plot(data.index, data['BB_High'], label='BB Upper')
            plt.plot(data.index, data['BB_Low'], label='BB Lower')
            plt.plot(data.index, data['Keltner_High'], label='Keltner Upper', linestyle='--')
            plt.plot(data.index, data['Keltner_Low'], label='Keltner Lower', linestyle='--')
            plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=0.1, color='blue')
            
            # Highlight squeeze areas
            squeeze_indices = data.index[data['BB_Squeeze'] == 1]
            if len(squeeze_indices) > 0:
                plt.scatter(squeeze_indices, data.loc[squeeze_indices, 'Close'], 
                           color='red', marker='^', s=50, label='Squeeze')
            
            plt.title(f'{symbol} Bollinger Bands and Keltner Channels')
        else:
            # Default Bollinger Bands
            plt.plot(data.index, data['BB_High'], label='BB Upper (20, 2σ)')
            plt.plot(data.index, data['BB_Mid'], label='BB Middle (20)')
            plt.plot(data.index, data['BB_Low'], label='BB Lower (20, 2σ)')
            plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=0.1)
            plt.title(f'{symbol} Bollinger Bands (20, 2σ)')
            
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # Save the chart
        chart2_filename = f"{symbol}_bollinger_{current_date}.png"
        chart2_path = os.path.join(output_dir, chart2_filename)
        plt.savefig(chart2_path)
        chart_files.append(chart2_path)
        
        # Plot 3: Ichimoku Cloud chart if selected
        if strategy == "ichimoku" and 'Ichimoku_SpanA' in data.columns:
            plt.figure(figsize=(12, 8))
            
            # Subplot 1: Price with Ichimoku Cloud
            plt.subplot(2, 1, 1)
            
            # Plot the cloud (area between Span A and Span B)
            plt.fill_between(data.index, data['Ichimoku_SpanA'], data['Ichimoku_SpanB'], 
                           where=data['Ichimoku_SpanA'] >= data['Ichimoku_SpanB'], 
                           color='lightgreen', alpha=0.3)
            plt.fill_between(data.index, data['Ichimoku_SpanA'], data['Ichimoku_SpanB'], 
                           where=data['Ichimoku_SpanA'] < data['Ichimoku_SpanB'], 
                           color='lightcoral', alpha=0.3)
            
            # Plot price and Ichimoku components
            plt.plot(data.index, data['Close'], label='Close', color='black')
            plt.plot(data.index, data['Ichimoku_Tenkan'], label='Tenkan-sen (9)', color='red')
            plt.plot(data.index, data['Ichimoku_Kijun'], label='Kijun-sen (26)', color='blue')
            plt.plot(data.index, data['Ichimoku_SpanA'], label='Span A', color='green')
            plt.plot(data.index, data['Ichimoku_SpanB'], label='Span B', color='red', alpha=0.5)
            
            # If we have Chikou Span (lagging line), plot it
            if 'Ichimoku_Chikou' in data.columns:
                chikou_valid = data['Ichimoku_Chikou'].dropna()
                if len(chikou_valid) > 0:
                    plt.plot(chikou_valid.index, chikou_valid, label='Chikou Span', color='purple')
            
            plt.title(f'{symbol} Ichimoku Cloud')
            plt.legend()
            plt.grid(True)
            
            # Subplot 2: Parabolic SAR and On-Balance Volume
            plt.subplot(2, 1, 2)
            
            # Twin axes for price and OBV
            ax1 = plt.gca()
            ax2 = ax1.twinx()
            
            # Plot price and SAR on primary axis
            ax1.plot(data.index, data['Close'], label='Close', color='black', alpha=0.5)
            ax1.scatter(data.index, data['SAR'], label='SAR', marker='.', color='blue', s=15)
            
            # Plot OBV and its MA on secondary axis
            ax2.plot(data.index, data['OBV'], label='OBV', color='purple', alpha=0.7)
            if 'OBV_MA' in data.columns:
                ax2.plot(data.index, data['OBV_MA'], label='OBV MA(20)', color='orange')
            
            # Set labels and legend
            ax1.set_ylabel('Price', color='black')
            ax2.set_ylabel('OBV', color='purple')
            
            # Add legends for both axes
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.title(f'{symbol} Parabolic SAR and On-Balance Volume')
            ax1.grid(True)
            
            plt.tight_layout()
            
            # Save the Ichimoku chart
            chart3_filename = f"{symbol}_ichimoku_{current_date}.png"
            chart3_path = os.path.join(output_dir, chart3_filename)
            plt.savefig(chart3_path)
            chart_files.append(chart3_path)
            
        # Plot 4: Strategy combination chart for trend following, momentum, or volatility
        if strategy in ["trend_following", "momentum", "volatility"]:
            plt.figure(figsize=(12, 8))
            
            if strategy == "trend_following":
                # Trend Following Combo: SMA(50,200) + EMA(12,26) + ADX(14)
                plt.subplot(3, 1, 1)
                plt.plot(data.index, data['Close'], label='Close', color='black')
                plt.plot(data.index, data['SMA50'], label='SMA50', color='blue')
                plt.plot(data.index, data['SMA200'], label='SMA200', color='red')
                plt.title(f'{symbol} - SMA50/200 Golden/Death Cross')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 2)
                plt.plot(data.index, data['Close'], label='Close', color='black')
                plt.plot(data.index, data['EMA12'], label='EMA12', color='green')
                plt.plot(data.index, data['EMA26'], label='EMA26', color='purple')
                plt.title(f'{symbol} - EMA12/26 Crossover')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 3)
                plt.plot(data.index, data['ADX'], label='ADX(14)', color='orange')
                plt.axhline(y=25, color='r', linestyle='--', alpha=0.7, label='Strong Trend')
                plt.axhline(y=20, color='y', linestyle='--', alpha=0.7, label='Moderate Trend')
                plt.title(f'{symbol} - ADX Trend Strength')
                plt.legend()
                plt.grid(True)
                
                chart4_filename = f"{symbol}_trend_strategy_{current_date}.png"
                
            elif strategy == "momentum":
                # Momentum Validation Combo: RSI(14) + MACD(12,26,9) + Stochastic(14,3)
                plt.subplot(3, 1, 1)
                plt.plot(data.index, data['RSI'], label='RSI(14)')
                plt.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
                plt.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
                plt.title(f'{symbol} - RSI(14)')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 2)
                plt.plot(data.index, data['MACD'], label='MACD', color='blue')
                plt.plot(data.index, data['MACD_Signal'], label='Signal', color='red')
                plt.bar(data.index, data['MACD_Histogram'], color='gray', alpha=0.5, label='Histogram')
                plt.title(f'{symbol} - MACD(12,26,9)')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 3)
                plt.plot(data.index, data['STOCH_K'], label='%K', color='green')
                plt.plot(data.index, data['STOCH_D'], label='%D', color='red')
                plt.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='Overbought')
                plt.axhline(y=20, color='g', linestyle='--', alpha=0.7, label='Oversold')
                plt.title(f'{symbol} - Stochastic(14,3)')
                plt.legend()
                plt.grid(True)
                
                chart4_filename = f"{symbol}_momentum_strategy_{current_date}.png"
                
            elif strategy == "volatility":
                # Volatility Trading Combo: Bollinger Bands + ATR + Keltner Channels
                plt.subplot(3, 1, 1)
                plt.plot(data.index, data['Close'], label='Close', color='black')
                plt.plot(data.index, data['BB_High'], label='BB Upper', color='blue')
                plt.plot(data.index, data['BB_Mid'], label='BB Middle', color='blue', linestyle='--')
                plt.plot(data.index, data['BB_Low'], label='BB Lower', color='blue')
                plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=0.1, color='blue')
                plt.title(f'{symbol} - Bollinger Bands(20,2)')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 2)
                plt.plot(data.index, data['ATR'], label='ATR(14)', color='purple')
                plt.plot(data.index, data['ATR_Percent'], label='ATR %', color='orange')
                plt.title(f'{symbol} - Average True Range (14)')
                plt.legend()
                plt.grid(True)
                
                plt.subplot(3, 1, 3)
                plt.plot(data.index, data['Close'], label='Close', color='black')
                plt.plot(data.index, data['Keltner_High'], label='Keltner Upper', color='green')
                plt.plot(data.index, data['Keltner_Mid'], label='Keltner Middle', color='green', linestyle='--')
                plt.plot(data.index, data['Keltner_Low'], label='Keltner Lower', color='green')
                
                # Highlight BB Squeeze points
                squeeze_indices = data.index[data['BB_Squeeze'] == 1]
                if len(squeeze_indices) > 0:
                    plt.scatter(squeeze_indices, data.loc[squeeze_indices, 'Close'], 
                               color='red', marker='^', s=50, label='Squeeze')
                
                plt.title(f'{symbol} - Keltner Channels with BB Squeeze')
                plt.legend()
                plt.grid(True)
                
                chart4_filename = f"{symbol}_volatility_strategy_{current_date}.png"
            
            plt.tight_layout()
            chart4_path = os.path.join(output_dir, chart4_filename)
            plt.savefig(chart4_path)
            chart_files.append(chart4_path)
        
    except Exception as e:
        print(f"Error generating charts: {str(e)}")
        # Create a simple error chart as a fallback
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(data.index, data['Close'], 'b-', label='Price')
            plt.title(f"{symbol} Price Chart (Error in full chart generation)")
            plt.grid(True)
            plt.legend()
            
            # Save the fallback chart
            fallback_filename = f"{symbol}_basic_{current_date}.png"
            fallback_path = os.path.join(output_dir, fallback_filename)
            plt.savefig(fallback_path)
            chart_files.append(fallback_path)
            print(f"Created fallback chart: {fallback_path}")
        except Exception as fallback_error:
            print(f"Failed to create even fallback chart: {str(fallback_error)}")
    
    finally:
        plt.close('all')  # Close all figures to free memory
    
    print(f"Charts saved to {output_dir}")
    return chart_files


def main():
    """Main function to parse command line arguments and calculate indicators."""
    parser = argparse.ArgumentParser(description="Calculate technical indicators")
    parser.add_argument("file", help="Path to the CSV or Excel file with market data")
    parser.add_argument("--symbol", help="Symbol name for the report", required=True)
    parser.add_argument("--output_data", default=None, help="Directory to save processed data")
    parser.add_argument("--output_charts", default=None, help="Directory to save charts")
    parser.add_argument("--output_report", default=None, help="Directory to save the report")
    parser.add_argument("--strategy", default="default", 
                       choices=["default", "short_term", "medium_term", "high_freq", 
                                "tight_channel", "wide_channel", "trend_following", 
                                "momentum", "volatility", "ichimoku"],
                       help="Trading strategy parameter set")
    
    args = parser.parse_args()
    
    # Load the data
    data = load_data(args.file)
    
    # Calculate indicators
    data_with_indicators = calculate_indicators(data, parameter_set=args.strategy)
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # Set default output directories if not provided
    if args.output_data is None:
        output_data_dir = os.path.join(project_dir, "Data")
    else:
        output_data_dir = args.output_data
        
    if args.output_charts is None:
        output_charts_dir = os.path.join(project_dir, "Charts")
    else:
        output_charts_dir = args.output_charts
        
    if args.output_report is None:
        output_report_dir = os.path.join(project_dir, "Reports")
    else:
        output_report_dir = args.output_report
    
    # Save processed data
    os.makedirs(output_data_dir, exist_ok=True)
    output_data_path = os.path.join(output_data_dir, f"{args.symbol}_with_indicators.csv")
    data_with_indicators.to_csv(output_data_path)
    print(f"Processed data saved to {output_data_path}")
    
    # Generate report
    report_path = generate_report(data_with_indicators, args.symbol, output_report_dir)
    
    # Generate charts
    chart_paths = plot_indicators(data_with_indicators, args.symbol, output_charts_dir, strategy=args.strategy)
    
    print("\nAnalysis completed successfully!")
    print(f"Strategy: {args.strategy}")
    
    # Show a strategy-specific message
    if args.strategy == "trend_following":
        print("\nTrend Following Strategy: SMA(50,200) + EMA(12,26) + ADX(14)")
        print("Ideal for identifying strong trends and filtering false breakouts")
    elif args.strategy == "momentum":
        print("\nMomentum Validation Strategy: RSI(14) + MACD(12,26,9) + Stochastic(14,3)")
        print("Ideal for confirming price breakout validity and capturing overbought/oversold conditions")
    elif args.strategy == "volatility":
        print("\nVolatility Trading Strategy: Bollinger Bands(20,2) + ATR(14) + Keltner Channels")
        print("Ideal for capturing range breakout opportunities in oscillating markets")
    elif args.strategy == "ichimoku":
        print("\nMulti-timeframe Strategy: Ichimoku Cloud(9,26,52) + Parabolic SAR(0.02,0.2) + On-Balance Volume")
        print("Ideal for providing multi-timeframe decision support")
        
    print(f"\nReport: {report_path}")
    print(f"Charts: {', '.join(chart_paths)}")


if __name__ == "__main__":
    main()
