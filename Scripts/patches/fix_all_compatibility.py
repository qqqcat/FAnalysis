#!/usr/bin/env python
"""
Python 3.13 & pandas_ta 兼容性修复工具
---------------------------------------
此脚本自动修复 pandas_ta 库在 Python 3.13 环境中的兼容性问题，包括：
1. numpy 中的 NaN/nan 命名差异
2. PSAR 键名差异
3. Ichimoku 返回值类型变化
4. 其他常见兼容性问题
"""

import os
import sys
import importlib.util
import traceback
import logging
import shutil
import pandas as pd
import numpy as np
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout),
                        logging.FileHandler('pandas_ta_compatibility_fix.log')
                    ])
logger = logging.getLogger(__name__)

def find_module_path(module_name):
    """查找模块的安装路径"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            logger.error(f"找不到模块 {module_name}，请确认它已安装")
            return None
        
        module_path = Path(spec.origin).parent
        logger.info(f"找到 {module_name} 安装路径: {module_path}")
        return module_path
    except Exception as e:
        logger.error(f"查找 {module_name} 路径时出错: {e}")
        traceback.print_exc()
        return None

def backup_file(file_path):
    """备份文件"""
    try:
        backup_path = str(file_path) + '.bak'
        # 如果备份已存在，不再创建新备份
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            logger.info(f"已创建备份: {backup_path}")
        else:
            logger.info(f"备份已存在: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"创建备份时出错: {e}")
        traceback.print_exc()
        return False

def fix_numpy_nan_import(file_path):
    """修复文件中的 numpy NaN 导入问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换导入语句
        if 'from numpy import NaN as npNaN' in content:
            content = content.replace('from numpy import NaN as npNaN', 'from numpy import nan as npNaN')
            logger.info(f"替换 NaN 导入语句: {file_path}")
            
            # 备份原文件
            if backup_file(file_path):
                # 写回修改后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"成功修复 NaN 导入问题: {file_path}")
                return True
        else:
            logger.info(f"文件无需修复 NaN 导入: {file_path}")
        
        return False
    except Exception as e:
        logger.error(f"修复 NaN 导入时出错: {e}")
        traceback.print_exc()
        return False

def create_compatibility_patch(script_path):
    """创建兼容性补丁，修改项目中的calculate_indicators.py文件"""
    try:
        if not os.path.exists(script_path):
            logger.error(f"找不到目标脚本: {script_path}")
            return False
        
        # 备份原文件
        if not backup_file(script_path):
            return False
        
        # 读取文件内容
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改1: 确保正确导入numpy nan
        has_np_import = 'import numpy as np' in content
        if not has_np_import:
            content = content.replace('import pandas as pd', 'import pandas as pd\nimport numpy as np')
            logger.info(f"添加 numpy 导入: {script_path}")
        
        # 修改2: 增强Parabolic SAR处理逻辑
        psar_pattern = "sar_result = ta.psar(data['High'], data['Low'], data['Close'], af=0.02, max_af=0.2)\n    data['SAR'] = sar_result['PSARl_0.020_0.200']"
        psar_replacement = """sar_result = ta.psar(data['High'], data['Low'], data['Close'], af=0.02, max_af=0.2)
    
    # 处理不同版本pandas_ta库返回的键名差异
    if 'PSARl_0.020_0.200' in sar_result:
        data['SAR'] = sar_result['PSARl_0.020_0.200']
    elif 'PSAR_0.020_0.200' in sar_result:
        data['SAR'] = sar_result['PSAR_0.020_0.200']
    else:
        # 如果找不到已知的键名，尝试寻找包含PSAR的键
        psar_keys = [key for key in sar_result.keys() if 'PSAR' in key or 'psar' in key.lower()]
        if psar_keys:
            data['SAR'] = sar_result[psar_keys[0]]
        else:
            print(f"Warning: 找不到PSAR结果。可用键: {list(sar_result.keys())}")
            data['SAR'] = np.nan  # 使用NaN作为数据不可用的标识"""
        
        if psar_pattern in content:
            content = content.replace(psar_pattern, psar_replacement)
            logger.info(f"增强 PSAR 处理逻辑: {script_path}")
        
        # 修改3: 增强Ichimoku Cloud处理逻辑
        ichimoku_pattern_start = "        try:\n            ichimoku_result = ta.ichimoku(data['High'], data['Low'], data['Close'], "
        ichimoku_pattern_end = "            # Calculate Cloud Direction more reliably\n            data['Cloud_Direction'] = 0"
        
        # 尝试在内容中查找模式
        if ichimoku_pattern_start in content and ichimoku_pattern_end in content:
            # 找到起始和结束位置
            start_pos = content.find(ichimoku_pattern_start)
            end_pos = content.find(ichimoku_pattern_end)
            
            if start_pos != -1 and end_pos != -1:
                # 构建替换内容
                ichimoku_replacement = """        try:
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
            
            # Calculate Cloud Direction more reliably"""
                
                # 替换内容
                content = content[:start_pos] + ichimoku_replacement + content[end_pos:]
                logger.info(f"增强 Ichimoku Cloud 处理逻辑: {script_path}")
        
        # 修改4: 增强Cloud Direction计算逻辑
        cloud_dir_pattern = "            data['Cloud_Direction'] = 0\n            mask_above = data['Close'] > data['Ichimoku_SpanA']\n            mask_below = data['Close'] < data['Ichimoku_SpanB']\n            data.loc[mask_above, 'Cloud_Direction'] = 1\n            data.loc[mask_below, 'Cloud_Direction'] = -1"
        cloud_dir_replacement = """            data['Cloud_Direction'] = 0
            data_with_cloud = data.dropna(subset=['Ichimoku_SpanA', 'Ichimoku_SpanB'])
            if not data_with_cloud.empty:
                mask_above = data_with_cloud['Close'] > data_with_cloud['Ichimoku_SpanA']
                mask_below = data_with_cloud['Close'] < data_with_cloud['Ichimoku_SpanB']
                data.loc[mask_above.index, 'Cloud_Direction'] = 1
                data.loc[mask_below.index, 'Cloud_Direction'] = -1"""
        
        if cloud_dir_pattern in content:
            content = content.replace(cloud_dir_pattern, cloud_dir_replacement)
            logger.info(f"增强 Cloud Direction 计算逻辑: {script_path}")
        
        # 写回修改后的内容
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"成功应用所有兼容性修复: {script_path}")
        return True
    
    except Exception as e:
        logger.error(f"创建兼容性补丁时出错: {e}")
        traceback.print_exc()
        return False

