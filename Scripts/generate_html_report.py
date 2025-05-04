#!/usr/bin/env python
"""
Generate Interactive HTML Reports
--------------------------------
Creates interactive HTML reports with technical analysis indicators
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import jinja2
import json

# Import core functions
from calculate_indicators import calculate_indicators

def generate_interactive_report(df, symbol, output_dir, report_date=None, parameter_set='default', language='en', standalone=False):
    """
    Generate an interactive HTML report with technical indicators
    
    Args:
        df (pandas.DataFrame): DataFrame with calculated indicators
        symbol (str): Symbol being analyzed
        output_dir (str): Directory to save the report
        report_date (str): Report date in YYYYMMDD format
        parameter_set (str): Parameter set used for the indicators
        language (str): Report language (en/zh)
        standalone (bool): If True, includes X-Frame-Options header to prevent embedding in iframes
        
    Returns:
        str: Path to the generated HTML report
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the latest data point
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Format the date for the filename
    if report_date:
        current_date = report_date
    else:
        current_date = pd.Timestamp.now().strftime("%Y%m%d")
    
    # Load translations
    translations = get_translations(language)
    
    # Create plotly figures
    price_ma_fig = create_price_ma_chart(df, symbol, parameter_set, translations)
    oscillators_fig = create_oscillators_chart(df, symbol, translations)
    volatility_fig = create_volatility_chart(df, symbol, parameter_set, translations)
    
    # Convert figures to HTML
    price_ma_chart = price_ma_fig.to_html(full_html=False, include_plotlyjs='cdn')
    oscillators_chart = oscillators_fig.to_html(full_html=False, include_plotlyjs='cdn')
    volatility_chart = volatility_fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Prepare indicator readings
    indicator_readings = prepare_indicator_readings(df, latest, prev, translations)
    
    # Prepare strategy signals
    strategy_signals = prepare_strategy_signals(df, latest, translations)
    
    # Create the report using Jinja2 template
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Templates')
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('interactive_report_template.html')
    
    output = template.render(
        symbol=symbol,
        current_date=current_date,
        parameter_set=parameter_set,
        translations=translations,
        price_ma_chart=price_ma_chart,
        oscillators_chart=oscillators_chart,
        volatility_chart=volatility_chart,
        indicator_readings=indicator_readings,
        strategy_signals=strategy_signals,
        standalone=standalone
    )
    
    # Save the report
    filename = f"{symbol}_interactive_report_{current_date}_{parameter_set}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Interactive report saved to {filepath}")
    return filepath

