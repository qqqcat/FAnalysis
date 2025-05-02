#!/usr/bin/env python
"""
HTML Technical Analysis Report Generator
---------------------------------------
This script generates beautiful HTML technical analysis reports from indicator text files.
It reads the indicator data and creates visually appealing reports.
"""

import os
import re
import sys
import argparse
from datetime import datetime
import glob
import random  # Added for mock data generation

# Add these helper functions to generate realistic-looking data
def get_historical_comparison(symbol):
    """Get historical comparison data for a symbol."""
    # This function should fetch historical data and compare current prices with past periods
    # In a real implementation, this would query a database or parse historical CSV files
    
    # For now, just return sample data
    return {
        'percent_change_month': 2.35,  # example: 2.35% higher than a month ago
        'percent_change_year': -1.47,  # example: 1.47% lower than a year ago
        'vol_comparison': '高于' if symbol in ['EURUSD', 'GBPUSD', 'USDJPY'] else '低于'  # example: higher or lower volatility
    }

def get_correlation_data(symbol):
    """Get correlation data for a symbol with other financial instruments."""
    # This should calculate correlations between the symbol and other currencies/indices
    
    # Sample correlation data
    correlations = {
        'EURUSD': {'strongest_corr': 'GBPUSD', 'strongest_corr_value': 0.78, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.82, 'usd_outlook': 'negative', 'risk_sentiment': 'risk-on'},
        'GBPUSD': {'strongest_corr': 'EURUSD', 'strongest_corr_value': 0.78, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.75, 'usd_outlook': 'negative', 'risk_sentiment': 'risk-on'},
        'USDJPY': {'strongest_corr': 'USD指数', 'strongest_corr_value': 0.65, 'inverse_corr': '黄金', 'inverse_corr_value': -0.58, 'usd_outlook': 'positive', 'risk_sentiment': 'risk-off'},
        'AUDUSD': {'strongest_corr': 'NZDUSD', 'strongest_corr_value': 0.85, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.79, 'usd_outlook': 'negative', 'risk_sentiment': 'risk-on'},
        'GOLD': {'strongest_corr': 'SILVER', 'strongest_corr_value': 0.92, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.73, 'usd_outlook': 'negative', 'risk_sentiment': 'risk-off'},
        'SILVER': {'strongest_corr': 'GOLD', 'strongest_corr_value': 0.92, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.68, 'usd_outlook': 'negative', 'risk_sentiment': 'risk-off'},
        'OIL': {'strongest_corr': 'S&P500', 'strongest_corr_value': 0.63, 'inverse_corr': 'USD指数', 'inverse_corr_value': -0.45, 'usd_outlook': 'neutral', 'risk_sentiment': 'risk-on'}
    }
    
    # If symbol is not in our predefined correlations, provide default values
    if symbol not in correlations:
        return {'strongest_corr': '未知', 'strongest_corr_value': 0.0, 'inverse_corr': '未知', 'inverse_corr_value': 0.0, 'usd_outlook': 'neutral', 'risk_sentiment': 'neutral'}
    
    return correlations[symbol]

def get_seasonal_patterns(symbol):
    """Get seasonal patterns for a symbol."""
    # This should analyze historical seasonal trends
    import datetime
    
    current_month = datetime.datetime.now().strftime('%B')
    quarter_end = "Q2 2025"  # This should be calculated based on current date
    
    # Sample seasonal data
    patterns = {
        'EURUSD': {'current_month': current_month, 'current_month_pattern': 'positive', 'avg_monthly_change': 1.2, 'quarterly_outlook': 'positive', 'quarter_end': quarter_end},
        'GBPUSD': {'current_month': current_month, 'current_month_pattern': 'negative', 'avg_monthly_change': 0.8, 'quarterly_outlook': 'neutral', 'quarter_end': quarter_end},
        'USDJPY': {'current_month': current_month, 'current_month_pattern': 'positive', 'avg_monthly_change': 1.5, 'quarterly_outlook': 'positive', 'quarter_end': quarter_end}
    }
    
    # Return data for the requested symbol, or default data if symbol not found
    return patterns.get(symbol, {'current_month': current_month, 'current_month_pattern': 'neutral', 'avg_monthly_change': 0.5, 'quarterly_outlook': 'neutral', 'quarter_end': quarter_end})

def get_economic_factors(symbol):
    """Get economic factors affecting a currency pair."""
    # This should analyze economic indicators affecting the currency pair
    
    # Sample economic data
    econ_factors = {
        'EURUSD': {'key_indicator1': '欧元区通胀率', 'key_indicator1_value': '2.5%', 'key_indicator1_impact': 'positive',
                  'key_indicator2': '美国就业数据', 'key_indicator2_value': '稳健', 'key_indicator2_impact': 'negative',
                  'interest_rate_diff': -1.25},
        'GBPUSD': {'key_indicator1': '英国GDP增长', 'key_indicator1_value': '1.8%', 'key_indicator1_impact': 'positive',
                  'key_indicator2': '英国利率', 'key_indicator2_value': '3.75%', 'key_indicator2_impact': 'positive',
                  'interest_rate_diff': 0.75},
        'USDJPY': {'key_indicator1': '美日利差', 'key_indicator1_value': '4.2%', 'key_indicator1_impact': 'positive',
                  'key_indicator2': '日本通胀率', 'key_indicator2_value': '2.7%', 'key_indicator2_impact': 'positive',
                  'interest_rate_diff': 4.2}
    }
    
    # Return data for the requested symbol, or default data if symbol not found
    return econ_factors.get(symbol, {'key_indicator1': '利率差异', 'key_indicator1_value': '1.0%', 'key_indicator1_impact': 'neutral',
                                     'key_indicator2': '经济增长', 'key_indicator2_value': '适中', 'key_indicator2_impact': 'neutral',
                                     'interest_rate_diff': 1.0})

