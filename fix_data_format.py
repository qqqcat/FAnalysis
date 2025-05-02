#!/usr/bin/env python
"""
数据文件格式修复工具
-------------------
这个脚本用于修复数据文件的格式，使其符合技术分析系统所需的格式。
主要处理：
1. 删除多余的头信息行（Ticker行和空Date行）
2. 保留简单的列名行和数据行
3. 确保日期列格式正确
"""

import os
import pandas as pd
import glob
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_data_format(data_dir):
    """
    修复数据文件格式，使其符合应用程序的期望格式。
    主要解决以下问题：
    1. 去除多余的头信息行（如Ticker行和空Date行）
    2. 确保Date列是日期格式并设置为索引
    3. 确保包含必要的OHLC列（Open, High, Low, Close）
    """
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    # 统计
    total_files = len(csv_files)
    fixed_files = 0
    failed_files = 0
    
    logger.info(f"找到{total_files}个CSV文件需要处理")
    
    for file_path in csv_files:
        try:
            file_name = os.path.basename(file_path)
            # 跳过已经处理过的文件
            if "_fixed.csv" in file_name:
                logger.info(f"跳过已处理的文件: {file_name}")
                continue
                
            logger.info(f"处理文件: {file_name}")
            
            # 读取原始CSV文件，跳过前几行头信息
            try:
                # 先尝试读取文件头，查看结构
                with open(file_path, 'r') as f:
                    header_lines = [next(f) for _ in range(min(5, sum(1 for _ in f)))]
                
                # 确定要跳过的行数
                skip_rows = 0
                if len(header_lines) > 1 and any("Ticker" in line for line in header_lines):
                    skip_rows = 2  # 跳过Ticker行和空Date行
                
                # 读取数据，跳过确定的行数
                df = pd.read_csv(file_path, skiprows=skip_rows)
                
                # 检查是否包含必要的列
                required_columns = ['Date', 'Close', 'High', 'Low', 'Open']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    logger.warning(f"文件 {file_name} 缺少必要的列: {', '.join(missing_columns)}")
                    # 尝试从其他列名映射
                    if 'Date' in missing_columns and df.columns[0].lower() in ['date', 'time', 'datetime']:
                        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
                    if 'Price' in df.columns and 'Close' in missing_columns:
                        df.rename(columns={'Price': 'Close'}, inplace=True)
                
                # 确保Date列是日期格式
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                
                # 保存修复后的文件
                fixed_file_path = os.path.join(data_dir, file_name.replace('.csv', '_fixed.csv'))
                df.to_csv(fixed_file_path, index=False)
                
                logger.info(f"成功修复文件: {file_name} -> {os.path.basename(fixed_file_path)}")
                fixed_files += 1
                
            except Exception as e:
                logger.error(f"无法读取或处理文件 {file_name}: {str(e)}")
                failed_files += 1
                
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
            failed_files += 1
    
    logger.info(f"处理完成. 总文件数: {total_files}, 成功修复: {fixed_files}, 失败: {failed_files}")
    return fixed_files, failed_files

if __name__ == "__main__":
    # 数据目录
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
    
    # 执行修复
    fixed, failed = fix_data_format(data_dir)
    
    print(f"数据修复完成! 成功处理: {fixed} 文件, 失败: {failed} 文件")
    print("修复后的文件名带有'_fixed'后缀")