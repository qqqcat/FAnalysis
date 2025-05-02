# Financial Data Analysis and Visualization Platform  
## 金融数据分析与可视化平台  

## Project Overview  
This is a comprehensive financial data analysis system that includes data collection, indicator calculation, and visual report generation modules. It supports multi-language interface switching (Chinese/English).  

## 项目简介  
本项目为金融数据综合分析系统，包含数据采集、指标计算、可视化报告生成等模块，支持多语言界面切换（中/英文）。  

## Functional Modules  
### Backend Service (api/ directory)  
- Data API Service: `app.py` provides RESTful API  
- Dependency Management: `requirements.txt` defines Python dependencies  

### 后端服务（api/目录）  
- 数据接口服务：`app.py` 提供RESTful API  
- 依赖管理：`requirements.txt` 定义Python依赖  

### Frontend Application (web/ directory)  
- Visualization Dashboard: `Dashboard.js` main interface component  
- Chart Analysis Module: `ChartAnalysis.js` implements data visualization  
- Multi-language Support: `i18n.js` + `web/src/locales/` directory  

### 前端应用（web/目录）  
- 可视化仪表盘：`Dashboard.js` 主界面组件  
- 图表分析模块：`ChartAnalysis.js` 实现数据可视化  
- 多语言支持：`i18n.js` + `web/src/locales/` 目录  

### Data Processing Scripts (Scripts/ directory)  
- Indicator Calculation: `calculate_indicators.py`  
- Report Generation: `generate_html_report.py`  
- Data Format Fixing: `fix_data_format.py`  

### 数据处理脚本（Scripts/目录）  
- 指标计算：`calculate_indicators.py`  
- 报告生成：`generate_html_report.py`  
- 数据格式修复：`fix_data_format.py`  

### Template System (Templates/ directory)  
- Contains `interactive_report_template.html` and other report templates  

### 模板系统（Templates/目录）  
- 含`interactive_report_template.html`等报告模板  

## Deployment Steps  
### Environment Preparation  
- Install Python 3.8+ and Node.js 16+  
- Install dependencies:  
  ```bash
  cd e:\FAnalysis
  pip install -r api/requirements.txt
  cd web
  npm install
  ```

### 环境准备  
- 安装Python 3.8+ 和 Node.js 16+  
- 安装必要依赖：  
  ```bash
  cd e:\FAnalysis
  pip install -r api/requirements.txt
  cd web
  npm install
  ```

### Start Services  
- Backend Service:  
  ```bash
  start_backend.bat
  ```
- Frontend Development Server:  
  ```bash
  start_frontend.bat
  ```

### 启动服务  
- 后端服务：  
  ```bash
  start_backend.bat
  ```
- 前端开发服务器：  
  ```bash
  start_frontend.bat
  ```

### Data Processing Workflow  
1. Check data file integrity:  
   ```bash
   python check_data_files.py
   ```
2. Fix historical data format:  
   ```bash
   python fix_data_format.py
   ```
3. Generate analysis indicators:  
   ```bash
   python Scripts/calculate_indicators.py
   ```
4. Create visual reports:  
   ```bash
   python Scripts/generate_html_report.py
   ```

### 数据处理流程  
1. 检查数据文件完整性：  
   ```bash
   python check_data_files.py
   ```
2. 修复历史数据格式：  
   ```bash
   python fix_data_format.py
   ```
3. 生成分析指标：  
   ```bash
   python Scripts/calculate_indicators.py
   ```
4. 创建可视化报告：  
   ```bash
   python Scripts/generate_html_report.py
   ```

### Production Build  
- Build frontend static resources:  
  ```bash
  cd web
  npm run build
  ```
- Report output path: `Reports/` directory  

### 生产环境构建  
- 构建前端静态资源：  
  ```bash
  cd web
  npm run build
  ```
- 报告文件输出路径：`Reports/` 目录  

## File Structure Explanation  
```
├── api/                  # Backend service  
├── web/                  # Frontend application  
├── Scripts/              # Data processing scripts  
├── Templates/            # Report templates  
├── Reports/              # Auto-generated report output  
├── README.md             # This documentation file  
└── .gitignore            # Git ignore configuration  
```

## 文件结构说明  
```
├── api/                  # 后端服务  
├── web/                  # 前端应用  
├── Scripts/              # 数据处理脚本  
├── Templates/            # 报告模板  
├── Reports/              # 自动生成的报告输出  
├── README.md             # 本说明文件  
└── .gitignore            # Git忽略配置  
```

## Notes  
1. Environment variable configuration file: `web/.env` needs to be modified according to the actual deployment environment  
2. Data files are stored in the `Data/` directory and should be kept up-to-date with market data  
3. Use the original scripts in the `BackupScripts/` directory to roll back changes  

## 注意事项  
1. 环境变量配置文件：`web/.env` 需要根据实际部署环境修改  
2. 数据文件存放在`Data/`目录，需保持最新市场数据  
3. 使用`BackupScripts/`目录中的原始脚本可回滚变更
