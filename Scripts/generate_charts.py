import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt # Keep for old functions if needed elsewhere, though not called directly now
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from calculate_indicators import calculate_indicators # Assuming this function exists and is correctly imported

# --- New Plotly Interactive Chart Functions ---

def plot_interactive_indicators(data, symbol, output_dir, chart_date=None, suffix=''):
    """
    Generate interactive plots of key indicators using Plotly.

    Args:
        data (pandas.DataFrame): Data with indicators. Must include OHLC if using Candlestick.
        symbol (str): Symbol being analyzed.
        output_dir (str): Directory to save the charts.
        chart_date (str): Date in YYYYMMDD format for the chart filename.
        suffix (str): Optional suffix for the filename (e.g., '_short_term').

    Returns:
        str: Path to the generated interactive chart HTML file, or None if error.
    """
    os.makedirs(output_dir, exist_ok=True)
    if chart_date:
        current_date = chart_date
    else:
        current_date = pd.Timestamp.now().strftime("%Y%m%d")

    chart_path = None
    try:
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Price / MAs', 'RSI', 'MACD'),
            row_heights=[0.6, 0.2, 0.2]
        )

        # Subplot 1: Price and Moving Averages
        if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
            fig.add_trace(go.Candlestick(x=data.index,
                                        open=data['Open'], high=data['High'],
                                        low=data['Low'], close=data['Close'],
                                        name='Price'), row=1, col=1)
        elif 'Close' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines',
                                    name='Close Price'), row=1, col=1)

        # Add MAs dynamically based on suffix or default
        ma_columns_to_plot = []
        if suffix == '_short_term':
             ma_columns_to_plot = ['SMA9', 'SMA21', 'EMA12', 'EMA26']
        elif suffix == '_medium_term':
             ma_columns_to_plot = ['SMA50', 'SMA200', 'EMA50', 'EMA200']
        else: # Default or other suffixes
             ma_columns_to_plot = ['SMA20', 'SMA50', 'SMA200'] # Default MAs

        for ma in ma_columns_to_plot:
             if ma in data.columns:
                 fig.add_trace(go.Scatter(x=data.index, y=data[ma], mode='lines',
                                         name=ma, line=dict(width=1)), row=1, col=1)


        # Subplot 2: RSI
        rsi_col = 'RSI7' if suffix == '_high_freq' else 'RSI'
        if rsi_col in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[rsi_col], mode='lines',
                                    name=rsi_col, line=dict(color='green')), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="blue", row=2, col=1)

        # Subplot 3: MACD
        macd_cols = ['MACD_HF', 'MACD_HF_Signal', 'MACD_HF_Histogram'] if suffix == '_high_freq' else ['MACD', 'MACD_Signal', 'MACD_Histogram']
        if all(col in data.columns for col in macd_cols):
            fig.add_trace(go.Scatter(x=data.index, y=data[macd_cols[0]], mode='lines',
                                    name=macd_cols[0], line=dict(color='blue')), row=3, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data[macd_cols[1]], mode='lines',
                                    name=macd_cols[1], line=dict(color='red')), row=3, col=1)
            colors = ['green' if val >= 0 else 'red' for val in data[macd_cols[2]]]
            fig.add_trace(go.Bar(x=data.index, y=data[macd_cols[2]], name=macd_cols[2],
                                marker_color=colors), row=3, col=1)

        # Update layout
        title_suffix = f' ({suffix.replace("_", " ").strip()})' if suffix else ''
        fig.update_layout(
            title_text=f'{symbol} Interactive Technical Indicators{title_suffix} ({current_date})',
            height=800,
            xaxis_rangeslider_visible=False,
            legend_title_text='Indicators',
            hovermode='x unified'
        )
        fig.update_xaxes(showticklabels=False, row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=True, title_text='Date', row=3, col=1)

        # Save chart
        chart_filename = f"{symbol}_interactive_indicators_{current_date}{suffix}.html"
        chart_path = os.path.join(output_dir, chart_filename)
        fig.write_html(chart_path)
        print(f"Interactive indicators chart saved to {chart_path}")

    except Exception as e:
        print(f"Error generating interactive indicator chart for {symbol}{suffix}: {e}")
        chart_path = None # Ensure None is returned on error

    return chart_path


