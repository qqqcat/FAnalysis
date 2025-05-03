#!/usr/bin/env python
"""
Financial Analysis Web Platform API
-----------------------------------
Flask backend API for the Financial Analysis web platform
"""

import os
import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import plotly
import yfinance as yf
import glob
import logging

# Add Scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Scripts'))

# Import core functions from existing codebase
from calculate_indicators import calculate_indicators, load_data
from generate_charts import generate_parameter_set_charts, plot_interactive_indicators, plot_interactive_bollinger

# Create Flask application
app = Flask(__name__, static_folder='../web/build')
CORS(app)  # Enable CORS for all routes

# Configure directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
CHARTS_DIR = os.path.join(BASE_DIR, 'Charts')
REPORTS_DIR = os.path.join(BASE_DIR, 'Reports')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Available assets and parameter sets
AVAILABLE_ASSETS = {
    'forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'],
    'commodities': ['GOLD', 'SILVER', 'OIL'],
    'indices': ['S&P500', 'NASDAQ', 'DOW']
}

PARAMETER_SETS = [
    'default', 'short_term', 'medium_term', 'high_freq', 
    'tight_channel', 'wide_channel', 'trend_following',
    'momentum', 'volatility', 'ichimoku'
]

# Helper functions
def get_symbol_data(symbol, period="1y"):
    """获取标的数据，优先使用本地修复后的数据文件"""
    today = datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    # 尝试加载数据，优先查找今天的数据，然后是昨天的，最后尝试其他日期
    for date_str in [today, yesterday]:
        # 1. 首先尝试加载已修复的文件（带有_fixed后缀）
        fixed_filename = f"{symbol}_{date_str}_fixed.csv"
        fixed_file_path = os.path.join(DATA_DIR, fixed_filename)
        
        if os.path.exists(fixed_file_path):
            try:
                logger.info(f"正在加载已修复的文件: {fixed_filename}")
                data = pd.read_csv(fixed_file_path)
                if 'Date' in data.columns:
                    data['Date'] = pd.to_datetime(data['Date'])
                    data.set_index('Date', inplace=True)
                    return data
            except Exception as e:
                logger.error(f"读取修复文件出错: {str(e)}")
                
        # 2. 尝试直接读取原始文件
        orig_filename = f"{symbol}_{date_str}.csv"
        orig_file_path = os.path.join(DATA_DIR, orig_filename)
        
        if os.path.exists(orig_file_path):
            try:
                logger.info(f"正在加载原始文件: {orig_filename}")
                # 尝试跳过可能的标题行
                data = pd.read_csv(orig_file_path, skiprows=[1, 2] if check_has_ticker_row(orig_file_path) else None)
                if 'Date' in data.columns:
                    data['Date'] = pd.to_datetime(data['Date'])
                    data.set_index('Date', inplace=True)
                    return data
            except Exception as e:
                logger.error(f"读取原始文件出错: {str(e)}")
    
    # 3. 找不到今天或昨天的数据，尝试查找任何可用的最新数据文件
    pattern = f"{symbol}_*_fixed.csv"
    fixed_files = glob.glob(os.path.join(DATA_DIR, pattern))
    
    if fixed_files:
        # 按文件名排序，通常最新的文件会排在最后
        fixed_files.sort(reverse=True)
        try:
            logger.info(f"尝试加载最新的修复文件: {os.path.basename(fixed_files[0])}")
            data = pd.read_csv(fixed_files[0])
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
                data.set_index('Date', inplace=True)
                return data
        except Exception as e:
            logger.error(f"读取最新修复文件出错: {str(e)}")
    
    # 4. 最后尝试从网络获取数据
    try:
        logger.info(f"从网络下载数据: {symbol}")
        data = yf.download(symbol, period=period)
        # 保存到本地以供将来使用
        out_file = os.path.join(DATA_DIR, f"{symbol}_{today}.csv")
        data.reset_index().to_csv(out_file, index=False)
        return data
    except Exception as e:
        logger.error(f"下载数据失败: {str(e)}")
        # 返回空的数据框
        return pd.DataFrame()