def get_translations(language='en'):
    """
    Get translations for the specified language from JSON files in the locales directory
    """
    # Find the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    locales_dir = os.path.join(project_dir, "locales")
    
    # Default fallback translations
    default_translations = {
        'en': {
            'title': 'Technical Analysis Report',
            'date': 'Date',
            'price_data': 'Price Data',
            # ... (remainder of English translations as fallback)
        }
    }
    
    # Try to load from JSON file
    try:
        locale_file = os.path.join(locales_dir, f"{language}.json")
        if os.path.exists(locale_file):
            with open(locale_file, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        else:
            print(f"Warning: Translation file for '{language}' not found at {locale_file}")
            # Try to load English as fallback
            en_file = os.path.join(locales_dir, "en.json")
            if language != 'en' and os.path.exists(en_file):
                with open(en_file, 'r', encoding='utf-8') as f:
                    return json.loads(f.read())
            
            # Use hardcoded fallback
            return default_translations.get(language, default_translations['en'])
    except Exception as e:
        print(f"Error loading translation file: {e}")
        return default_translations.get(language, default_translations['en'])

def create_price_ma_chart(df, symbol, parameter_set, translations):
    """
    Create price and moving averages interactive chart
    """
    fig = go.Figure()
    
    # Add price as candlestick if OHLC is available, otherwise as line
    if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price'
        ))
    
    # Define moving averages to plot based on parameter set
    if parameter_set == 'short_term':
        ma_columns = ['SMA9', 'SMA21', 'EMA12', 'EMA26']
    elif parameter_set == 'medium_term':
        ma_columns = ['SMA50', 'SMA200', 'EMA50', 'EMA200']
    elif parameter_set == 'trend_following':
        ma_columns = ['SMA50', 'SMA200', 'EMA12', 'EMA26']
    else:
        ma_columns = ['SMA20', 'SMA50', 'SMA200']
    
    # Add moving averages
    for ma in ma_columns:
        if ma in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[ma],
                mode='lines',
                name=ma,
                line=dict(width=1)
            ))
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} - {translations['price_ma_chart']}",
        xaxis_title=translations['date'],
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        legend_title=translations['moving_averages'],
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_oscillators_chart(df, symbol, translations):
    """
    Create interactive oscillators chart
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('RSI', 'MACD', 'Stochastic'),
        row_heights=[0.33, 0.33, 0.34]
    )
    
    # Add RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI(14)',
            line=dict(color='purple')
        ), row=1, col=1)
        
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash='dash', line_color='red', row=1, col=1,
                     annotation_text=translations['overbought'])
        fig.add_hline(y=30, line_dash='dash', line_color='green', row=1, col=1,
                     annotation_text=translations['oversold'])
    
    # Add MACD
    if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='red')
        ), row=2, col=1)
        
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors
        ), row=2, col=1)
    
    # Add Stochastic
    if all(col in df.columns for col in ['STOCH_K', 'STOCH_D']):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['STOCH_K'],
            mode='lines',
            name='%K',
            line=dict(color='blue')
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['STOCH_D'],
            mode='lines',
            name='%D',
            line=dict(color='red')
        ), row=3, col=1)
        
        # Add overbought/oversold lines
        fig.add_hline(y=80, line_dash='dash', line_color='red', row=3, col=1)
        fig.add_hline(y=20, line_dash='dash', line_color='green', row=3, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} - {translations['oscillators_chart']}",
        xaxis3_title=translations['date'],
        height=700,
        margin=dict(l=50, r=50, t=80, b=50),
        legend_title=translations['oscillators'],
        hovermode='x unified'
    )
    
    return fig

def create_volatility_chart(df, symbol, parameter_set, translations):
    """
    Create interactive volatility chart
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Bollinger Bands', 'ATR'),
        row_heights=[0.7, 0.3]
    )
    
    # Determine which Bollinger Bands to use
    if parameter_set == 'tight_channel':
        bb_cols = ['BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low']
    elif parameter_set == 'wide_channel':
        bb_cols = ['BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low']
    else:
        bb_cols = ['BB_High', 'BB_Mid', 'BB_Low']
    
    # Add price
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close',
        line=dict(color='black')
    ), row=1, col=1)
    
    # Add Bollinger Bands
    if all(col in df.columns for col in bb_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[bb_cols[0]],
            mode='lines',
            name='Upper Band',
            line=dict(color='red', width=1)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[bb_cols[1]],
            mode='lines',
            name='Middle Band',
            line=dict(color='orange', width=1, dash='dash')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[bb_cols[2]],
            mode='lines',
            name='Lower Band',
            line=dict(color='green', width=1),
            fill='tonexty',
            fillcolor='rgba(0, 250, 0, 0.1)'
        ), row=1, col=1)
    
    # Add Keltner Channels if available
    if all(col in df.columns for col in ['Keltner_High', 'Keltner_Mid', 'Keltner_Low']):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Keltner_High'],
            mode='lines',
            name='Keltner Upper',
            line=dict(color='blue', width=1, dash='dash')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Keltner_Low'],
            mode='lines',
            name='Keltner Lower',
            line=dict(color='blue', width=1, dash='dash')
        ), row=1, col=1)
        
        # Add squeeze points if available
        if 'BB_Squeeze' in df.columns:
            squeeze_indices = df.index[df['BB_Squeeze'] == 1]
            if len(squeeze_indices) > 0:
                fig.add_trace(go.Scatter(
                    x=squeeze_indices,
                    y=df.loc[squeeze_indices, 'Close'],
                    mode='markers',
                    name='Squeeze',
                    marker=dict(color='red', size=8, symbol='triangle-up')
                ), row=1, col=1)
    
    # Add ATR
    if 'ATR' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['ATR'],
            mode='lines',
            name='ATR(14)',
            line=dict(color='purple')
        ), row=2, col=1)
        
        # Add ATR Percentage if available
        if 'ATR_Percent' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['ATR_Percent'],
                mode='lines',
                name='ATR %',
                line=dict(color='orange')
            ), row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} - {translations['volatility_chart']}",
        xaxis2_title=translations['date'],
        height=700,
        margin=dict(l=50, r=50, t=80, b=50),
        legend_title=translations['volatility'],
        hovermode='x unified'
    )
    
    return fig