def plot_interactive_bollinger(data, symbol, output_dir, chart_date=None, suffix=''):
    """
    Generate interactive Bollinger Bands plot using Plotly.

    Args:
        data (pandas.DataFrame): Data with Bollinger Bands.
        symbol (str): Symbol being analyzed.
        output_dir (str): Directory to save the chart.
        chart_date (str): Date in YYYYMMDD format for the chart filename.
        suffix (str): Optional suffix for the filename (e.g., '_tight_channel').

    Returns:
        str: Path to the generated interactive chart HTML file, or None if error.
    """
    os.makedirs(output_dir, exist_ok=True)
    if chart_date:
        current_date = chart_date
    else:
        current_date = pd.Timestamp.now().strftime("%Y%m%d")

    chart_path = None
    try:
        # Determine BB columns based on suffix
        if suffix == '_tight_channel':
            bb_cols = ['BB_Tight_Mid', 'BB_Tight_High', 'BB_Tight_Low']
        elif suffix == '_wide_channel':
            bb_cols = ['BB_Wide_Mid', 'BB_Wide_High', 'BB_Wide_Low']
        else:
            bb_cols = ['BB_Mid', 'BB_High', 'BB_Low'] # Default

        if all(col in data.columns for col in bb_cols) and 'Close' in data.columns:
            fig_bb = go.Figure()
            # Price line
            fig_bb.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
            # Bollinger Bands
            fig_bb.add_trace(go.Scatter(x=data.index, y=data[bb_cols[1]], mode='lines', name='Upper Band', line=dict(width=0.5, color='red'))) # Show lines slightly
            fig_bb.add_trace(go.Scatter(x=data.index, y=data[bb_cols[2]], mode='lines', name='Lower Band', line=dict(width=0.5, color='green'),
                                       fill='tonexty', fillcolor='rgba(211, 211, 211, 0.3)')) # Fill to upper band
            fig_bb.add_trace(go.Scatter(x=data.index, y=data[bb_cols[0]], mode='lines', name='Middle Band', line=dict(color='orange', dash='dash')))

            title_suffix = f' ({suffix.replace("_", " ").strip()})' if suffix else ''
            fig_bb.update_layout(
                title_text=f'{symbol} Interactive Bollinger Bands{title_suffix} ({current_date})',
                height=500,
                xaxis_title='Date',
                yaxis_title='Price',
                legend_title_text='Bollinger Bands',
                hovermode='x unified'
            )

            # Save chart
            chart_bb_filename = f"{symbol}_interactive_bollinger_{current_date}{suffix}.html"
            chart_path = os.path.join(output_dir, chart_bb_filename)
            fig_bb.write_html(chart_path)
            print(f"Interactive Bollinger chart saved to {chart_path}")
        else:
             print(f"Skipping Bollinger chart for {symbol}{suffix}: Missing required columns.")
             chart_path = None

    except Exception as e:
        print(f"Error generating interactive Bollinger Bands chart for {symbol}{suffix}: {e}")
        chart_path = None # Ensure None is returned on error

    return chart_path


# --- Modified Function to Call Plotly AND Return Indicator DataFrame ---

def generate_parameter_set_charts(symbol, data, output_dir, parameter_sets=None):
    """
    Generate INTERACTIVE charts for different parameter sets using Plotly
    AND return the DataFrame with indicators for the first parameter set.

    Args:
        symbol (str): Symbol name (e.g., 'EURUSD')
        data (pandas.DataFrame): Base price data (OHLCV). Indicators are calculated inside.
        output_dir (str): Directory to save charts.
        parameter_sets (list): List of parameter sets to generate charts for.

    Returns:
        tuple: (dict of generated file paths, pandas.DataFrame with indicators for the first param_set or None)
    """
    if parameter_sets is None:
        parameter_sets = ['default']

    today = datetime.now().strftime('%Y%m%d')
    generated_files = {'indicators': [], 'bollinger': []}
    first_df_indicators = None # To store the first calculated dataframe

    for i, param_set in enumerate(parameter_sets): # Added index i
        print(f"\nGenerating interactive charts for {symbol} with parameter set: {param_set}")
        # Calculate indicators with specific parameter set
        df_indicators = calculate_indicators(data.copy(), parameter_set=param_set) # Use copy

        # Store the first calculated DataFrame (usually 'default')
        if i == 0:
            first_df_indicators = df_indicators

        param_suffix = f"_{param_set}" if param_set != 'default' else ''

        # Generate Bollinger Bands chart using Plotly
        bb_chart_path = plot_interactive_bollinger(df_indicators, symbol, output_dir, today,
                                                   suffix=param_suffix)
        if bb_chart_path:
            generated_files['bollinger'].append(bb_chart_path)

        # Generate other indicators chart using Plotly
        ind_chart_path = plot_interactive_indicators(df_indicators, symbol, output_dir, today,
                                                     suffix=param_suffix)
        if ind_chart_path:
            generated_files['indicators'].append(ind_chart_path)

    # Return both the generated file paths and the first indicator DataFrame
    return generated_files, first_df_indicators