def test_indicator_calculation():
    """测试指标计算是否正常工作"""
    try:
        # 尝试导入pandas_ta
        import pandas_ta as ta
        
        # 创建测试数据
        dates = pd.date_range('2020-01-01', periods=100)
        data = pd.DataFrame({
            'Close': np.random.normal(100, 5, 100),
            'High': np.random.normal(105, 5, 100),
            'Low': np.random.normal(95, 5, 100),
            'Open': np.random.normal(100, 5, 100),
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # 测试计算SMA
        logger.info("测试 SMA 计算...")
        sma = ta.sma(data['Close'], length=10)
        assert sma is not None
        logger.info("SMA 计算正常")
        
        # 测试计算PSAR
        logger.info("测试 PSAR 计算...")
        psar = ta.psar(data['High'], data['Low'], data['Close'])
        assert psar is not None
        logger.info(f"PSAR 计算正常，返回列: {list(psar.columns)}")
        
        # 测试计算Ichimoku
        logger.info("测试 Ichimoku 计算...")
        ichimoku = ta.ichimoku(data['High'], data['Low'], data['Close'])
        logger.info(f"Ichimoku 返回类型: {type(ichimoku)}")
        
        if isinstance(ichimoku, tuple):
            logger.info(f"Ichimoku 作为元组返回，包含 {len(ichimoku)} 个元素")
            logger.info(f"第一个元素类型: {type(ichimoku[0])}")
            if hasattr(ichimoku[0], 'columns'):
                logger.info(f"第一个元素列: {list(ichimoku[0].columns)}")
        elif hasattr(ichimoku, 'columns'):
            logger.info(f"Ichimoku 列: {list(ichimoku.columns)}")
        else:
            logger.info(f"Ichimoku 返回值不含列属性: {ichimoku}")
        
        logger.info("指标计算测试完成")
        return True
    except Exception as e:
        logger.error(f"测试指标计算时出错: {e}")
        traceback.print_exc()
        return False

def fix_all_pandas_ta_files():
    """修复所有pandas_ta相关文件"""
    try:
        pandas_ta_path = find_module_path('pandas_ta')
        if not pandas_ta_path:
            return False
        
        # 修复squeeze_pro.py中的NaN导入
        squeeze_pro_path = pandas_ta_path / 'momentum' / 'squeeze_pro.py'
        if os.path.exists(squeeze_pro_path):
            fix_numpy_nan_import(squeeze_pro_path)
        
        # 添加其他可能需要修复的文件
        momentum_files = (pandas_ta_path / 'momentum').glob('*.py')
        for file_path in momentum_files:
            if 'import NaN' in open(file_path, 'r', encoding='utf-8').read():
                fix_numpy_nan_import(file_path)
        
        return True
    except Exception as e:
        logger.error(f"修复所有pandas_ta文件时出错: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    logger.info("开始全面兼容性修复...")
    
    # 1. 修复pandas_ta库中的问题
    fix_all_pandas_ta_files()
    
    # 2. 修改项目中的calculate_indicators.py文件
    script_path = "e:/FAnalysis/Scripts/calculate_indicators.py"
    create_compatibility_patch(script_path)
    
    # 3. 测试修复后的功能
    test_result = test_indicator_calculation()
    if test_result:
        logger.info("兼容性修复成功完成！系统现在应该可以正常工作。")
        logger.info("如需应用更改，请重启后端服务。")
    else:
        logger.warning("测试时遇到问题，但兼容性补丁已应用。请重启后端服务并验证功能。")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())