def prepare_indicator_readings(df, latest, prev, translations):
    """
    Prepare indicator readings for the report
    """
    readings = {
        'price_data': {
            'title': translations['price_data'],
            'data_points': [  # Changed 'items' to 'data_points' to avoid conflict
                {'name': translations['last_close'], 'value': f"{latest['Close']:.4f}"},
                {'name': translations['prev_close'], 'value': f"{prev['Close']:.4f}"},
                {'name': translations['change'], 'value': f"{(latest['Close'] - prev['Close']):.4f} ({(latest['Close'] / prev['Close'] - 1) * 100:.2f}%)"}
            ]
        },
        'moving_averages': {
            'title': translations['moving_averages'],
            'data_points': []  # Changed 'items' to 'data_points'
        },
        'oscillators': {
            'title': translations['oscillators'],
            'data_points': []  # Changed 'items' to 'data_points'
        },
        'volatility': {
            'title': translations['volatility'],
            'data_points': []  # Changed 'items' to 'data_points'
        },
        'trend': {
            'title': translations['trend'],
            'data_points': []  # Changed 'items' to 'data_points'
        }
    }
    
    # Add moving averages
    ma_cols = ['SMA20', 'SMA50', 'SMA200', 'EMA20', 'EMA50', 'EMA200']
    for col in ma_cols:
        if col in latest:
            readings['moving_averages']['data_points'].append({  # Changed 'items' to 'data_points'
                'name': col,
                'value': f"{latest[col]:.4f}"
            })
    
    # Add oscillators
    if 'RSI' in latest:
        readings['oscillators']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'RSI(14)',
            'value': f"{latest['RSI']:.2f}"
        })
    
    if all(col in latest for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        readings['oscillators']['data_points'].extend([  # Changed 'items' to 'data_points'
            {'name': 'MACD', 'value': f"{latest['MACD']:.4f}"},
            {'name': 'MACD Signal', 'value': f"{latest['MACD_Signal']:.4f}"},
            {'name': 'MACD Histogram', 'value': f"{latest['MACD_Histogram']:.4f}"}
        ])
    
    if all(col in latest for col in ['STOCH_K', 'STOCH_D']):
        readings['oscillators']['data_points'].extend([  # Changed 'items' to 'data_points'
            {'name': 'Stochastic %K', 'value': f"{latest['STOCH_K']:.2f}"},
            {'name': 'Stochastic %D', 'value': f"{latest['STOCH_D']:.2f}"}
        ])
    
    # Add volatility indicators
    if all(col in latest for col in ['BB_High', 'BB_Mid', 'BB_Low']):
        readings['volatility']['data_points'].extend([  # Changed 'items' to 'data_points'
            {'name': 'Bollinger High', 'value': f"{latest['BB_High']:.4f}"},
            {'name': 'Bollinger Mid', 'value': f"{latest['BB_Mid']:.4f}"},
            {'name': 'Bollinger Low', 'value': f"{latest['BB_Low']:.4f}"}
        ])
    
    if 'ATR' in latest:
        readings['volatility']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'ATR(14)',
            'value': f"{latest['ATR']:.4f}"
        })
    
    if 'BB_Width' in latest:
        readings['volatility']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'Bollinger Width',
            'value': f"{latest['BB_Width']:.4f}"
        })
    
    if 'ATR_Percent' in latest:
        readings['volatility']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'ATR %',
            'value': f"{latest['ATR_Percent']:.2f}%"
        })
    
    # Add trend indicators
    if 'ADX' in latest:
        readings['trend']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'ADX(14)',
            'value': f"{latest['ADX']:.2f}"
        })
    
    if 'SAR' in latest:
        readings['trend']['data_points'].append({  # Changed 'items' to 'data_points'
            'name': 'Parabolic SAR',
            'value': f"{latest['SAR']:.4f}"
        })
    
    return readings