# --- Original Matplotlib Functions (kept for reference or potential other uses) ---

def plot_bollinger_bands(data, symbol, output_dir, date_str=None, suffix='',
                        bb_columns=None):
    """
    Plot price with Bollinger Bands using Matplotlib.
    (Note: This function is no longer called by generate_parameter_set_charts)
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')

    if bb_columns is None:
        bb_columns = ['BB_Mid', 'BB_High', 'BB_Low']

    if not all(col in data.columns for col in bb_columns + ['Close']):
        print(f"Skipping Matplotlib Bollinger chart for {symbol}{suffix}: Missing required columns.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['Close'], label='Close Price', color='blue')
    ax.plot(data.index, data[bb_columns[0]], label='Middle Band', color='orange')
    ax.plot(data.index, data[bb_columns[1]], label='Upper Band', color='red')
    ax.plot(data.index, data[bb_columns[2]], label='Lower Band', color='green')
    ax.fill_between(data.index, data[bb_columns[1]], data[bb_columns[2]],
                    alpha=0.1, color='gray')

    title_suffix = f' ({suffix.replace("_", " ").strip()})' if suffix else ''
    ax.set_title(f'{symbol} Price with Bollinger Bands{title_suffix} (Matplotlib)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate()

    filename = f"{symbol}_matplotlib_bollinger_{date_str}{suffix}.png" # Changed filename to avoid overwrite
    try:
        fig.savefig(os.path.join(output_dir, filename))
        print(f"Matplotlib Bollinger chart saved to {filename}")
    except Exception as e:
        print(f"Error saving Matplotlib Bollinger chart: {e}")
    plt.close(fig)


def plot_indicators(data, symbol, output_dir, date_str=None, suffix='',
                  ma_columns=None, rsi_column='RSI',
                  macd_columns=None):
    """
    Plot technical indicators using Matplotlib.
    (Note: This function is no longer called by generate_parameter_set_charts)
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')

    # Define default columns if not provided
    if ma_columns is None: ma_columns = ['SMA20', 'SMA50', 'SMA200']
    if macd_columns is None: macd_columns = ['MACD', 'MACD_Signal', 'MACD_Histogram']

    # Check if necessary columns exist
    required_cols = ['Close', rsi_column] + ma_columns + macd_columns
    if not all(col in data.columns for col in required_cols):
         print(f"Skipping Matplotlib indicators chart for {symbol}{suffix}: Missing required columns.")
         missing = [col for col in required_cols if col not in data.columns]
         print(f"Missing: {missing}")
         return

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [3, 1, 1]})

    # Plot Price and MAs
    ax1.plot(data.index, data['Close'], label='Close Price')
    for ma in ma_columns:
        if ma in data.columns: # Double check just in case
            ax1.plot(data.index, data[ma], label=ma)
    title_suffix = f' ({suffix.replace("_", " ").strip()})' if suffix else ''
    ax1.set_title(f'{symbol} with Technical Indicators{title_suffix} (Matplotlib)')
    ax1.set_ylabel('Price')
    ax1.grid(True)
    ax1.legend()

    # Plot RSI
    ax2.plot(data.index, data[rsi_column], color='purple')
    ax2.axhline(y=70, color='r', linestyle='--')
    ax2.axhline(y=30, color='g', linestyle='--')
    ax2.set_ylabel(rsi_column)
    ax2.grid(True)

    # Plot MACD
    ax3.plot(data.index, data[macd_columns[0]], label=macd_columns[0])
    ax3.plot(data.index, data[macd_columns[1]], label=macd_columns[1])
    ax3.bar(data.index, data[macd_columns[2]], label=macd_columns[2], alpha=0.5)
    ax3.set_ylabel('MACD')
    ax3.grid(True)
    ax3.legend()

    ax3.set_xlabel('Date')
    fig.autofmt_xdate()

    filename = f"{symbol}_matplotlib_indicators_{date_str}{suffix}.png" # Changed filename
    try:
        fig.savefig(os.path.join(output_dir, filename))
        print(f"Matplotlib indicators chart saved to {filename}")
    except Exception as e:
        print(f"Error saving Matplotlib indicators chart: {e}")
    plt.close(fig)