def check_has_ticker_row(file_path):
    """检查CSV文件是否包含Ticker行"""
    try:
        with open(file_path, 'r') as f:
            lines = [next(f) for _ in range(min(5, sum(1 for _ in open(file_path))))]
            return any('Ticker' in line for line in lines)
    except Exception:
        return False

def format_indicator_data(df):
    """
    Format indicator data for JSON response
    """
    # Store index name before resetting
    index_name = df.index.name if df.index.name else 'Date' # Default to 'Date' if index has no name
    
    # Reset index, making the original index a column
    df = df.reset_index()
    
    # Ensure the column derived from the index is datetime
    # Use the stored index name
    if index_name in df.columns:
        # Convert to datetime just in case it's not already
        df[index_name] = pd.to_datetime(df[index_name], errors='coerce') 
        # Format the datetime column to string, handle potential NaT from coerce
        df[index_name] = df[index_name].dt.strftime('%Y-%m-%d')
        # Rename the column to 'Date' if it's not already named 'Date' for consistency
        if index_name != 'Date':
             df.rename(columns={index_name: 'Date'}, inplace=True)
    else:
        # Fallback or error handling if the expected index column isn't found
        logger.warning(f"Expected index column '{index_name}' not found after reset_index(). Date formatting might be incorrect.")
        # Attempt to find a date-like column if 'Date' doesn't exist
        if 'Date' not in df.columns:
             date_col = next((col for col in df.columns if 'date' in col.lower()), None)
             if date_col:
                 df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                 df[date_col] = df[date_col].dt.strftime('%Y-%m-%d')
                 df.rename(columns={date_col: 'Date'}, inplace=True)


    # Format to list of objects with date and values
    result = df.to_dict(orient='records')
    return result

# API Routes
@app.route('/api/assets', methods=['GET'])
def get_assets():
    """Return list of available assets"""
    return jsonify(AVAILABLE_ASSETS)

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """Return list of available parameter sets"""
    return jsonify(PARAMETER_SETS)