def prepare_strategy_signals(df, latest, translations):
    """
    Prepare strategy signals for the report
    """
    signals = {}
    
    # Traditional trend analysis
    signals['traditional_trend'] = {
        'title': translations['traditional_trend'],
        'signals': []
    }
    
    # Short-term trend
    short_term_signal = ''
    if latest['Close'] > latest['SMA20'] and latest['SMA20'] > latest['SMA50']:
        short_term_signal = translations['bullish']
    elif latest['Close'] < latest['SMA20'] and latest['SMA20'] < latest['SMA50']:
        short_term_signal = translations['bearish']
    else:
        short_term_signal = translations['neutral']
    
    signals['traditional_trend']['signals'].append({
        'name': translations['short_term_trend'],
        'value': short_term_signal
    })
    
    # Long-term trend
    long_term_signal = ''
    if latest['SMA50'] > latest['SMA150']:
        long_term_signal = translations['bullish']
    elif latest['SMA50'] < latest['SMA150']:
        long_term_signal = translations['bearish']
    else:
        long_term_signal = translations['neutral']
    
    signals['traditional_trend']['signals'].append({
        'name': translations['long_term_trend'],
        'value': long_term_signal
    })
    
    # Trend following strategy
    if all(col in latest for col in ['SMA_Cross_Signal', 'EMA_Cross_Signal', 'ADX', 'Trend_Strength']):
        sma_signal = translations['bullish'] if latest['SMA_Cross_Signal'] == 1 else translations['bearish']
        ema_signal = translations['bullish'] if latest['EMA_Cross_Signal'] == 1 else translations['bearish']
        
        overall_signal = ''
        if latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == 1 and latest['ADX'] > 25:
            overall_signal = translations['strong_bullish']
        elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == -1 and latest['ADX'] > 25:
            overall_signal = translations['strong_bearish']
        elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == 1:
            overall_signal = translations['bullish']
        elif latest['SMA_Cross_Signal'] == latest['EMA_Cross_Signal'] == -1:
            overall_signal = translations['bearish']
        else:
            overall_signal = translations['neutral']
        
        signals['trend_following'] = {
            'title': translations['trend_following'],
            'signals': [
                {'name': 'SMA(50,200)', 'value': sma_signal},
                {'name': 'EMA(12,26)', 'value': ema_signal},
                {'name': 'ADX(14)', 'value': f"{latest['ADX']:.2f} ({latest['Trend_Strength']})"},
                {'name': 'Overall', 'value': overall_signal}
            ]
        }
    
    # Momentum strategy
    if all(col in latest for col in ['RSI_Signal', 'MACD_Cross_Signal', 'Stoch_Signal', 'Momentum_Score']):
        rsi_signal = translations['bullish'] if latest['RSI_Signal'] == 1 else (
            translations['bearish'] if latest['RSI_Signal'] == -1 else translations['neutral']
        )
        
        macd_signal = translations['bullish'] if latest['MACD_Cross_Signal'] == 1 else translations['bearish']
        
        stoch_signal = translations['bullish'] if latest['Stoch_Signal'] == 1 else (
            translations['bearish'] if latest['Stoch_Signal'] == -1 else translations['neutral']
        )
        
        overall_signal = ''
        if latest['Momentum_Score'] >= 2:
            overall_signal = translations['strong_bullish']
        elif latest['Momentum_Score'] <= -2:
            overall_signal = translations['strong_bearish']
        elif latest['Momentum_Score'] > 0:
            overall_signal = translations['bullish']
        elif latest['Momentum_Score'] < 0:
            overall_signal = translations['bearish']
        else:
            overall_signal = translations['neutral']
        
        signals['momentum'] = {
            'title': translations['momentum'],
            'signals': [
                {'name': 'RSI(14)', 'value': rsi_signal},
                {'name': 'MACD', 'value': macd_signal},
                {'name': 'Stochastic', 'value': stoch_signal},
                {'name': 'Momentum Score', 'value': f"{int(latest['Momentum_Score'])} ({overall_signal})"}
            ]
        }
    
    # Volatility strategy
    if all(col in latest for col in ['BB_Squeeze', 'BB_Width', 'ATR_Percent']):
        squeeze_status = 'Yes' if latest['BB_Squeeze'] == 1 else 'No'
        
        volatility_status = ''
        if latest['BB_Squeeze'] == 1:
            volatility_status = 'LOW - Potential breakout setup'
        elif latest['ATR_Percent'] > 2.0:
            volatility_status = 'HIGH - Trending market'
        else:
            volatility_status = 'NORMAL'
        
        signals['volatility_strategy'] = {
            'title': translations['volatility_strategy'],
            'signals': [
                {'name': 'BB Squeeze', 'value': squeeze_status},
                {'name': 'BB Width', 'value': f"{latest['BB_Width']:.4f}"},
                {'name': 'ATR %', 'value': f"{latest['ATR_Percent']:.2f}%"},
                {'name': 'Volatility Status', 'value': volatility_status}
            ]
        }
    
    # Ichimoku strategy
    if all(col in latest for col in ['Cloud_Direction', 'SAR_Signal', 'OBV_Signal']):
        cloud_dir = translations['bullish'] if latest['Cloud_Direction'] == 1 else (
            translations['bearish'] if latest['Cloud_Direction'] == -1 else translations['neutral']
        )
        
        sar_signal = translations['bullish'] if latest['SAR_Signal'] == 1 else translations['bearish']
        
        obv_signal = translations['bullish'] if latest['OBV_Signal'] == 1 else translations['bearish']
        
        # Calculate overall score
        score = (1 if latest['Cloud_Direction'] == 1 else (-1 if latest['Cloud_Direction'] == -1 else 0)) + \
                latest['SAR_Signal'] + latest['OBV_Signal']
        
        overall_signal = ''
        if score >= 2:
            overall_signal = translations['strong_bullish']
        elif score <= -2:
            overall_signal = translations['strong_bearish']
        elif score > 0:
            overall_signal = translations['bullish']
        elif score < 0:
            overall_signal = translations['bearish']
        else:
            overall_signal = translations['neutral']
        
        signals['ichimoku'] = {
            'title': translations['ichimoku'],
            'signals': [
                {'name': 'Ichimoku Cloud', 'value': cloud_dir},
                {'name': 'Parabolic SAR', 'value': sar_signal},
                {'name': 'On-Balance Volume', 'value': obv_signal},
                {'name': 'Overall', 'value': overall_signal}
            ]
        }
    
    return signals

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate interactive HTML report")
    parser.add_argument("file", help="Path to the CSV or Excel file with market data")
    parser.add_argument("--symbol", help="Symbol name for the report", required=True)
    parser.add_argument("--output", default=None, help="Directory to save the report")
    parser.add_argument("--parameter_set", default="default", 
                       choices=["default", "short_term", "medium_term", "high_freq", 
                                "tight_channel", "wide_channel", "trend_following", 
                                "momentum", "volatility", "ichimoku"],
                       help="Trading strategy parameter set")
    parser.add_argument("--language", default="en", choices=["en", "zh"], help="Report language")
    parser.add_argument("--date", default=None, help="Report date in YYYYMMDD format")
    parser.add_argument("--standalone", action="store_true", help="Generate standalone report")
    
    args = parser.parse_args()
    
    # Load data
    from calculate_indicators import load_data, calculate_indicators
    
    data = load_data(args.file)
    data_with_indicators = calculate_indicators(data, parameter_set=args.parameter_set)
    
    # Get default output directory
    if args.output is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        output_dir = os.path.join(project_dir, "Reports")
    else:
        output_dir = args.output
    
    # Generate report
    report_path = generate_interactive_report(
        data_with_indicators, 
        args.symbol, 
        output_dir, 
        report_date=args.date, 
        parameter_set=args.parameter_set,
        language=args.language,
        standalone=args.standalone
    )
    
    print(f"Report generated: {report_path}")
