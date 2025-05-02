#!/usr/bin/env python
"""
Technical Analysis Indicators Calculator
---------------------------------------
This script calculates various technical indicators on market data.
It uses numpy and pandas for calculations without relying on external TA libraries.

Includes indicator combinations for different trading strategies:
- Trend Following: SMA, EMA, ADX
- Momentum Validation: RSI, MACD, Stochastic
- Volatility Trading: Bollinger Bands
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

# Indicator calculation functions
def sma(series, length):
    """Calculate Simple Moving Average (robust to 1D input)"""
    series = pd.Series(np.asarray(series).reshape(-1))
    return series.rolling(window=length).mean()

def ema(series, length):
    """Calculate Exponential Moving Average (robust to 1D input)"""
    series = pd.Series(np.asarray(series).reshape(-1))
    return series.ewm(span=length, adjust=False).mean()

def rsi(close, length=14):
    """Calculate Relative Strength Index (robust to 1D input)"""
    close = pd.Series(np.asarray(close).reshape(-1))
    delta = close.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gain = gains.rolling(window=length).mean()
    avg_loss = losses.rolling(window=length).mean()
    # Avoid division by zero
    avg_loss = avg_loss.replace(0, 0.00001)
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(close, fast=12, slow=26, signal=9):
    """Calculate MACD (robust to 1D input)"""
    close = pd.Series(np.asarray(close).reshape(-1))
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame({
        'MACD': macd_line,
        'MACD_Signal': signal_line,
        'MACD_Histogram': histogram
    }, index=close.index)

def bbands(close, length=20, std=2):
    """Calculate Bollinger Bands (robust to 1D input)"""
    close = pd.Series(np.asarray(close).reshape(-1))
    middle = sma(close, length)
    std_dev = close.rolling(window=length).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return pd.DataFrame({
        'BB_High': upper,
        'BB_Mid': middle,
        'BB_Low': lower
    }, index=close.index)

def stoch(high, low, close, k=14, d=3, smooth_k=3):
    """Calculate Stochastic Oscillator (robust to 1D input)"""
    high = pd.Series(np.asarray(high).reshape(-1))
    low = pd.Series(np.asarray(low).reshape(-1))
    close = pd.Series(np.asarray(close).reshape(-1))
    lowest_low = low.rolling(window=k).min()
    highest_high = high.rolling(window=k).max()
    
    # Avoid division by zero by adding a small epsilon
    denominator = highest_high - lowest_low
    denominator = denominator.replace(0, 0.00001)
    
    k_percent = 100 * ((close - lowest_low) / denominator)
    if smooth_k > 1:
        k_percent = k_percent.rolling(window=smooth_k).mean()
    d_percent = k_percent.rolling(window=d).mean()
    return pd.DataFrame({
        'STOCH_K': k_percent,
        'STOCH_D': d_percent
    }, index=close.index)

def psar(high, low, close, af_start=0.02, af_step=0.02, af_max=0.2):
    """Calculate Parabolic SAR (robust to Series/2D input)"""
    # Ensure inputs are 1D numpy arrays and wrap as Series
    high = pd.Series(np.asarray(high).reshape(-1))
    low = pd.Series(np.asarray(low).reshape(-1))
    close = pd.Series(np.asarray(close).reshape(-1))
    n = len(close)
    psar = np.zeros(n)
    ep = np.zeros(n)
    af = np.zeros(n)
    trending = np.zeros(n)  # 1 for uptrend, -1 for downtrend
    # Initial values
    psar[0] = float(low.iloc[0])
    trending[0] = 1  # Assume uptrend to start
    ep[0] = float(high.iloc[0])
    af[0] = af_start
    # Calculate PSAR values
    for i in range(1, n):
        prev_psar = psar[i-1]
        prev_ep = ep[i-1]
        prev_af = af[i-1]
        prev_trend = trending[i-1]
        if prev_trend == 1:  # Uptrend
            psar[i] = prev_psar + prev_af * (prev_ep - prev_psar)
            # Check for trend reversal
            if float(low.iloc[i]) < psar[i]:
                trending[i] = -1  # Switch to downtrend
                psar[i] = prev_ep
                ep[i] = float(low.iloc[i])
                af[i] = af_start
            else:
                trending[i] = 1  # Maintain uptrend
                if float(high.iloc[i]) > prev_ep:
                    ep[i] = float(high.iloc[i])
                    af[i] = min(prev_af + af_step, af_max)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af
        else:  # Downtrend
            psar[i] = prev_psar - prev_af * (prev_psar - prev_ep)
            # Check for trend reversal
            if float(high.iloc[i]) > psar[i]:
                trending[i] = 1  # Switch to uptrend
                psar[i] = prev_ep
                ep[i] = float(high.iloc[i])
                af[i] = af_start
            else:
                trending[i] = -1  # Maintain downtrend
                if float(low.iloc[i]) < prev_ep:
                    ep[i] = float(low.iloc[i])
                    af[i] = min(prev_af + af_step, af_max)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af
    return pd.Series(psar, index=close.index)

def obv(close, volume):
    """Calculate On-Balance Volume (robust to 2D/Series input)"""
    # Ensure inputs are numpy arrays and flatten to 1D if needed
    close = np.asarray(close).reshape(-1)
    volume = np.asarray(volume).reshape(-1)
    # Convert to pandas Series with default integer index
    close = pd.Series(close)
    volume = pd.Series(volume)
    # Calculate direction
    direction = np.where(close > close.shift(1), 1, np.where(close < close.shift(1), -1, 0))
    # Calculate OBV
    obv = (direction * volume).cumsum()
    return pd.Series(obv, index=close.index)

def adx(high, low, close, length=14):
    """Calculate Average Directional Index (robust to scalar/2D input)"""
    # Ensure inputs are numpy arrays and flatten to 1D if needed
    high = np.asarray(high).reshape(-1)
    low = np.asarray(low).reshape(-1)
    close = np.asarray(close).reshape(-1)
    # Convert to pandas Series with default integer index
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}, index=high.index).max(axis=1)
    
    # Calculate directional movement
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    # Calculate positive directional movement (+DM)
    pdm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    
    # Calculate negative directional movement (-DM)
    ndm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    
    # Smooth TR, +DM, -DM using Wilder's method
    smoothed_tr = tr.copy()
    smoothed_pdm = pdm.copy()
    smoothed_ndm = ndm.copy()
    
    # Apply Wilder's smoothing
    for i in range(1, len(tr)):
        smoothed_tr.iloc[i] = smoothed_tr.iloc[i-1] - (smoothed_tr.iloc[i-1] / length) + tr.iloc[i]
        smoothed_pdm.iloc[i] = smoothed_pdm.iloc[i-1] - (smoothed_pdm.iloc[i-1] / length) + pdm.iloc[i]
        smoothed_ndm.iloc[i] = smoothed_ndm.iloc[i-1] - (smoothed_ndm.iloc[i-1] / length) + ndm.iloc[i]
    
    # Avoid division by zero
    smoothed_tr = smoothed_tr.replace(0, 0.00001)
    
    # Calculate positive directional index (+DI) and negative directional index (-DI)
    pdi = 100 * (smoothed_pdm / smoothed_tr)
    ndi = 100 * (smoothed_ndm / smoothed_tr)
    
    # Calculate directional index (DX)
    # Avoid division by zero
    sum_di = pdi + ndi
    sum_di = sum_di.replace(0, 0.00001)
    
    dx = 100 * abs(pdi - ndi) / sum_di
    
    # Calculate ADX as smoothed DX
    adx = dx.rolling(window=length).mean()
    
    return pd.DataFrame({
        'ADX': adx,
        'PDI': pdi,
        'NDI': ndi
    })

def ichimoku(high, low, close, tenkan=9, kijun=26, senkou=52):
    """Calculate Ichimoku Cloud components (robust to 1D input)"""
    high = pd.Series(np.asarray(high).reshape(-1))
    low = pd.Series(np.asarray(low).reshape(-1))
    close = pd.Series(np.asarray(close).reshape(-1))
    high_tenkan = high.rolling(window=tenkan).max()
    low_tenkan = low.rolling(window=tenkan).min()
    tenkan_sen = (high_tenkan + low_tenkan) / 2
    high_kijun = high.rolling(window=kijun).max()
    low_kijun = low.rolling(window=kijun).min()
    kijun_sen = (high_kijun + low_kijun) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    high_senkou = high.rolling(window=senkou).max()
    low_senkou = low.rolling(window=senkou).min()
    senkou_span_b = ((high_senkou + low_senkou) / 2).shift(kijun)
    chikou_span = close.shift(-kijun)
    return pd.DataFrame({
        'Ichimoku_Tenkan': tenkan_sen,
        'Ichimoku_Kijun': kijun_sen,
        'Ichimoku_SpanA': senkou_span_a,
        'Ichimoku_SpanB': senkou_span_b,
        'Ichimoku_Chikou': chikou_span
    }, index=close.index)

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
        data[f'SMA{window}'] = sma(data['Close'], window)
    
    # EMA
    for window in ma_windows:
        data[f'EMA{window}'] = ema(data['Close'], window)
    
    # Add short-term trading parameters
    if parameter_set in ['default', 'short_term']:
        # Short-term SMA and EMA
        data['SMA9'] = sma(data['Close'], 9)
        data['SMA21'] = sma(data['Close'], 21)
        data['EMA12'] = ema(data['Close'], 12)
        data['EMA26'] = ema(data['Close'], 26)
    
    # Add medium-term trend parameters
    if parameter_set in ['default', 'medium_term']:
        # Medium-term SMA and EMA (some already calculated in default)
        # SMA50 and EMA50 already calculated above
        data['SMA200'] = sma(data['Close'], 200)
        data['EMA200'] = ema(data['Close'], 200)
    
    # RSI - 14 period (default)
    data['RSI'] = rsi(data['Close'], 14)
    
    # Add high-frequency trading RSI(7)
    if parameter_set in ['default', 'high_freq']:
        data['RSI7'] = rsi(data['Close'], 7)
    
    # MACD - default parameters (12, 26, 9)
    macd_result = macd(data['Close'], 12, 26, 9)
    data['MACD'] = macd_result['MACD']
    data['MACD_Signal'] = macd_result['MACD_Signal']
    data['MACD_Histogram'] = macd_result['MACD_Histogram']
    
    # Add high-frequency MACD (5, 35, 5)
    if parameter_set in ['default', 'high_freq']:
        macd_hf_result = macd(data['Close'], 5, 35, 5)
        data['MACD_HF'] = macd_hf_result['MACD']
        data['MACD_HF_Signal'] = macd_hf_result['MACD_Signal']
        data['MACD_HF_Histogram'] = macd_hf_result['MACD_Histogram']
    
    # Bollinger Bands - default parameters (20, 2)
    bb_result = bbands(data['Close'], 20, 2)
    data['BB_High'] = bb_result['BB_High']
    data['BB_Mid'] = bb_result['BB_Mid']
    data['BB_Low'] = bb_result['BB_Low']
    
    # Add tight channel Bollinger Bands (14, 1.5)
    if parameter_set in ['default', 'tight_channel', 'volatility']:
        bb_tight_result = bbands(data['Close'], 14, 1.5)
        data['BB_Tight_High'] = bb_tight_result['BB_High']
        data['BB_Tight_Mid'] = bb_tight_result['BB_Mid']
        data['BB_Tight_Low'] = bb_tight_result['BB_Low']
    
    # Add wide channel Bollinger Bands (30, 2.5)
    if parameter_set in ['default', 'wide_channel']:
        bb_wide_result = bbands(data['Close'], 30, 2.5)
        data['BB_Wide_High'] = bb_wide_result['BB_High']
        data['BB_Wide_Mid'] = bb_wide_result['BB_Mid']
        data['BB_Wide_Low'] = bb_wide_result['BB_Low']
    
    # Calculate Parabolic SAR
    data['SAR'] = psar(data['High'], data['Low'], data['Close'], 0.02, 0.02, 0.2)
    
    # Calculate Stochastic Oscillator
    stoch_result = stoch(data['High'], data['Low'], data['Close'], 14, 3, 3)
    data['STOCH_K'] = stoch_result['STOCH_K']
    data['STOCH_D'] = stoch_result['STOCH_D']
    
    # ADX (Average Directional Index) - For trend strength
    adx_result = adx(data['High'], data['Low'], data['Close'], 14)
    data['ADX'] = adx_result['ADX']
    data['PDI'] = adx_result['PDI']
    data['NDI'] = adx_result['NDI']
    
    # On-Balance Volume (OBV)
    data['OBV'] = obv(data['Close'], data['Volume'])
    
    # Calculate Ichimoku Cloud components
    if parameter_set in ['default', 'ichimoku']:
        try:
            ichimoku_result = ichimoku(data['High'], data['Low'], data['Close'], 9, 26, 52)
            # 首先将计算结果添加到数据框中
            for col in ichimoku_result.columns:
                data[col] = ichimoku_result[col]
            
            # 注释掉可能导致索引对齐问题的部分
            # 这里添加一个默认值
            data['Cloud_Direction'] = 0
            
            '''
            # 原始代码导致索引对齐问题
            close = data['Close']
            span_a = data['Ichimoku_SpanA']
            span_b = data['Ichimoku_SpanB']
            
            # 如果有DataFrame，强制只取第一列
            if isinstance(close, pd.DataFrame):
                close = close.squeeze()
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
            if isinstance(span_a, pd.DataFrame):
                span_a = span_a.squeeze()
                if isinstance(span_a, pd.DataFrame):
                    span_a = span_a.iloc[:, 0]
            if isinstance(span_b, pd.DataFrame):
                span_b = span_b.squeeze()
                if isinstance(span_b, pd.DataFrame):
                    span_b = span_b.iloc[:, 0]
            
            # 确保索引一致
            close = close.reindex(data.index)
            span_a = span_a.reindex(data.index)
            span_b = span_b.reindex(data.index)
            
            # 计算Cloud Direction
            cloud_dir = np.where(close > span_a, 1, np.where(close < span_b, -1, 0))
            data['Cloud_Direction'] = pd.Series(cloud_dir, index=data.index)
            '''
            
        except Exception as e:
            print(f"Error calculating Ichimoku Cloud: {e}")
            # 如果出错，至少添加空列以防止后面的错误
            data['Ichimoku_Tenkan'] = np.nan
            data['Ichimoku_Kijun'] = np.nan
            data['Ichimoku_SpanA'] = np.nan
            data['Ichimoku_SpanB'] = np.nan
            data['Ichimoku_Chikou'] = np.nan
            data['Cloud_Direction'] = 0
    
    return data