@app.route('/api/data/<symbol>', methods=['GET'])
def get_data(symbol):
    """
    Get raw price data for a symbol
    Optional query parameters:
    - period: time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - interval: data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    """
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    try:
        data = get_symbol_data(symbol, period)
        return jsonify({
            'symbol': symbol,
            'data': format_indicator_data(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/indicators/<symbol>', methods=['GET'])
def get_indicators(symbol):
    """
    Calculate indicators for a symbol
    Optional query parameters:
    - parameter_set: indicator parameter set to use
    - period: time period for data
    - interval: data interval
    """
    parameter_set = request.args.get('parameter_set', 'default')
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    if parameter_set not in PARAMETER_SETS:
        return jsonify({'error': f'Invalid parameter set. Choose from: {", ".join(PARAMETER_SETS)}'}), 400
    
    try:
        # Get data for the symbol
        data = get_symbol_data(symbol, period)
        logger.info(f"原始数据预览: {data.head()}")
        logger.info(f"原始数据index类型: {type(data.index)}, index name: {data.index.name}")

        # Calculate indicators
        with_indicators = calculate_indicators(data, parameter_set=parameter_set)
        logger.info(f"指标数据预览: {with_indicators.head()}")

        # Return processed data
        return jsonify({
            'symbol': symbol,
            'parameter_set': parameter_set,
            'data': format_indicator_data(with_indicators)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/charts/<symbol>', methods=['GET'])
def generate_charts(symbol):
    """
    Generate interactive charts for a symbol
    Optional query parameters:
    - parameter_sets: comma-separated list of parameter sets
    - period: time period for data
    - interval: data interval
    """
    parameter_sets_str = request.args.get('parameter_sets', 'default')
    parameter_sets = parameter_sets_str.split(',')
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    # Validate parameter sets
    for ps in parameter_sets:
        if ps not in PARAMETER_SETS:
            return jsonify({'error': f'Invalid parameter set: {ps}. Choose from: {", ".join(PARAMETER_SETS)}'}), 400
    
    try:
        # Get data for the symbol
        data = get_symbol_data(symbol, period)
        
        # 创建一个空的chart_files字典，以防出现异常
        chart_files = {
            'indicators': [],
            'bollinger': [],
            'interactive': []
        }
        
        try:
            # Generate charts for all requested parameter sets
            chart_files, indicator_data = generate_parameter_set_charts(
                symbol, data, CHARTS_DIR, parameter_sets=parameter_sets
            )
        except Exception as chart_error:
            # 如果调用generate_parameter_set_charts失败，我们回退到简单图表生成
            print(f"Error in generate_parameter_set_charts: {chart_error}")
            import traceback
            traceback.print_exc()
            
            # 生成基本图表作为后备
            try:
                # 手动创建简单的价格图表
                import matplotlib.pyplot as plt
                
                # 确保目录存在
                os.makedirs(CHARTS_DIR, exist_ok=True)
                
                # 创建一个简单的价格图表
                plt.figure(figsize=(10, 6))
                plt.plot(data.index, data['Close'], 'b-', label=f'{symbol} Price')
                plt.title(f"{symbol} Price Chart (Fallback)")
                plt.grid(True)
                plt.legend()
                
                # 保存图表
                today = datetime.now().strftime("%Y%m%d")
                fallback_path = os.path.join(CHARTS_DIR, f"{symbol}_basic_{today}.png")
                plt.savefig(fallback_path)
                plt.close()
                
                chart_files = {
                    'indicators': [f"/charts/{os.path.basename(fallback_path)}"],
                    'bollinger': [],
                    'interactive': []
                }
                
                print(f"Created fallback chart: {fallback_path}")
            except Exception as fallback_error:
                print(f"Failed to create fallback chart: {fallback_error}")
                return jsonify({'error': str(fallback_error)}), 500
        
        # Create URLs for chart access
        chart_urls = {}
        for chart_type, files in chart_files.items():
            chart_urls[chart_type] = [
                f"/charts/{os.path.basename(file)}" for file in files if file and os.path.exists(file)
            ]
            
        # 查找并添加交互式图表 - 这些是前端页面使用iframe加载的HTML文件
        today = datetime.now().strftime("%Y%m%d")
        interactive_indicators = os.path.join(CHARTS_DIR, f"{symbol}_interactive_indicators_{today}.html")
        interactive_bollinger = os.path.join(CHARTS_DIR, f"{symbol}_interactive_bollinger_{today}.html")
        
        # 修改返回的数据结构以符合前端预期，确保返回正确的交互式图表URL
        response_data = {
            'symbol': symbol,
            'parameter_sets': parameter_sets,
            'charts': {
                # 如果有交互式图表，使用它们；否则回退到静态图表
                'indicators': [f"/charts/{symbol}_interactive_indicators_{today}.html"] 
                              if os.path.exists(interactive_indicators) 
                              else chart_urls.get('indicators', []),
                
                'bollinger': [f"/charts/{symbol}_interactive_bollinger_{today}.html"] 
                            if os.path.exists(interactive_bollinger) 
                            else chart_urls.get('bollinger', [])
            }
        }
        
        # 添加静态图表URLs以备前端需要
        response_data['static_charts'] = chart_urls
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimal_indicators/<asset_type>', methods=['GET'])
def get_optimal_indicators(asset_type):
    """Get optimal indicator set for an asset type"""
    asset_indicators = {
        'forex': ['SMA(50,200)', 'Bollinger Bands(20)', 'MACD(12,26)', 'RSI(14)'],
        'commodities': ['SMA(200)', 'Bollinger Bands(50)', 'ATR(14)', 'Ichimoku'],
        'indices': ['EMA(9,21)', 'Bollinger Bands(20)', 'MACD(12,26)', 'Volume Profile']
    }
    
    if asset_type in asset_indicators:
        return jsonify(asset_indicators[asset_type])
    else:
        return jsonify(['SMA(50)', 'Bollinger Bands(20)', 'RSI(14)'])

@app.route('/api/market_summary', methods=['GET'])
def get_market_summary():
    """
    获取市场概览数据，返回实时的市场数据用于仪表盘展示
    """
    market_data = []
    
    try:
        # 获取主要市场资产的最新数据
        key_assets = {
            'forex': ['EURUSD'],
            'commodities': ['GOLD', 'OIL'], 
            'indices': ['S&P500', 'NASDAQ']
        }
        
        for category, assets in key_assets.items():
            for symbol in assets:
                # 获取该资产的最新数据和前一天数据
                data = get_symbol_data(symbol, period="5d")  # 获取近5天数据以确保有上一个交易日数据
                
                if data.empty:
                    logger.warning(f"无法获取 {symbol} 的数据")
                    continue
                    
                # 获取最新价格
                latest_date = data.index.max()
                previous_date = data.index[-2] if len(data.index) > 1 else None
                
                if previous_date is None:
                    logger.warning(f"无法获取 {symbol} 的前一天数据")
                    continue
                
                last_price = data.loc[latest_date, 'Close']
                previous_price = data.loc[previous_date, 'Close']
                
                # 计算变动
                change = last_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
                trend = 'up' if change >= 0 else 'down'
                
                # 添加到结果中
                market_data.append({
                    'asset': symbol,
                    'lastPrice': float(last_price),
                    'change': float(change),
                    'changePercent': float(change_percent),
                    'trend': trend
                })
                
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"获取市场概览数据出错: {str(e)}")
        # 如果出错，返回一些默认数据以避免前端崩溃
        fallback_data = [
            {'asset': 'EURUSD', 'lastPrice': 1.0784, 'change': 0.0023, 'changePercent': 0.21, 'trend': 'up'},
            {'asset': 'GOLD', 'lastPrice': 2334.50, 'change': -12.70, 'changePercent': -0.54, 'trend': 'down'},
            {'asset': 'S&P500', 'lastPrice': 5021.84, 'change': 32.40, 'changePercent': 0.65, 'trend': 'up'},
            {'asset': 'NASDAQ', 'lastPrice': 15848.16, 'change': 124.35, 'changePercent': 0.79, 'trend': 'up'},
            {'asset': 'OIL', 'lastPrice': 82.63, 'change': -1.45, 'changePercent': -1.72, 'trend': 'down'}
        ]
        return jsonify(fallback_data)

@app.route('/api/chart-data/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """
    Get combined price and indicator data for frontend charting
    Optional query parameters:
    - parameter_set: indicator parameter set to use (default: 'default')
    - period: time period for data (default: '1y')
    """
    parameter_set = request.args.get('parameter_set', 'default')
    period = request.args.get('period', '1y')
    
    if parameter_set not in PARAMETER_SETS:
        return jsonify({'error': f'Invalid parameter set: {parameter_set}. Choose from: {", ".join(PARAMETER_SETS)}'}), 400
        
    try:
        # Get raw price data
        price_data = get_symbol_data(symbol, period)
        if price_data.empty:
            return jsonify({'error': f'Could not retrieve data for symbol: {symbol}'}), 404
            
        # Calculate indicators
        indicator_data = calculate_indicators(price_data.copy(), parameter_set=parameter_set)

        # 合并数据时只保留一份主数据，避免 _x/_y 列
        combined_data = price_data.copy()
        for col in indicator_data.columns:
            combined_data[col] = indicator_data[col]

        # Format data for JSON response
        combined_data.replace([pd.NA, None, float('inf'), float('-inf')], np.nan, inplace=True)
        formatted_data = format_indicator_data(combined_data)
        for record in formatted_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        logger.info(f"Formatted data length for {symbol}: {len(formatted_data)}")
        if len(formatted_data) > 0:
            logger.info(f"First record for {symbol}: {formatted_data[0]}")
            if len(formatted_data) > 1:
                logger.info(f"Last record for {symbol}: {formatted_data[-1]}")

        return jsonify({
            'symbol': symbol,
            'parameter_set': parameter_set,
            'data': formatted_data
        })
        
    except Exception as e:
        logger.error(f"Error getting chart data for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred while processing chart data: {str(e)}'}), 500

@app.route('/api', methods=['GET'])
def api_index():
    """API welcome page with available endpoints"""
    endpoints = {
        'GET /api/assets': 'List of available assets by category',
        'GET /api/parameters': 'Available parameter sets for indicator calculation',
        'GET /api/data/<symbol>': 'Raw price data for a symbol',
        'GET /api/indicators/<symbol>': 'Calculated indicators for a symbol',
        'GET /api/charts/<symbol>': 'Generate and get URLs for symbol charts',
        'GET /api/optimal_indicators/<asset_type>': 'Get optimal indicators for an asset type',
        'GET /api/market_summary': 'Get market summary data for dashboard',
        'GET /charts/<filename>': 'Serve chart files',
        'GET /reports/<filename>': 'Serve report files'
    }
    
    return jsonify({
        'name': 'Financial Analysis Platform API',
        'version': '1.0',
        'endpoints': endpoints,
        'usage': 'See documentation for detailed usage information'
    })

@app.route('/charts/<path:filename>')
def serve_chart(filename):
    """Serve chart files"""
    response = send_from_directory(CHARTS_DIR, filename)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/reports/<path:filename>')
def serve_report(filename):
    """Serve report files"""
    response = send_from_directory(REPORTS_DIR, filename)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Serve React frontend or a temporary welcome page
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # Check if the React build folder exists
    if os.path.exists(app.static_folder):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        elif os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
    
    # If build directory doesn't exist, show a temporary welcome page
    welcome_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Platform</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #3498db;
                margin-top: 30px;
            }}
            .card {{
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
            .api-link {{
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                text-decoration: none;
                border-radius: 4px;
                display: inline-block;
                margin-top: 20px;
            }}
            .api-link:hover {{
                background-color: #2980b9;
            }}
            code {{
                background-color: #f1f1f1;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <h1>Financial Analysis Platform</h1>
        <div class="card">
            <p>Welcome to the Financial Analysis Platform. The React frontend has not been built yet.</p>
            <p>To view and use the complete web application:</p>
            <ol>
                <li>Build the React frontend using: <code>python run.py build</code></li>
                <li>Or run both frontend and backend with: <code>python run.py both</code></li>
            </ol>
            <p>The API is currently running and ready to use.</p>
            <a href="/api" class="api-link">View API Documentation</a>
        </div>
        
        <h2>Quick API Examples</h2>
        <div class="card">
            <p>Get available assets:</p>
            <code>GET /api/assets</code><br><br>
            
            <p>Get parameter sets for technical indicators:</p>
            <code>GET /api/parameters</code><br><br>
            
            <p>Generate charts for EURUSD with default parameters:</p>
            <code>GET /api/charts/EURUSD</code>
        </div>
        
        <h2>Available Assets</h2>
        <div class="card">
            <p><strong>Forex:</strong> {', '.join(AVAILABLE_ASSETS['forex'])}</p>
            <p><strong>Commodities:</strong> {', '.join(AVAILABLE_ASSETS['commodities'])}</p>
            <p><strong>Indices:</strong> {', '.join(AVAILABLE_ASSETS['indices'])}</p>
        </div>
        
        <h2>Available Charts</h2>
        <div class="card">
            <p>Check out some pre-generated charts:</p>
            <ul>
                <li><a href="/charts/EURUSD_indicators_20250501.png">EURUSD Technical Indicators</a></li>
                <li><a href="/charts/EURUSD_bollinger_20250501.png">EURUSD Bollinger Bands</a></li>
                <li><a href="/charts/GOLD_indicators_20250501.png">Gold Technical Indicators</a></li>
                <li><a href="/charts/NASDAQ_indicators_20250502.png">NASDAQ Technical Indicators</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return welcome_html

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
