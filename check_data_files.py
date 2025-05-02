import os
import pandas as pd
import glob

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

def check_fixed_files():
    """检查已修复的文件是否能正确加载"""
    fixed_files = glob.glob(os.path.join(DATA_DIR, "*_fixed.csv"))
    print(f"找到 {len(fixed_files)} 个已修复的数据文件")
    
    successful = 0
    failed = 0
    
    for file_path in fixed_files:
        file_name = os.path.basename(file_path)
        try:
            # 加载数据文件
            df = pd.read_csv(file_path)
            
            # 检查必要的列
            required_columns = ['Date', 'Close', 'High', 'Low', 'Open']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"警告: {file_name} 缺少必要的列: {', '.join(missing_columns)}")
                failed += 1
                continue
            
            # 检查数据行数
            if len(df) < 5:
                print(f"警告: {file_name} 数据行数过少: {len(df)}")
                failed += 1
                continue
                
            # 转换日期列
            df['Date'] = pd.to_datetime(df['Date'])
            
            # 一切正常
            print(f"成功: {file_name} 可以正确加载，包含 {len(df)} 行数据")
            successful += 1
            
        except Exception as e:
            print(f"错误: 无法加载 {file_name}: {str(e)}")
            failed += 1
    
    print(f"\n检查完成! 成功: {successful}, 失败: {failed}")
    return successful, failed

if __name__ == "__main__":
    print("检查已修复的数据文件...")
    check_fixed_files()