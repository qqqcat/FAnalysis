#!/usr/bin/env python
"""
Technical Analysis Indicators Calculator
---------------------------------------
This script calculates various technical indicators on market data.
It uses pandas-ta library for efficient and reliable technical indicator calculations.

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
    Calculate various technical indicators using pandas-ta
    
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
    
    # Import pandas_ta inside function to avoid global import
    import pandas_ta as ta
    
    # Ensure we have the required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in data.columns:
            if col == 'Volume':
                data[col] = 0  # Default volume if not available
            else:
                raise ValueError(f"Required column {col} not found in dataframe")
    
    # Define parameter sets dictionary for better organization
    param_sets = {
        'default': {
            'ma': [5, 10, 20, 50, 100, 150],
            'short_ma': [9, 21],
            'long_ma': [200],
            'rsi': [14, 7],
            'macd': [
                {'fast': 12, 'slow': 26, 'signal': 9},
                {'fast': 5, 'slow': 35, 'signal': 5}
            ],
            'bbands': [
                {'length': 20, 'std': 2.0},
                {'length': 14, 'std': 1.5},
                {'length': 30, 'std': 2.5}
            ],
            'use_ichimoku': True
        },
        'short_term': {
            'ma': [5, 10, 20, 50],
            'short_ma': [9, 21],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [{'length': 20, 'std': 2.0}]
        },
        'medium_term': {
            'ma': [10, 20, 50, 100],
            'long_ma': [200],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [{'length': 20, 'std': 2.0}]
        },
        'high_freq': {
            'ma': [5, 10, 20, 50],
            'rsi': [7, 14],
            'macd': [
                {'fast': 12, 'slow': 26, 'signal': 9},
                {'fast': 5, 'slow': 35, 'signal': 5}
            ],
            'bbands': [{'length': 20, 'std': 2.0}]
        },
        'tight_channel': {
            'ma': [5, 10, 20, 50],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [
                {'length': 20, 'std': 2.0},
                {'length': 14, 'std': 1.5}
            ]
        },
        'wide_channel': {
            'ma': [5, 10, 20, 50],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [
                {'length': 20, 'std': 2.0},
                {'length': 30, 'std': 2.5}
            ]
        },
        'volatility': {
            'ma': [5, 10, 20, 50],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [
                {'length': 20, 'std': 2.0},
                {'length': 14, 'std': 1.5}
            ]
        },
        'ichimoku': {
            'ma': [5, 10, 20, 50],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [{'length': 20, 'std': 2.0}],
            'use_ichimoku': True
        }
    }
    
    # Use default if parameter_set not found
    params = param_sets.get(parameter_set, param_sets['default'])
    
    # Calculate Moving Averages - SMA and EMA
    for window in params.get('ma', []):
        data[f'SMA{window}'] = ta.sma(data['Close'], length=window)
        data[f'EMA{window}'] = ta.ema(data['Close'], length=window)
    
    # Add short-term trading parameters
    for window in params.get('short_ma', []):
        if f'SMA{window}' not in data.columns:
            data[f'SMA{window}'] = ta.sma(data['Close'], length=window)
        if f'EMA{window}' not in data.columns:
            data[f'EMA{window}'] = ta.ema(data['Close'], length=window)
    
    # Add medium-term trend parameters
    for window in params.get('long_ma', []):
        if f'SMA{window}' not in data.columns:
            data[f'SMA{window}'] = ta.sma(data['Close'], length=window)
        if f'EMA{window}' not in data.columns:
            data[f'EMA{window}'] = ta.ema(data['Close'], length=window)
    
    # Calculate RSI
    for length in params.get('rsi', [14]):
        if length == 14:
            data['RSI'] = ta.rsi(data['Close'], length=length)
        else:
            data[f'RSI{length}'] = ta.rsi(data['Close'], length=length)
    
    # Calculate MACD
    macd_configs = params.get('macd', [{'fast': 12, 'slow': 26, 'signal': 9}])
    for i, macd_params in enumerate(macd_configs):
        if i == 0:  # Default MACD
            macd_result = ta.macd(data['Close'], **macd_params)
            data['MACD'] = macd_result['MACD_12_26_9']
            data['MACD_Signal'] = macd_result['MACDs_12_26_9']
            data['MACD_Histogram'] = macd_result['MACDh_12_26_9']
        else:  # High-frequency MACD
            macd_result = ta.macd(data['Close'], **macd_params)
            fast, slow, signal = macd_params['fast'], macd_params['slow'], macd_params['signal']
            data[f'MACD_HF'] = macd_result[f'MACD_{fast}_{slow}_{signal}']
            data[f'MACD_HF_Signal'] = macd_result[f'MACDs_{fast}_{slow}_{signal}']
            data[f'MACD_HF_Histogram'] = macd_result[f'MACDh_{fast}_{slow}_{signal}']
    
    # Calculate Bollinger Bands
    bbands_configs = params.get('bbands', [{'length': 20, 'std': 2.0}])
    for i, bb_params in enumerate(bbands_configs):
        bbands_result = ta.bbands(data['Close'], **bb_params)
        
        if i == 0:  # Default Bollinger Bands
            data['BB_High'] = bbands_result[f"BBU_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Mid'] = bbands_result[f"BBM_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Low'] = bbands_result[f"BBL_{bb_params['length']}_{bb_params['std']}"]
            
            # Calculate BB Width
            data['BB_Width'] = (data['BB_High'] - data['BB_Low']) / data['BB_Mid']
        elif bb_params['length'] == 14 and bb_params['std'] == 1.5:  # Tight channel
            data['BB_Tight_High'] = bbands_result[f"BBU_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Tight_Mid'] = bbands_result[f"BBM_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Tight_Low'] = bbands_result[f"BBL_{bb_params['length']}_{bb_params['std']}"]
        elif bb_params['length'] == 30 and bb_params['std'] == 2.5:  # Wide channel
            data['BB_Wide_High'] = bbands_result[f"BBU_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Wide_Mid'] = bbands_result[f"BBM_{bb_params['length']}_{bb_params['std']}"]
            data['BB_Wide_Low'] = bbands_result[f"BBL_{bb_params['length']}_{bb_params['std']}"]
    
    # Stochastic Oscillator
    stoch_result = ta.stoch(data['High'], data['Low'], data['Close'], k=14, d=3, smooth_k=3)
    data['STOCH_K'] = stoch_result['STOCHk_14_3_3']
    data['STOCH_D'] = stoch_result['STOCHd_14_3_3']
    
    # ADX (Average Directional Index)
    adx_result = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    data['ADX'] = adx_result['ADX_14']
    data['PDI'] = adx_result['DMP_14']
    data['NDI'] = adx_result['DMN_14']
    
    # On-Balance Volume (OBV)
    data['OBV'] = ta.obv(data['Close'], data['Volume'])
    
    # Parabolic SAR
    sar_result = ta.psar(data['High'], data['Low'], data['Close'], af=0.02, max_af=0.2)
    
    # 处理不同版本pandas_ta库返回的键名差异
    if 'PSARl_0.020_0.200' in sar_result:
        data['SAR'] = sar_result['PSARl_0.020_0.200']
    elif 'PSAR_0.020_0.200' in sar_result:
        data['SAR'] = sar_result['PSAR_0.020_0.200']
    else:
        # 如果找不到已知的键名，尝试寻找包含PSAR的键
        psar_keys = [key for key in sar_result.keys() if 'PSAR' in key]
        if psar_keys:
            data['SAR'] = sar_result[psar_keys[0]]
        else:
            print(f"Warning: Could not find PSAR result in returned data. Available keys: {sar_result.keys()}")
            data['SAR'] = np.nan  # 使用NaN作为数据不可用的标识
    
    # Calculate Ichimoku Cloud
    if params.get('use_ichimoku', False):
        try:
            ichimoku_result = ta.ichimoku(data['High'], data['Low'], data['Close'], 
                                      tenkan=9, kijun=26, senkou=52)
            
            # 处理新版pandas_ta返回元组的情况
            if isinstance(ichimoku_result, tuple):
                # 新版pandas_ta返回(DataFrame, DataFrame)，第一个是指标值，第二个是云延迟值
                ichimoku_df = ichimoku_result[0]  # 获取第一个DataFrame
            else:
                # 旧版pandas_ta返回单个DataFrame
                ichimoku_df = ichimoku_result
            
            # Map Ichimoku columns to our naming convention
            ichimoku_mapping = {
                'ITS_9': 'Ichimoku_Tenkan',
                'IKS_26': 'Ichimoku_Kijun',
                'ISA_9': 'Ichimoku_SpanA',
                'ISB_26': 'Ichimoku_SpanB',
                'ICS_26': 'Ichimoku_Chikou'
            }
            
            for src, dst in ichimoku_mapping.items():
                if src in ichimoku_df.columns:
                    data[dst] = ichimoku_df[src]
                else:
                    # 尝试找到包含相似前缀的列
                    similar_found = False
                    for col in ichimoku_df.columns:
                        if src.split('_')[0] in col:
                            data[dst] = ichimoku_df[col]
                            similar_found = True
                            break
                    if not similar_found:
                        data[dst] = np.nan
            
            # Calculate Cloud Direction more reliably
            data['Cloud_Direction'] = 0
            data_with_cloud = data.dropna(subset=['Ichimoku_SpanA', 'Ichimoku_SpanB'])
            if not data_with_cloud.empty:
                mask_above = data_with_cloud['Close'] > data_with_cloud['Ichimoku_SpanA']
                mask_below = data_with_cloud['Close'] < data_with_cloud['Ichimoku_SpanB']
                data.loc[mask_above.index, 'Cloud_Direction'] = 1
                data.loc[mask_below.index, 'Cloud_Direction'] = -1
            
        except Exception as e:
            print(f"Error calculating Ichimoku Cloud: {e}")
            # If error occurs, add empty columns to prevent downstream errors
            for col in ['Ichimoku_Tenkan', 'Ichimoku_Kijun', 'Ichimoku_SpanA', 
                        'Ichimoku_SpanB', 'Ichimoku_Chikou']:
                data[col] = np.nan
            data['Cloud_Direction'] = 0
            
    # Calculate ATR and ATR Percentage
    data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)
    data['ATR_Percent'] = (data['ATR'] / data['Close']) * 100
    
    # Calculate Keltner Channels if needed for BB squeeze
    if 'volatility' in parameter_set or 'default' in parameter_set:
        keltner_result = ta.kc(data['High'], data['Low'], data['Close'], length=20, scalar=2.0)
        
        # Handle different versions of pandas_ta
        kc_upper_key = next((k for k in keltner_result.keys() if 'KCU' in k), None)
        kc_lower_key = next((k for k in keltner_result.keys() if 'KCL' in k), None)
        kc_middle_key = next((k for k in keltner_result.keys() if 'KCM' in k), None)
        
        if kc_upper_key and kc_lower_key and kc_middle_key:
            data['Keltner_High'] = keltner_result[kc_upper_key]
            data['Keltner_Mid'] = keltner_result[kc_middle_key]
            data['Keltner_Low'] = keltner_result[kc_lower_key]
            
            # Calculate BB squeeze (when Bollinger Bands are inside Keltner Channels)
            data['BB_Squeeze'] = np.where(
                (data['BB_High'] < data['Keltner_High']) & 
                (data['BB_Low'] > data['Keltner_Low']),
                1, 0
            )
    
    # Calculate strategy signals
    # These are the signals that prepare_strategy_signals in generate_html_report.py expects
    
    # 1. SMA Cross Signal (SMA50 vs SMA200)
    if all(col in data.columns for col in ['SMA50', 'SMA200']):
        # 1 for bullish (SMA50 > SMA200), -1 for bearish
        data['SMA_Cross_Signal'] = np.where(data['SMA50'] > data['SMA200'], 1, -1)
    
    # 2. EMA Cross Signal (EMA12 vs EMA26)
    if all(col in data.columns for col in ['EMA12', 'EMA26']):
        # 1 for bullish (EMA12 > EMA26), -1 for bearish
        data['EMA_Cross_Signal'] = np.where(data['EMA12'] > data['EMA26'], 1, -1)
    
    # 3. MACD Cross Signal (MACD vs MACD_Signal)
    if all(col in data.columns for col in ['MACD', 'MACD_Signal']):
        # 1 for bullish (MACD > Signal), -1 for bearish
        data['MACD_Cross_Signal'] = np.where(data['MACD'] > data['MACD_Signal'], 1, -1)
    
    # 4. RSI Signal
    if 'RSI' in data.columns:
        # 1 for bullish (RSI oversold and rising), -1 for bearish (RSI overbought and falling), 0 for neutral
        data['RSI_Signal'] = 0
        # Oversold condition (RSI < 30 and rising)
        data.loc[(data['RSI'] < 30) & (data['RSI'].shift(1) < data['RSI']), 'RSI_Signal'] = 1
        # Overbought condition (RSI > 70 and falling)
        data.loc[(data['RSI'] > 70) & (data['RSI'].shift(1) > data['RSI']), 'RSI_Signal'] = -1
    
    # 5. Stochastic Signal
    if all(col in data.columns for col in ['STOCH_K', 'STOCH_D']):
        # 1 for bullish (K > D and K < 20), -1 for bearish (K < D and K > 80), 0 for neutral
        data['Stoch_Signal'] = 0
        # Bullish stochastic crossover in oversold territory
        data.loc[(data['STOCH_K'] > data['STOCH_D']) & (data['STOCH_K'] < 20), 'Stoch_Signal'] = 1
        # Bearish stochastic crossover in overbought territory
        data.loc[(data['STOCH_K'] < data['STOCH_D']) & (data['STOCH_K'] > 80), 'Stoch_Signal'] = -1
    
    # 6. SAR Signal
    if 'SAR' in data.columns:
        # 1 for bullish (Price > SAR), -1 for bearish
        data['SAR_Signal'] = np.where(data['Close'] > data['SAR'], 1, -1)
    
    # 7. OBV Signal (Simple moving average of OBV)
    if 'OBV' in data.columns:
        data['OBV_SMA'] = ta.sma(data['OBV'], length=20)
        # 1 for bullish (OBV > OBV_SMA), -1 for bearish
        data['OBV_Signal'] = np.where(data['OBV'] > data['OBV_SMA'], 1, -1)
    
    # 8. ADX Trend Strength
    if 'ADX' in data.columns:
        # Categorize trend strength based on ADX value
        data['Trend_Strength'] = 'Weak'
        data.loc[data['ADX'] > 20, 'Trend_Strength'] = 'Moderate'
        data.loc[data['ADX'] > 25, 'Trend_Strength'] = 'Strong'
        data.loc[data['ADX'] > 30, 'Trend_Strength'] = 'Very Strong'
    
    # 9. Momentum Score
    # Combine signals from RSI, MACD, and Stochastic for an overall momentum score
    data['Momentum_Score'] = 0
    if 'RSI_Signal' in data.columns:
        data['Momentum_Score'] += data['RSI_Signal']
    if 'MACD_Cross_Signal' in data.columns:
        data['Momentum_Score'] += data['MACD_Cross_Signal']
    if 'Stoch_Signal' in data.columns:
        data['Momentum_Score'] += data['Stoch_Signal']
    
    return data
