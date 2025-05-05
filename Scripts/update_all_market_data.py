#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def update_market_data(symbols_file, output_dir, period="1y", interval="1d"):
    """
    批量更新金融产品数据
    
    参数:
    symbols_file (str): 包含符号列表的文件路径
    output_dir (str): 数据输出目录
    period (str): 数据时间跨度，默认为1年
    interval (str): 数据时间间隔，默认为1天
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取符号列表 - 使用utf-8编码
    with open(symbols_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    symbols = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # 如果有注释，只取符号部分
            symbol = line.split('#')[0].strip()
            symbols.append(symbol)
    
    # 当前日期
    today = datetime.now()
    # 一年前的日期
    start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # 获取所有符号的数据
    total = len(symbols)
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"正在获取第 {i}/{total} 个产品 {symbol} 的数据...")
            
            # 使用yfinance获取数据
            data = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if data.empty:
                print(f"警告: {symbol} 没有获取到数据")
                continue
                
            # 确保产品目录存在
            symbol_dir = os.path.join(output_dir, symbol.replace('=', '_').replace('^', ''))
            os.makedirs(symbol_dir, exist_ok=True)
            
            # 保存数据
            output_file = os.path.join(symbol_dir, f"{symbol.replace('=', '_').replace('^', '')}_daily.csv")
            data.to_csv(output_file)
            print(f"已成功保存 {symbol} 的数据到 {output_file}")
            
        except Exception as e:
            print(f"获取 {symbol} 数据时出错: {str(e)}")
    
    print("所有数据更新完成!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    # 符号列表文件路径
    symbols_file = os.path.join(project_dir, "Data", "Symbols", "symbols.txt")
    # 输出目录
    output_dir = os.path.join(project_dir, "Data", "Market")
    
    # 更新数据
    update_market_data(symbols_file, output_dir, period="1y", interval="1d")