# HTML Template - Fixed the formatting issues
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 技术分析报告 | {report_date_formatted}</title>
    <style>
        :root {{
            --primary-color: #1a56db;
            --secondary-color: #e53e3e;
            --bg-color: #f7fafc;
            --text-color: #2d3748;
            --border-color: #e2e8f0;
            --bullish-color: #38a169;
            --bearish-color: #e53e3e;
            --neutral-color: #718096;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            padding: 0;
            margin: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary-color), #1e429f);
            color: white;
            padding: 30px 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }}
        
        .header-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .logo {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}
        
        .date-badge {{
            background-color: rgba(255, 255, 255, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 10px;
        }}
        
        .report-section {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            padding: 25px;
            margin-bottom: 25px;
        }}
        
        h1, h2, h3, h4 {{
            color: var(--primary-color);
            margin-bottom: 15px;
        }}
        
        h1 {{
            font-size: 28px;
        }}
        
        h2 {{
            font-size: 22px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            margin-top: 20px;
        }}
        
        h3 {{
            font-size: 18px;
            margin-top: 15px;
        }}
        
        p {{
            margin-bottom: 15px;
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .status-card {{
            background-color: white;
            border-radius: 6px;
            padding: 15px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        
        .status-card .label {{
            font-size: 14px;
            color: var(--neutral-color);
            margin-bottom: 5px;
        }}
        
        .status-card .value {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        .trend-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 10px;
            font-size: 14px;
        }}
        
        .bullish {{
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--bullish-color);
        }}
        
        .bearish {{
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--bearish-color);
        }}
        
        .neutral {{
            background-color: rgba(113, 128, 150, 0.1);
            color: var(--neutral-color);
        }}
        
        .indicator-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        .indicator-table th, .indicator-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .indicator-table th {{
            background-color: #f8fafc;
            font-weight: 600;
        }}
        
        .indicator-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .chart-image {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-caption {{
            margin-top: 10px;
            font-style: italic;
            color: var(--neutral-color);
            font-size: 14px;
        }}
        
        .fib-levels {{
            display: flex;
            margin-bottom: 20px;
        }}
        
        .fib-column {{
            flex: 1;
        }}
        
        .level-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px;
            border-radius: 4px;
            background-color: #f8fafc;
        }}
        
        .level-pct {{
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .recommendation-box {{
            background: linear-gradient(135deg, #f6f0ff, #e6f7ff);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid var(--primary-color);
        }}
        
        .recommendation-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--primary-color);
        }}
        
        .recommendation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .recommendation-item {{
            background-color: white;
            border-radius: 6px;
            padding: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        
        .recommendation-item .label {{
            font-size: 12px;
            color: var(--neutral-color);
            margin-bottom: 5px;
        }}
        
        .recommendation-item .value {{
            font-size: 16px;
            font-weight: bold;
        }}
        
        .risk-assessment {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .risk-level {{
            width: 100px;
            height: 6px;
            background-color: #e2e8f0;
            border-radius: 3px;
            margin: 0 15px;
            position: relative;
        }}
        
        .risk-fill {{
            position: absolute;
            height: 100%;
            border-radius: 3px;
            left: 0;
        }}
        
        .risk-low .risk-fill {{
            width: 30%;
            background-color: #38a169;
        }}
        
        .risk-medium .risk-fill {{
            width: 60%;
            background-color: #ecc94b;
        }}
        
        .risk-high .risk-fill {{
            width: 90%;
            background-color: #e53e3e;
        }}
        
        .summary {{
            line-height: 1.8;
            font-size: 16px;
        }}
        
        footer {{
            margin-top: 40px;
            padding: 20px 0;
            text-align: center;
            border-top: 1px solid var(--border-color);
            color: var(--neutral-color);
            font-size: 14px;
        }}
        
        .disclaimer {{
            background-color: #fff8f8;
            border-left: 4px solid #feb2b2;
            padding: 15px;
            font-size: 14px;
            color: #742a2a;
            margin: 30px 0 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">{symbol} 技术分析报告</div>
                <div class="subtitle">全面技术指标分析</div>
                <div class="date-badge">{report_date_formatted_cn}</div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <section class="report-section">
            <h2>价格状态与走势</h2>
            
            <div class="status-grid">
                <div class="status-card">
                    <div class="label">当前价格</div>
                    <div class="value">{price}</div>
                </div>
                <div class="status-card">
                    <div class="label">前收盘价</div>
                    <div class="value">{previous_close}</div>
                </div>
                <div class="status-card">
                    <div class="label">日变动</div>
                    <div class="value">{change} ({change_percent})</div>
                </div>
                <div class="status-card">
                    <div class="label">52周区间</div>
                    <div class="value">{week_low} - {week_high}</div>
                </div>
            </div>
            
            <h3>走势分析</h3>
            <div>
                <div class="trend-badge {short_trend_class}">日线: {short_trend}</div>
                <div class="trend-badge {medium_trend_class}">周线: {medium_trend}</div>
                <div class="trend-badge {long_trend_class}">月线: {long_trend}</div>
            </div>
        </section>
        
        <section class="report-section">
            <h2>技术指标分析</h2>
            
            <h3>移动平均线</h3>
            <table class="indicator-table">
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                    <th>信号</th>
                </tr>
                <tr>
                    <td>MA5</td>
                    <td>{ma5}</td>
                    <td><span class="trend-badge {ma5_signal_class}">价格在{ma5_position}</span></td>
                </tr>
                <tr>
                    <td>MA10</td>
                    <td>{ma10}</td>
                    <td><span class="trend-badge {ma10_signal_class}">价格在{ma10_position}</span></td>
                </tr>
                <tr>
                    <td>MA20</td>
                    <td>{ma20}</td>
                    <td><span class="trend-badge {ma20_signal_class}">价格在{ma20_position}</span></td>
                </tr>
                <tr>
                    <td>MA50</td>
                    <td>{ma50}</td>
                    <td><span class="trend-badge {ma50_signal_class}">价格在{ma50_position}</span></td>
                </tr>
                <tr>
                    <td>MA100</td>
                    <td>{ma100}</td>
                    <td><span class="trend-badge {ma100_signal_class}">价格在{ma100_position}</span></td>
                </tr>
                <tr>
                    <td>MA150</td>
                    <td>{ma150}</td>
                    <td><span class="trend-badge {ma150_signal_class}">价格在{ma150_position}</span></td>
                </tr>
                <tr>
                    <td>移动平均线排列</td>
                    <td>-</td>
                    <td><span class="trend-badge {ma_align_class}">{ma_align}</span></td>
                </tr>
            </table>
            
            <h3>振荡指标</h3>
            <table class="indicator-table">
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                    <th>信号</th>
                </tr>
                <tr>
                    <td>RSI (14)</td>
                    <td>{rsi}</td>
                    <td><span class="trend-badge {rsi_signal_class}">{rsi_signal}</span></td>
                </tr>
                <tr>
                    <td>随机指标 %K</td>
                    <td>{stoch_k}</td>
                    <td><span class="trend-badge {stoch_k_signal_class}">{stoch_k_signal}</span></td>
                </tr>
                <tr>
                    <td>随机指标 %D</td>
                    <td>{stoch_d}</td>
                    <td><span class="trend-badge {stoch_d_signal_class}">{stoch_d_signal}</span></td>
                </tr>
                <tr>
                    <td>MACD线</td>
                    <td>{macd}</td>
                    <td><span class="trend-badge {macd_signal_class}">{macd_trend}</span></td>
                </tr>
                <tr>
                    <td>MACD信号线</td>
                    <td>{macd_signal}</td>
                    <td><span class="trend-badge {macd_signal_line_class}">{macd_signal_trend}</span></td>
                </tr>
                <tr>
                    <td>MACD柱状图</td>
                    <td>{macd_histogram}</td>
                    <td><span class="trend-badge {macd_histogram_class}">{macd_histogram_trend}</span></td>
                </tr>
            </table>
            
            <h3>波动性指标</h3>
            <table class="indicator-table">
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>布林带上轨</td>
                    <td>{bb_upper}</td>
                </tr>
                <tr>
                    <td>布林带中轨</td>
                    <td>{bb_middle}</td>
                </tr>
                <tr>
                    <td>布林带下轨</td>
                    <td>{bb_lower}</td>
                </tr>
                <tr>
                    <td>布林带宽度</td>
                    <td>{bb_width}</td>
                </tr>
                <tr>
                    <td>ATR(14)</td>
                    <td>{atr}</td>
                </tr>
            </table>
            
            <div class="chart-container">
                <iframe src="{indicator_chart_html_path}" width="100%" height="850px" style="border:none;" title="{symbol} Interactive Indicators Chart"></iframe>
                <div class="chart-caption">{symbol} 交互式价格走势及主要技术指标 (RSI、MACD)</div>
            </div>

            <div class="chart-container">
                 <iframe src="{bollinger_chart_html_path}" width="100%" height="550px" style="border:none;" title="{symbol} Interactive Bollinger Bands Chart"></iframe>
                <div class="chart-caption">{symbol} 交互式价格走势及布林带指标</div>
            </div>
        </section>
        
        <section class="report-section">
            <h2>支撑与阻力位</h2>
            <table class="indicator-table">
                <tr>
                    <th>类型</th>
                    <th>价位</th>
                    <th>强度</th>
                </tr>
                <tr>
                    <td>阻力位 3</td>
                    <td>{r3}</td>
                    <td>强</td>
                </tr>
                <tr>
                    <td>阻力位 2</td>
                    <td>{r2}</td>
                    <td>中</td>
                </tr>
                <tr>
                    <td>阻力位 1</td>
                    <td>{resistance}</td>
                    <td>弱</td>
                </tr>
                <tr>
                    <td>当前价格</td>
                    <td>{price}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>支撑位 1</td>
                    <td>{support}</td>
                    <td>弱</td>
                </tr>
                <tr>
                    <td>支撑位 2</td>
                    <td>{s2}</td>
                    <td>中</td>
                </tr>
                <tr>
                    <td>支撑位 3</td>
                    <td>{s3}</td>
                    <td>强</td>
                </tr>
            </table>
        </section>
        
        <section class="report-section">
            <h2>斐波那契分析</h2>
            <p>基于从{fib_low}到{fib_high}的波动计算</p>
            
            <div class="fib-levels">
                <div class="fib-column">
                    <h3>回调水平</h3>
                    <div class="level-item">
                        <span>0%</span>
                        <span class="level-pct">{fib_0}</span>
                    </div>
                    <div class="level-item">
                        <span>23.6%</span>
                        <span class="level-pct">{fib_236}</span>
                    </div>
                    <div class="level-item">
                        <span>38.2%</span>
                        <span class="level-pct">{fib_382}</span>
                    </div>
                    <div class="level-item">
                        <span>50.0%</span>
                        <span class="level-pct">{fib_50}</span>
                    </div>
                    <div class="level-item">
                        <span>61.8%</span>
                        <span class="level-pct">{fib_618}</span>
                    </div>
                </div>
                
                <div class="fib-column">
                    <h3>延伸水平</h3>
                    <div class="level-item">
                        <span>0%</span>
                        <span class="level-pct">{fib_0}</span>
                    </div>
                    <div class="level-item">
                        <span>127.2%</span>
                        <span class="level-pct">{fib_1272}</span>
                    </div>
                    <div class="level-item">
                        <span>138.2%</span>
                        <span class="level-pct">{fib_1382}</span>
                    </div>
                    <div class="level-item">
                        <span>161.8%</span>
                        <span class="level-pct">{fib_1618}</span>
                    </div>
                </div>
            </div>
            
            <p><strong>当前价格相对于斐波那契水平:</strong> {fib_position}</p>
        </section>
        
        <section class="report-section">
            <h2>交易建议</h2>
            <div class="recommendation-box">
                <div class="recommendation-title">操作建议: {recommendation}</div>
                <div class="recommendation-grid">
                    <div class="recommendation-item">
                        <div class="label">入场点</div>
                        <div class="value">{entry_point}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">回调买入点</div>
                        <div class="value">{pullback_entry}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">止损</div>
                        <div class="value">{stop_loss}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">目标价 1</div>
                        <div class="value">{tp1}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">目标价 2</div>
                        <div class="value">{tp2}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">目标价 3</div>
                        <div class="value">{tp3}</div>
                    </div>
                    <div class="recommendation-item">
                        <div class="label">风险回报比</div>
                        <div class="value">{risk_reward}</div>
                    </div>
                </div>
            </div>
            
            <h3>风险评估</h3>
            <div class="risk-assessment">
                <span>市场风险水平:</span>
                <div class="risk-level {risk_level_class}">
                    <div class="risk-fill"></div>
                </div>
                <span>{risk_level}</span>
            </div>
            
            <h3>需要关注的经济事件</h3>
            <ul>
                <li>欧洲央行利率决议</li>
                <li>美联储利率决议</li>
                <li>欧元区通胀数据</li>
                <li>美元指数(DXY)走势</li>
            </ul>
        </section>
        
        <section class="report-section">
            <h2>综合分析与展望</h2>
            <div class="summary">
                <p>{summary_p1}</p>
                
                <p>{summary_p2}</p>
                
                <p>{summary_p3}</p>
                
                <p>{summary_p4}</p>
            </div>
            
            <div class="disclaimer">
                <strong>免责声明：</strong>本技术分析报告仅供参考，不构成投资建议。外汇交易涉及显著风险，过往表现不能保证未来业绩。交易前请充分评估您的风险承受能力。
            </div>
        </section>
    </div>
    
    <footer>
        <div class="container">
            <p>© {current_year} 技术分析报告系统 | 生成日期: {report_date_formatted_cn}</p>
        </div>
    </footer>
</body>
</html>
"""

def generate_html_report(symbol, report_date=None, data=None, output_dir="Reports", language="zh_CN"):
    """
    Generate an HTML technical analysis report for the given symbol.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD', 'USDJPY')
        report_date (str, optional): Report date in YYYYMMDD format. If None, today's date is used.
        data (dict, optional): Dictionary with indicator data. If None, dummy data is generated.
        output_dir (str, optional): Directory to save the HTML report. Defaults to "Reports".
        language (str, optional): Language of the report. Defaults to "zh_CN".

    Returns:
        str: Path to the generated HTML report
    """
    from datetime import datetime
    import os
    import numpy as np # Needed for isnan check

    # Use current date if not provided
    if report_date is None:
        report_date = datetime.now().strftime("%Y%m%d")

    # Format dates for display
    date_obj = datetime.strptime(report_date, "%Y%m%d")
    report_date_formatted = date_obj.strftime("%Y-%m-%d")

    # Format date based on language
    if language == "zh_CN":
        report_date_formatted_cn = date_obj.strftime("%Y年%m月%d日")
    else:
        report_date_formatted_cn = date_obj.strftime("%B %d, %Y")

    current_year = datetime.now().year

    # Initialize template_vars with defaults from sample data first
    # This ensures all keys exist before formatting
    template_vars = generate_sample_data(symbol, report_date, language)
    
    # Set interactive chart paths and check if files exist
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Charts")
    
    # Define interactive chart paths (relative to HTML file)
    indicator_chart_html = f"{symbol}_interactive_indicators_{report_date}.html"
    bollinger_chart_html = f"{symbol}_interactive_bollinger_{report_date}.html"
    
    indicator_chart_full_path = os.path.join(charts_dir, indicator_chart_html)
    bollinger_chart_full_path = os.path.join(charts_dir, bollinger_chart_html)
    
    # Check if interactive chart files exist and set paths accordingly
    # Use relative paths in HTML (assuming Reports and Charts directories are at same level)
    if os.path.exists(indicator_chart_full_path):
        template_vars['indicator_chart_html_path'] = f"../Charts/{indicator_chart_html}"
    else:
        # Use the latest available static chart as fallback
        template_vars['indicator_chart_html_path'] = f"../Charts/{symbol}_indicators_{report_date}.png"
        print(f"Warning: Interactive indicators chart not found for {symbol} on {report_date}. Using static image instead.")
    
    if os.path.exists(bollinger_chart_full_path):
        template_vars['bollinger_chart_html_path'] = f"../Charts/{bollinger_chart_html}"
    else:
        # Use the latest available static chart as fallback
        template_vars['bollinger_chart_html_path'] = f"../Charts/{symbol}_bollinger_{report_date}.png"
        print(f"Warning: Interactive Bollinger chart not found for {symbol} on {report_date}. Using static image instead.")

    # If actual data is provided and is a dictionary, update template_vars
    if data and isinstance(data, dict):
        print("Using provided data for report generation.")
        # Update template_vars with actual data, applying formatting
        for key, value in data.items():
            if key in template_vars: # Only update keys that exist in the template
                if isinstance(value, (float, np.floating, int, np.integer)) and not np.isnan(value):
                    # Apply specific formatting based on expected value type/range
                    if key in ['price', 'previous_close', 'week_low', 'week_high', 'support', 'resistance', 's2', 's3', 'r2', 'r3', 'fib_low', 'fib_high', 'fib_0', 'fib_236', 'fib_382', 'fib_50', 'fib_618', 'fib_1272', 'fib_1382', 'fib_1618', 'entry_point', 'pullback_entry', 'stop_loss', 'tp1', 'tp2', 'tp3'] or 'ma' in key or 'bb_' in key:
                         precision = 4 if abs(value) < 10 else 2 # More precision for FX pairs
                         template_vars[key] = f"{value:.{precision}f}"
                    elif key == 'change':
                         precision = 4 if abs(value) < 10 else 2
                         template_vars[key] = f"{value:+.{precision}f}" # Add sign
                    elif key == 'rsi' or key == 'stoch_k' or key == 'stoch_d':
                         template_vars[key] = f"{value:.2f}"
                    elif key == 'macd' or key == 'macd_signal' or key == 'macd_histogram':
                         template_vars[key] = f"{value:.4f}"
                    elif key == 'atr':
                         template_vars[key] = f"{value:.5f}"
                    else: # Default numeric formatting
                         template_vars[key] = f"{value:.2f}"
                elif value is not None and not (isinstance(value, float) and np.isnan(value)): # Keep strings, handle None/NaN
                    template_vars[key] = str(value) # Ensure it's a string
                # If value is None or NaN, the default from sample_data remains

        # --- Recalculate signals/text based on actual data ---
        price_val = data.get('Close')
        prev_close_val = data.get('previous_close') # Needs to be passed in data dict

        # Price Change & Short Trend
        if price_val is not None and prev_close_val is not None and not np.isnan(price_val) and not np.isnan(prev_close_val) and prev_close_val != 0:
            change_val = price_val - prev_close_val
            change_percent_val = (change_val / prev_close_val) * 100
            template_vars['change'] = f"{change_val:+.{4 if abs(price_val) < 10 else 2}f}"
            template_vars['change_percent'] = f"{change_percent_val:+.2f}%"

            if change_val > 0:
                template_vars['short_trend'] = "上涨" if language == "zh_CN" else "Bullish"
                template_vars['short_trend_class'] = "bullish"
            elif change_val < 0:
                template_vars['short_trend'] = "下跌" if language == "zh_CN" else "Bearish"
                template_vars['short_trend_class'] = "bearish"
            else:
                template_vars['short_trend'] = "震荡" if language == "zh_CN" else "Sideways"
                template_vars['short_trend_class'] = "neutral"
        else:
             # Keep sample data defaults if real price/prev_close missing
             pass

        # MA Positions
        if price_val is not None and not np.isnan(price_val):
            for period in [5, 10, 20, 50, 100, 150]:
                ma_key = f'ma{period}' # Assuming key is like 'ma5', 'ma20' etc.
                ma_val = data.get(ma_key)
                if ma_val is not None and not np.isnan(ma_val):
                    pos_key = f'ma{period}_position'
                    class_key = f'ma{period}_signal_class'
                    if price_val > ma_val:
                        template_vars[pos_key] = "上方" if language == "zh_CN" else "Above"
                        template_vars[class_key] = "bullish"
                    else:
                        template_vars[pos_key] = "下方" if language == "zh_CN" else "Below"
                        template_vars[class_key] = "bearish"

        # RSI Signal
        rsi_val = data.get('rsi') # Assuming key is 'rsi'
        if rsi_val is not None and not np.isnan(rsi_val):
            if language == "zh_CN":
                if rsi_val > 70: template_vars['rsi_signal'] = "超买"; template_vars['rsi_signal_class'] = "bearish"
                elif rsi_val < 30: template_vars['rsi_signal'] = "超卖"; template_vars['rsi_signal_class'] = "bullish"
                else: template_vars['rsi_signal'] = "中性"; template_vars['rsi_signal_class'] = "neutral"
            else: # en_US
                if rsi_val > 70: template_vars['rsi_signal'] = "Overbought"; template_vars['rsi_signal_class'] = "bearish"
                elif rsi_val < 30: template_vars['rsi_signal'] = "Oversold"; template_vars['rsi_signal_class'] = "bullish"
                else: template_vars['rsi_signal'] = "Neutral"; template_vars['rsi_signal_class'] = "neutral"

        # Stochastic Signals (Assuming keys 'stoch_k', 'stoch_d')
        stoch_k_val = data.get('stoch_k')
        stoch_d_val = data.get('stoch_d')
        if stoch_k_val is not None and not np.isnan(stoch_k_val):
             # ... (add logic for stoch_k_signal and stoch_k_signal_class) ...
             pass # Placeholder - add logic similar to RSI
        if stoch_d_val is not None and not np.isnan(stoch_d_val):
             # ... (add logic for stoch_d_signal and stoch_d_signal_class) ...
             pass # Placeholder - add logic similar to RSI

        # MACD Signals (Assuming keys 'macd', 'macd_signal', 'macd_histogram')
        macd_val = data.get('macd')
        macd_sig_val = data.get('macd_signal')
        macd_hist_val = data.get('macd_histogram')
        if macd_val is not None and not np.isnan(macd_val):
             template_vars['macd_trend'] = ("看涨" if language == "zh_CN" else "Bullish") if macd_val > 0 else ("看跌" if language == "zh_CN" else "Bearish")
             template_vars['macd_signal_class'] = "bullish" if macd_val > 0 else "bearish"
        if macd_val is not None and macd_sig_val is not None and not np.isnan(macd_val) and not np.isnan(macd_sig_val):
             template_vars['macd_signal_trend'] = ("金叉" if language == "zh_CN" else "Golden Cross") if macd_val > macd_sig_val else ("死叉" if language == "zh_CN" else "Death Cross")
             template_vars['macd_signal_line_class'] = "bullish" if macd_val > macd_sig_val else "bearish"
        if macd_hist_val is not None and not np.isnan(macd_hist_val):
             template_vars['macd_histogram_trend'] = ("扩散" if language == "zh_CN" else "Diverging") if macd_hist_val > 0 else ("收敛" if language == "zh_CN" else "Converging")
             template_vars['macd_histogram_class'] = "bullish" if macd_hist_val > 0 else "bearish"

        # Update summary based on actual data if possible
        # (This requires more complex logic or passing pre-generated summary text)
        # For now, we'll keep the sample summary but use real values where possible
        try:
            template_vars['summary_p1'] = template_vars['summary_p1'].format(**template_vars)
            template_vars['summary_p2'] = template_vars['summary_p2'].format(**template_vars)
            template_vars['summary_p3'] = template_vars['summary_p3'].format(**template_vars)
            template_vars['summary_p4'] = template_vars['summary_p4'].format(**template_vars)
        except KeyError as ke:
            print(f"Warning: Missing key for summary formatting: {ke}. Summary might be incomplete.")


    # Add common vars AFTER potentially updating from real data
    template_vars['symbol'] = symbol
    template_vars['report_date'] = report_date
    template_vars['report_date_formatted'] = report_date_formatted
    template_vars['report_date_formatted_cn'] = report_date_formatted_cn
    template_vars['current_year'] = current_year

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate HTML content from template
    try:
        html_content = HTML_TEMPLATE.format(**template_vars)
    except KeyError as e:
        print(f"Error: Missing key in template: {e}")
        # Add default value for missing key
        template_vars[str(e).strip("'")] = "N/A"
        html_content = HTML_TEMPLATE.format(**template_vars)
    except Exception as e:
        print(f"Error formatting template: {e}")
        raise
    
    # Write to file
    output_file = os.path.join(output_dir, f"{symbol}_Beautiful_Report_{report_date}.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 为了兼容性，同时创建旧格式文件名的副本
    output_file_alt = os.path.join(output_dir, f"{symbol}_report_{report_date}.html")
    with open(output_file_alt, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file

def generate_sample_data(symbol, report_date, language="zh_CN"):
    """Generate sample data for the report when real data is not available.
    
    Args:
        symbol (str): The trading symbol
        report_date (str): Report date in YYYYMMDD format
        language (str): Language of the report
        
    Returns:
        dict: Sample data for the report
    """
    # Create realistic-looking sample data for the report
    import random
    from datetime import datetime
    
    # Base price data (different ranges for different symbols)
    price_base = {
        'EURUSD': 1.08,
        'GBPUSD': 1.27,
        'USDJPY': 155.0,
        'AUDUSD': 0.66,
        'USDCAD': 1.36,
        'GOLD': 2300,
        'OIL': 78.5,
        'S&P500': 5200,
        'NASDAQ': 16500,
        'DOW': 39000
    }
    
    # Get base price or use default
    base_price = price_base.get(symbol, 100.0)
    
    # Random variation percentage
    variation = random.uniform(-0.015, 0.015)  # Up to 1.5% variation
    
    # Current price with variation
    price = round(base_price * (1 + variation), 4 if base_price < 100 else 2)
    
    # Previous close (slightly different)
    prev_variation = random.uniform(-0.01, 0.01)
    previous_close = round(price * (1 - prev_variation), 4 if base_price < 100 else 2)
    
    # Calculate change
    change = round(price - previous_close, 4 if base_price < 100 else 2)
    change_percent = f"{round(change / previous_close * 100, 2)}%"
    
    # 52-week range
    week_low = round(base_price * 0.9, 4 if base_price < 100 else 2)
    week_high = round(base_price * 1.1, 4 if base_price < 100 else 2)
    
    # Language-specific text
    if language == "zh_CN":
        trend_options = ["上涨", "下跌", "震荡"]
        trend_class_options = ["bullish", "bearish", "neutral"]
    else:
        trend_options = ["Bullish", "Bearish", "Sideways"]
        trend_class_options = ["bullish", "bearish", "neutral"]
    
    # Calculate trend based on price changes
    short_trend_idx = 0 if change > 0 else 1 if change < 0 else 2
    medium_trend_idx = random.randint(0, 2)  # More random
    long_trend_idx = random.randint(0, 2)  # More random
    
    short_trend = trend_options[short_trend_idx]
    medium_trend = trend_options[medium_trend_idx]
    long_trend = trend_options[long_trend_idx]
    
    short_trend_class = trend_class_options[short_trend_idx]
    medium_trend_class = trend_class_options[medium_trend_idx]
    long_trend_class = trend_class_options[long_trend_idx]
    
    # Moving average data
    ma_values = {}
    ma_positions = {}
    ma_signal_classes = {}
    
    for period in [5, 10, 20, 50, 100, 150]:
        # Generate MA values with proper relations (shorter MAs closer to price)
        ma_variation = random.uniform(-0.03, 0.03) * (1 - period/200)  # Smaller variation for longer periods
        ma_values[f'ma{period}'] = round(base_price * (1 + ma_variation), 4 if base_price < 100 else 2)
        
        # Determine price position relative to MA
        if price > ma_values[f'ma{period}']:
            ma_positions[f'ma{period}_position'] = "上方" if language == "zh_CN" else "Above"
            ma_signal_classes[f'ma{period}_signal_class'] = "bullish"
        else:
            ma_positions[f'ma{period}_position'] = "下方" if language == "zh_CN" else "Below"
            ma_signal_classes[f'ma{period}_signal_class'] = "bearish"
    
    # MA alignment
    if language == "zh_CN":
        ma_align_options = ["多头排列", "空头排列", "交叉排列"]
        ma_align_class_options = ["bullish", "bearish", "neutral"]
    else:
        ma_align_options = ["Bullish Alignment", "Bearish Alignment", "Mixed Alignment"]
        ma_align_class_options = ["bullish", "bearish", "neutral"]
        
    ma_idx = random.randint(0, 2)
    ma_align = ma_align_options[ma_idx]
    ma_align_class = ma_align_class_options[ma_idx]
    
    # Oscillator indicators
    rsi = random.randint(30, 70)
    if language == "zh_CN":
        if rsi > 70:
            rsi_signal = "超买"
            rsi_signal_class = "bearish"
        elif rsi < 30:
            rsi_signal = "超卖"
            rsi_signal_class = "bullish"
        else:
            rsi_signal = "中性"
            rsi_signal_class = "neutral"
    else:
        if rsi > 70:
            rsi_signal = "Overbought"
            rsi_signal_class = "bearish"
        elif rsi < 30:
            rsi_signal = "Oversold"
            rsi_signal_class = "bullish"
        else:
            rsi_signal = "Neutral"
            rsi_signal_class = "neutral"
    
    # Stochastic
    stoch_k = random.randint(20, 80)
    stoch_d = random.randint(20, 80)
    
    if language == "zh_CN":
        if stoch_k > 80:
            stoch_k_signal = "超买"
            stoch_k_signal_class = "bearish"
        elif stoch_k < 20:
            stoch_k_signal = "超卖"
            stoch_k_signal_class = "bullish"
        else:
            stoch_k_signal = "中性"
            stoch_k_signal_class = "neutral"
            
        if stoch_d > 80:
            stoch_d_signal = "超买"
            stoch_d_signal_class = "bearish"
        elif stoch_d < 20:
            stoch_d_signal = "超卖"
            stoch_d_signal_class = "bullish"
        else:
            stoch_d_signal = "中性"
            stoch_d_signal_class = "neutral"
    else:
        if stoch_k > 80:
            stoch_k_signal = "Overbought"
            stoch_k_signal_class = "bearish"
        elif stoch_k < 20:
            stoch_k_signal = "Oversold"
            stoch_k_signal_class = "bullish"
        else:
            stoch_k_signal = "Neutral"
            stoch_k_signal_class = "neutral"
            
        if stoch_d > 80:
            stoch_d_signal = "Overbought"
            stoch_d_signal_class = "bearish"
        elif stoch_d < 20:
            stoch_d_signal = "Oversold"
            stoch_d_signal_class = "bullish"
        else:
            stoch_d_signal = "Neutral"
            stoch_d_signal_class = "neutral"
    
    # MACD
    macd = round(random.uniform(-0.5, 0.5), 2)
    macd_signal = round(random.uniform(-0.5, 0.5), 2)
    macd_histogram = round(macd - macd_signal, 2)
    
    if language == "zh_CN":
        if macd > 0:
            macd_trend = "看涨"
            macd_signal_class = "bullish"
        else:
            macd_trend = "看跌"
            macd_signal_class = "bearish"
            
        if macd > macd_signal:
            macd_signal_trend = "金叉"
            macd_signal_line_class = "bullish"
        else:
            macd_signal_trend = "死叉"
            macd_signal_line_class = "bearish"
            
        if macd_histogram > 0:
            macd_histogram_trend = "扩散"
            macd_histogram_class = "bullish"
        else:
            macd_histogram_trend = "收敛"
            macd_histogram_class = "bearish"
    else:
        if macd > 0:
            macd_trend = "Bullish"
            macd_signal_class = "bullish"
        else:
            macd_trend = "Bearish"
            macd_signal_class = "bearish"
            
        if macd > macd_signal:
            macd_signal_trend = "Golden Cross"
            macd_signal_line_class = "bullish"
        else:
            macd_signal_trend = "Death Cross"
            macd_signal_line_class = "bearish"
            
        if macd_histogram > 0:
            macd_histogram_trend = "Diverging"
            macd_histogram_class = "bullish"
        else:
            macd_histogram_trend = "Converging"
            macd_histogram_class = "bearish"
    
    # Bollinger Bands
    bb_middle = price
    bb_width = round(random.uniform(0.5, 2.0), 2)
    bb_upper = round(bb_middle * (1 + 0.02 * bb_width), 4 if base_price < 100 else 2)
    bb_lower = round(bb_middle * (1 - 0.02 * bb_width), 4 if base_price < 100 else 2)
    
    # ATR
    atr = round(price * random.uniform(0.005, 0.02), 4 if base_price < 100 else 2)
    
    # Support and resistance
    support = round(price * (1 - random.uniform(0.01, 0.03)), 4 if base_price < 100 else 2)
    resistance = round(price * (1 + random.uniform(0.01, 0.03)), 4 if base_price < 100 else 2)
    s2 = round(support * (1 - random.uniform(0.01, 0.02)), 4 if base_price < 100 else 2)
    s3 = round(s2 * (1 - random.uniform(0.01, 0.02)), 4 if base_price < 100 else 2)
    r2 = round(resistance * (1 + random.uniform(0.01, 0.02)), 4 if base_price < 100 else 2)
    r3 = round(r2 * (1 + random.uniform(0.01, 0.02)), 4 if base_price < 100 else 2)
    
    # Fibonacci levels
    if language == "zh_CN":
        fib_trend = random.choice(["上升", "下降"])
    else:
        fib_trend = random.choice(["Ascending", "Descending"])
        
    if fib_trend == "上升" or fib_trend == "Ascending":
        fib_low = round(price * (1 - random.uniform(0.05, 0.1)), 4 if base_price < 100 else 2)
        fib_high = price
    else:
        fib_high = round(price * (1 + random.uniform(0.05, 0.1)), 4 if base_price < 100 else 2)
        fib_low = price
    
    fib_range = fib_high - fib_low
    fib_0 = round(fib_low, 4 if base_price < 100 else 2)
    fib_236 = round(fib_low + fib_range * 0.236, 4 if base_price < 100 else 2)
    fib_382 = round(fib_low + fib_range * 0.382, 4 if base_price < 100 else 2)
    fib_50 = round(fib_low + fib_range * 0.5, 4 if base_price < 100 else 2)
    fib_618 = round(fib_low + fib_range * 0.618, 4 if base_price < 100 else 2)
    fib_1272 = round(fib_low + fib_range * 1.272, 4 if base_price < 100 else 2)
    fib_1382 = round(fib_low + fib_range * 1.382, 4 if base_price < 100 else 2)
    fib_1618 = round(fib_low + fib_range * 1.618, 4 if base_price < 100 else 2)
    
    # Position relative to fib levels
    if language == "zh_CN":
        fib_positions = ["在0-23.6%区间", "在23.6%-38.2%区间", "在38.2%-50%区间", "在50%-61.8%区间", "在61.8%-100%区间", "突破100%水平"]
    else:
        fib_positions = ["In 0-23.6% range", "In 23.6%-38.2% range", "In 38.2%-50% range", "In 50%-61.8% range", "In 61.8%-100% range", "Above 100% level"]
        
    fib_position = random.choice(fib_positions)
    
    # Trading recommendation
    if language == "zh_CN":
        rec_options = ["买入", "卖出", "观望", "等待回调买入", "等待反弹卖出"]
    else:
        rec_options = ["Buy", "Sell", "Hold", "Buy on Pullback", "Sell on Rally"]
        
    recommendation = random.choice(rec_options)
    
    # Entry points
    if language == "zh_CN":
        if "买入" in recommendation:
            entry_point = price
            pullback_entry = support
            stop_loss = s2
            tp1 = resistance
            tp2 = r2
            tp3 = r3
        elif "卖出" in recommendation:
            entry_point = price
            pullback_entry = resistance
            stop_loss = r2
            tp1 = support
            tp2 = s2
            tp3 = s3
        else:
            entry_point = "-"
            pullback_entry = "-"
            stop_loss = "-"
            tp1 = "-"
            tp2 = "-"
            tp3 = "-"
    else:
        if "Buy" in recommendation:
            entry_point = price
            pullback_entry = support
            stop_loss = s2
            tp1 = resistance
            tp2 = r2
            tp3 = r3
        elif "Sell" in recommendation:
            entry_point = price
            pullback_entry = resistance
            stop_loss = r2
            tp1 = support
            tp2 = s2
            tp3 = s3
        else:
            entry_point = "-"
            pullback_entry = "-"
            stop_loss = "-"
            tp1 = "-"
            tp2 = "-"
            tp3 = "-"
    
    # Risk reward
    if isinstance(entry_point, (int, float)) and isinstance(stop_loss, (int, float)) and isinstance(tp2, (int, float)):
        if language == "zh_CN":
            if "买入" in recommendation:
                risk = entry_point - stop_loss
                reward = tp2 - entry_point
            else:
                risk = stop_loss - entry_point
                reward = entry_point - tp2
        else:
            if "Buy" in recommendation:
                risk = entry_point - stop_loss
                reward = tp2 - entry_point
            else:
                risk = stop_loss - entry_point
                reward = entry_point - tp2
                
        if risk > 0:
            risk_reward = f"1:{round(reward/risk, 1)}"
        else:
            risk_reward = "-"
    else:
        risk_reward = "-"
    
    # Risk level
    if language == "zh_CN":
        risk_levels = ["低风险", "中等风险", "高风险"]
    else:
        risk_levels = ["Low Risk", "Medium Risk", "High Risk"]
        
    risk_level_classes = ["risk-low", "risk-medium", "risk-high"]
    risk_idx = random.randint(0, 2)
    risk_level = risk_levels[risk_idx]
    risk_level_class = risk_level_classes[risk_idx]
    
    # Get additional data from helper functions
    hist_comp = get_historical_comparison(symbol)
    corr_data = get_correlation_data(symbol)
    seasonal_data = get_seasonal_patterns(symbol)
    econ_data = get_economic_factors(symbol)
    
    # Summary paragraphs
    if language == "zh_CN":
        summary_p1 = f"{symbol}目前处于{short_trend}趋势，价格{price}较前收盘价{change_percent}。从技术指标来看，RSI为{rsi}，表明{'超买状态' if rsi > 70 else '超卖状态' if rsi < 30 else '中性状态'}。"
        
        summary_p2 = f"移动平均线分析显示，价格目前{'高于' if price > ma_values['ma20'] else '低于'}20日均线，{'高于' if price > ma_values['ma50'] else '低于'}50日均线，整体呈现{ma_align}。MACD指标{'金叉' if macd > macd_signal else '死叉'}，显示{'潜在上涨' if macd > macd_signal else '潜在下跌'}动能。"
        
        summary_p3 = f"重要支撑位于{support}和{s2}，关键阻力位于{resistance}和{r2}。价格突破{'阻力位' if short_trend == '上涨' else '支撑位'}可能会加速{'上涨' if short_trend == '上涨' else '下跌'}。"
        
        summary_p4 = f"综合技术指标和市场环境，我们{'建议' if recommendation != '观望' else '暂不建议'}{recommendation}。交易者应密切关注{econ_data['key_indicator1']}和{econ_data['key_indicator2']}等基本面因素，并根据市场变化及时调整策略。"
    else:
        summary_p1 = f"{symbol} is currently in a {short_trend.lower()} trend, with price at {price}, {change_percent} from the previous close. Technical indicators show RSI at {rsi}, indicating {'an overbought' if rsi > 70 else 'an oversold' if rsi < 30 else 'a neutral'} condition."
        
        summary_p2 = f"Moving average analysis shows price {'above' if price > ma_values['ma20'] else 'below'} the 20-day MA and {'above' if price > ma_values['ma50'] else 'below'} the 50-day MA, with an overall {ma_align.lower()} pattern. MACD shows a {'golden cross' if macd > macd_signal else 'death cross'}, indicating {'potential upward' if macd > macd_signal else 'potential downward'} momentum."
        
        summary_p3 = f"Key support levels are at {support} and {s2}, while resistance levels are at {resistance} and {r2}. A breakout above {'resistance' if short_trend == 'Bullish' else 'support'} could accelerate the {'upward' if short_trend == 'Bullish' else 'downward'} move."
        
        summary_p4 = f"Based on technical indicators and market conditions, our recommendation is to {recommendation}. Traders should closely monitor factors such as {econ_data['key_indicator1']} and {econ_data['key_indicator2']}, and adjust strategies accordingly as market conditions change."
    
    # Compile all data
    return {
        'price': price,
        'previous_close': previous_close,
        'change': change,
        'change_percent': change_percent,
        'week_low': week_low,
        'week_high': week_high,
        'short_trend': short_trend,
        'medium_trend': medium_trend,
        'long_trend': long_trend,
        'short_trend_class': short_trend_class,
        'medium_trend_class': medium_trend_class,
        'long_trend_class': long_trend_class,
        **ma_values,
        **ma_positions,
        **ma_signal_classes,
        'ma_align': ma_align,
        'ma_align_class': ma_align_class,
        'rsi': rsi,
        'rsi_signal': rsi_signal,
        'rsi_signal_class': rsi_signal_class,
        'stoch_k': stoch_k,
        'stoch_d': stoch_d,
        'stoch_k_signal': stoch_k_signal,
        'stoch_k_signal_class': stoch_k_signal_class,
        'stoch_d_signal': stoch_d_signal,
        'stoch_d_signal_class': stoch_d_signal_class,
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_histogram': macd_histogram,
        'macd_trend': macd_trend,
        'macd_signal_trend': macd_signal_trend,
        'macd_histogram_trend': macd_histogram_trend,
        'macd_signal_class': macd_signal_class,
        'macd_signal_line_class': macd_signal_line_class,
        'macd_histogram_class': macd_histogram_class,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'bb_width': bb_width,
        'atr': atr,
        'support': support,
        'resistance': resistance,
        's2': s2,
        's3': s3,
        'r2': r2,
        'r3': r3,
        'fib_low': fib_low,
        'fib_high': fib_high,
        'fib_0': fib_0,
        'fib_236': fib_236,
        'fib_382': fib_382,
        'fib_50': fib_50,
        'fib_618': fib_618,
        'fib_1272': fib_1272,
        'fib_1382': fib_1382,
        'fib_1618': fib_1618,
        'fib_position': fib_position,
        'recommendation': recommendation,
        'entry_point': entry_point,
        'pullback_entry': pullback_entry,
        'stop_loss': stop_loss,
        'tp1': tp1,
        'tp2': tp2,
        'tp3': tp3,
        'risk_reward': risk_reward,
        'risk_level': risk_level,
        'risk_level_class': risk_level_class,
        'summary_p1': summary_p1,
        'summary_p2': summary_p2,
        'summary_p3': summary_p3,
        'summary_p4': summary_p4,
    }

# Main function for command line use
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an HTML technical analysis report")
    parser.add_argument("symbol", help="Trading symbol (e.g., EURUSD, USDJPY)")
    parser.add_argument("--date", help="Report date in YYYYMMDD format", default=None)
    parser.add_argument("--output-dir", help="Output directory", default="Reports")
    parser.add_argument("--language", help="Language of the report (e.g., zh_CN, en_US)", default="zh_CN")
    
    args = parser.parse_args()
    
    output_file = generate_html_report(args.symbol, args.date, output_dir=args.output_dir, language=args.language)
    print(f"Report generated: {output_file}")
