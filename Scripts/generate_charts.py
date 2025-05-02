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
        elif strategy == "trend_following" and 'ADX' in data.columns:
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
        
        if strategy == "high_freq" and 'MACD_HF' in data.columns:
            plt.plot(data.index, data['MACD_HF'], label='MACD(5,35,5)')
            plt.plot(data.index, data['MACD_HF_Signal'], label='Signal')
            plt.bar(data.index, data['MACD_HF_Histogram'], color='gray', alpha=0.3, label='Histogram')
            plt.title('High-Frequency MACD')
        elif strategy == "momentum" and 'STOCH_K' in data.columns and 'STOCH_D' in data.columns:
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
        chart1_filename = f"{symbol}_indicators_{chart_date}.png"
        chart1_path = os.path.join(output_dir, chart1_filename)
        plt.savefig(chart1_path)
        plt.close()
        chart_files.append(chart1_path)
        
        # Plot 2: Volatility indicators based on strategy
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Close'], label='Close Price')
        
        if strategy == "tight_channel" and all(col in data.columns for col in ['BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low']):
            # Tight channel Bollinger Bands
            plt.plot(data.index, data['BB_Tight_High'], label='BB Upper (14, 1.5σ)')
            plt.plot(data.index, data['BB_Tight_Mid'], label='BB Middle (14)')
            plt.plot(data.index, data['BB_Tight_Low'], label='BB Lower (14, 1.5σ)')
            plt.fill_between(data.index, data['BB_Tight_High'], data['BB_Tight_Low'], alpha=0.1)
            plt.title(f'{symbol} Tight Channel Bollinger Bands (14, 1.5σ)')
        elif strategy == "wide_channel" and all(col in data.columns for col in ['BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low']):
            # Wide channel Bollinger Bands
            plt.plot(data.index, data['BB_Wide_High'], label='BB Upper (30, 2.5σ)')
            plt.plot(data.index, data['BB_Wide_Mid'], label='BB Middle (30)')
            plt.plot(data.index, data['BB_Wide_Low'], label='BB Lower (30, 2.5σ)')
            plt.fill_between(data.index, data['BB_Wide_High'], data['BB_Wide_Low'], alpha=0.1)
            plt.title(f'{symbol} Wide Channel Bollinger Bands (30, 2.5σ)')
        elif strategy == "volatility":
            # Bollinger Bands
            plt.plot(data.index, data['BB_High'], label='BB Upper')
            plt.plot(data.index, data['BB_Low'], label='BB Lower')
            plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=0.1, color='blue')
            
            plt.title(f'{symbol} Bollinger Bands')
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
        chart2_filename = f"{symbol}_bollinger_{chart_date}.png"
        chart2_path = os.path.join(output_dir, chart2_filename)
        plt.savefig(chart2_path)
        plt.close()
        chart_files.append(chart2_path)
        
        # Plot 3: Ichimoku Cloud chart if selected
        if strategy == "ichimoku" and 'Ichimoku_SpanA' in data.columns and 'Ichimoku_SpanB' in data.columns:
            try:
                plt.figure(figsize=(12, 8))
                
                # 首先确保所有需要的列的索引对齐
                ichimoku_columns = ['Close', 'Ichimoku_Tenkan', 'Ichimoku_Kijun', 'Ichimoku_SpanA', 'Ichimoku_SpanB']
                # 过滤出所有在数据中存在的列
                valid_columns = [col for col in ichimoku_columns if col in data.columns]
                
                # 创建一个临时数据框，包含所有需要的列，确保所有列共享相同的索引
                ichimoku_data = pd.DataFrame({col: data[col] for col in valid_columns})
                
                # 删除包含任何NaN值的行，避免绘图错误
                ichimoku_data = ichimoku_data.dropna(subset=['Ichimoku_SpanA', 'Ichimoku_SpanB'])
                
                # 确保数据不为空
                if len(ichimoku_data) > 0:
                    # Subplot 1: Price with Ichimoku Cloud
                    plt.subplot(2, 1, 1)
                    
                    # 修复一目均衡图绘制，使用更安全的绘图方式，避免索引对齐问题
                    # 使用布尔掩码预先计算比较结果，避免在fill_between中直接比较
                    comparison_mask = ichimoku_data['Ichimoku_SpanA'] >= ichimoku_data['Ichimoku_SpanB']
                    
                    # 为绿色区域绘制(SpanA >= SpanB)
                    plt.fill_between(
                        ichimoku_data.index, 
                        ichimoku_data['Ichimoku_SpanA'].values, 
                        ichimoku_data['Ichimoku_SpanB'].values, 
                        where=comparison_mask.values,  # 使用预计算的布尔掩码
                        color='lightgreen', alpha=0.3
                    )
                    
                    # 为红色区域绘制(SpanA < SpanB) 
                    plt.fill_between(
                        ichimoku_data.index, 
                        ichimoku_data['Ichimoku_SpanA'].values, 
                        ichimoku_data['Ichimoku_SpanB'].values, 
                        where=~comparison_mask.values,  # 使用预计算的布尔掩码的反面
                        color='lightcoral', alpha=0.3
                    )
                    
                    # Plot price and Ichimoku components
                    plt.plot(ichimoku_data.index, ichimoku_data['Close'], label='Close', color='black')
                    plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_Tenkan'], label='Tenkan-sen (9)', color='red')
                    plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_Kijun'], label='Kijun-sen (26)', color='blue')
                    plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_SpanA'], label='Span A', color='green')
                    plt.plot(ichimoku_data.index, ichimoku_data['Ichimoku_SpanB'], label='Span B', color='red', alpha=0.5)
                    
                    # If we have Chikou Span (lagging line), plot it
                    if 'Ichimoku_Chikou' in data.columns:
                        # 确保有数据可用
                        chikou_data = pd.DataFrame({'Ichimoku_Chikou': data['Ichimoku_Chikou']})
                        chikou_valid = chikou_data.dropna()
                        if len(chikou_valid) > 0:
                            plt.plot(chikou_valid.index, chikou_valid['Ichimoku_Chikou'], label='Chikou Span', color='purple')
                    
                    plt.title(f'{symbol} Ichimoku Cloud')
                    plt.legend()
                    plt.grid(True)
                    
                    # Subplot 2: Parabolic SAR and On-Balance Volume
                    plt.subplot(2, 1, 2)
                    
                    # 创建临时DataFrame用于绘制SAR和OBV
                    plot_data = data[['Close']].copy()
                    if 'SAR' in data.columns:
                        plot_data['SAR'] = data['SAR']
                    if 'OBV' in data.columns:
                        plot_data['OBV'] = data['OBV']
                    if 'OBV_MA' in data.columns:
                        plot_data['OBV_MA'] = data['OBV_MA']
                    
                    # 删除有NaN的行
                    plot_data = plot_data.dropna()
                    
                    # Twin axes for price and OBV
                    ax1 = plt.gca()
                    ax2 = ax1.twinx()
                    
                    # Plot price and SAR on primary axis (if SAR exists)
                    ax1.plot(plot_data.index, plot_data['Close'], label='Close', color='black', alpha=0.5)
                    if 'SAR' in plot_data.columns:
                        ax1.scatter(plot_data.index, plot_data['SAR'], label='SAR', marker='.', color='blue', s=15)
                    
                    # Plot OBV and its MA on secondary axis (if they exist)
                    if 'OBV' in plot_data.columns:
                        ax2.plot(plot_data.index, plot_data['OBV'], label='OBV', color='purple', alpha=0.7)
                    if 'OBV_MA' in plot_data.columns:
                        ax2.plot(plot_data.index, plot_data['OBV_MA'], label='OBV MA(20)', color='orange')
                    
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
                    chart3_filename = f"{symbol}_ichimoku_{chart_date}.png"
                    chart3_path = os.path.join(output_dir, chart3_filename)
                    plt.savefig(chart3_path)
                    plt.close()
                    chart_files.append(chart3_path)
            except Exception as e:
                print(f"Error creating Ichimoku chart: {e}")
                # Continue with other charts even if Ichimoku fails
                
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
                
                chart4_filename = f"{symbol}_trend_strategy_{chart_date}.png"
                
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
                
                chart4_filename = f"{symbol}_momentum_strategy_{chart_date}.png"
                
            elif strategy == "volatility":
                # Volatility Trading Combo: Bollinger Bands
                plt.subplot(3, 1, 1)
                plt.plot(data.index, data['Close'], label='Close', color='black')
                plt.plot(data.index, data['BB_High'], label='BB Upper', color='blue')
                plt.plot(data.index, data['BB_Mid'], label='BB Middle', color='blue', linestyle='--')
                plt.plot(data.index, data['BB_Low'], label='BB Lower', color='blue')
                plt.fill_between(data.index, data['BB_High'], data['BB_Low'], alpha=0.1, color='blue')
                plt.title(f'{symbol} - Bollinger Bands(20,2)')
                plt.legend()
                plt.grid(True)
                
                chart4_filename = f"{symbol}_volatility_strategy_{chart_date}.png"
            
            plt.tight_layout()
            chart4_path = os.path.join(output_dir, chart4_filename)
            plt.savefig(chart4_path)
            plt.close()
            chart_files.append(chart4_path)
        
    except Exception as e:
        print(f"Error generating charts: {str(e)}")
        import traceback
        traceback.print_exc()
        # Create a simple error chart as a fallback
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(data.index, data['Close'], 'b-', label='Price')
            plt.title(f"{symbol} Price Chart (Error in full chart generation)")
            plt.grid(True)
            plt.legend()
            
            # Save the fallback chart
            fallback_filename = f"{symbol}_basic_{chart_date}.png"
            fallback_path = os.path.join(output_dir, fallback_filename)
            plt.savefig(fallback_path)
            plt.close()
            chart_files.append(fallback_path)
            print(f"Created fallback chart: {fallback_path}")
        except Exception as fallback_error:
            print(f"Failed to create even fallback chart: {str(fallback_error)}")
    
    finally:
        plt.close('all')  # Close all figures to free memory
    
    print(f"Charts saved to {output_dir}")
    return chart_files

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
        # 临时注释掉可能导致维度问题的代码，直接使用现有数据而不是重建
        
        # 创建subplot
        fig = make_subplots(rows=3, cols=1, 
                         shared_xaxes=True,
                         vertical_spacing=0.05,
                         row_heights=[0.5, 0.25, 0.25],
                         subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'))
        
        # 添加价格和移动平均线到第1行 - 直接使用原始数据列，不重建
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price', line=dict(color='black')), row=1, col=1)
        
        if 'SMA20' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name='SMA20', line=dict(color='blue')), row=1, col=1)
            
        if 'SMA50' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name='SMA50', line=dict(color='orange')), row=1, col=1)
            
        if 'SMA200' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], name='SMA200', line=dict(color='red')), row=1, col=1)
        
        # 添加RSI到第2行
        if 'RSI' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
            
            # 添加RSI的过度买入/卖出线
            fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=70, y1=70,
                       line=dict(color="red", width=2, dash="dash"), row=2, col=1)
            fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=30, y1=30,
                       line=dict(color="green", width=2, dash="dash"), row=2, col=1)
        
        # 添加MACD到第3行
        if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')), row=3, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD_Signal'], name='Signal', line=dict(color='red')), row=3, col=1)
            
            # 绘制MACD直方图
            try:
                # 安全获取MACD直方图值并处理可能的2D数组
                macd_hist_vals = data['MACD_Histogram']
                if hasattr(macd_hist_vals, 'values'):
                    macd_hist_vals = macd_hist_vals.values
                
                # 确保是扁平的1D数组
                macd_hist_vals = np.asarray(macd_hist_vals).flatten()
                
                # 创建自定义颜色
                colors = ['green' if val > 0 else 'red' for val in macd_hist_vals]
                
                fig.add_trace(go.Bar(
                    x=data.index, 
                    y=macd_hist_vals,  # 使用展平后的数据
                    name='Histogram', 
                    marker=dict(color=colors, opacity=0.5)
                ), row=3, col=1)
            except Exception as hist_error:
                print(f"Error plotting MACD histogram: {hist_error}")
                # 继续执行，即使直方图不能绘制
        
        # 更新布局
        fig.update_layout(
            title=f'{symbol} Technical Indicators',
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        # 添加时间范围选择器
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
        
        # 添加Y轴标签
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        # 保存交互式图表
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
        # 直接使用原始数据列，不尝试重建Series
        
        # 创建图表
        fig = go.Figure()
        
        # 添加价格
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Close'], 
            name='Price',
            line=dict(color='black')
        ))
        
        # 添加布林带
        if 'BB_High' in data.columns:
            # 确保数据是一维的
            bb_high_values = np.asarray(data['BB_High']).flatten()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_high_values, 
                name='Upper Band',
                line=dict(color='blue', width=1)
            ))
        
        if 'BB_Mid' in data.columns:
            # 确保数据是一维的
            bb_mid_values = np.asarray(data['BB_Mid']).flatten()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_mid_values, 
                name='Middle Band',
                line=dict(color='blue', width=1, dash='dash')
            ))
        
        if 'BB_Low' in data.columns:
            # 确保数据是一维的
            bb_low_values = np.asarray(data['BB_Low']).flatten()
            # 添加布林带下轨并使用填充区域
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=bb_low_values, 
                name='Lower Band',
                line=dict(color='blue', width=1),
                fill='tonexty',  # 填充到前一个trace
                fillcolor='rgba(0, 0, 255, 0.1)'
            ))
        
        # 更新布局
        fig.update_layout(
            title=f'{symbol} Bollinger Bands',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        # 添加时间范围选择器
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
        
        # 保存交互式图表
        filepath = os.path.join(output_dir, f"{symbol}_interactive_bollinger_{chart_date}.html")
        fig.write_html(filepath)
        print(f"Interactive Bollinger chart saved to {filepath}")
        
        return filepath
    
    except Exception as e:
        print(f"Error creating interactive Bollinger chart: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 即使出错，也尝试创建一个简单的价格图表作为备用
        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data['Close'], 
                name='Price',
                line=dict(color='black')
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
