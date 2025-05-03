#!/usr/bin/env python
"""
修复pandas_ta库与NumPy最新版本的兼容性问题
适用于Python 3.13及以上版本

问题：pandas_ta库尝试从numpy导入大写的'NaN'，但在最新版本的NumPy中使用的是小写的'nan'
解决方案：修改受影响的文件，使用正确的导入语句
"""

import os
import sys
from pathlib import Path
import importlib.util
import shutil
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_pandas_ta_path():
    """查找pandas_ta库的安装路径"""
    try:
        spec = importlib.util.find_spec('pandas_ta')
        if spec is None:
            logger.error("找不到pandas_ta库，请确认它已安装")
            return None
        
        pandas_ta_path = Path(spec.origin).parent
        logger.info(f"找到pandas_ta安装路径: {pandas_ta_path}")
        return pandas_ta_path
    except Exception as e:
        logger.error(f"查找pandas_ta路径时出错: {e}")
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
        return False

def fix_numpy_nan_import(file_path):
    """修复文件中的numpy NaN导入"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换导入语句
        if 'from numpy import NaN as npNaN' in content:
            content = content.replace('from numpy import NaN as npNaN', 'from numpy import nan as npNaN')
            logger.info(f"替换导入语句: {file_path}")
            
            # 备份原文件
            if backup_file(file_path):
                # 写回修改后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"成功修复文件: {file_path}")
                return True
        else:
            logger.info(f"文件无需修复: {file_path}")
        
        return False
    except Exception as e:
        logger.error(f"修复文件时出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始修复pandas_ta库与NumPy的兼容性问题...")
    
    # 查找pandas_ta路径
    pandas_ta_path = find_pandas_ta_path()
    if not pandas_ta_path:
        return False
    
    # 需要检查的文件
    target_file = pandas_ta_path / 'momentum' / 'squeeze_pro.py'
    
    if not os.path.exists(target_file):
        logger.error(f"找不到目标文件: {target_file}")
        return False
    
    # 修复文件
    fixed = fix_numpy_nan_import(target_file)
    
    if fixed:
        logger.info("修复成功完成!")
        logger.info("现在应该可以正常使用pandas_ta库了")
        return True
    else:
        logger.warning("没有进行任何修复，或者修复过程中出现错误")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)