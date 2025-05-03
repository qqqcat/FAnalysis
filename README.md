# Financial Data Analysis and Visualization Platform  
## 金融数据分析与可视化平台  

## Project Overview  
This is a comprehensive financial data analysis system that includes data collection, indicator calculation, and visual report generation modules. It supports multi-language interface switching (Chinese/English), provides advanced technical analysis capabilities with interactive charts and reports, and features a flexible parameter set management system for various trading strategies.

## 项目简介  
本项目为金融数据综合分析系统，包含数据采集、指标计算、可视化报告生成等模块。支持多语言界面切换（中/英文），提供先进的技术分析功能，包括交互式图表和报告，并具备灵活的参数集管理系统，适用于各种交易策略分析。

## Functional Modules  
### Backend Service (api/ directory)  
- Data API Service: `app.py` provides RESTful API for data access and analysis
- Indicator Calculation: Technical indicators and analytical methods using pandas-ta
- Interactive Chart Generation: Plotly-based HTML visualizations
- Report Generation: Dynamic HTML reports with multilingual support
- Parameter Set Management: Predefined and customizable indicator parameter sets

### 后端服务（api/目录）  
- 数据接口服务：`app.py` 提供RESTful API用于数据访问和分析
- 指标计算：基于pandas-ta的技术指标和分析方法
- 交互式图表生成：基于Plotly的HTML可视化
- 报告生成：支持多语言的动态HTML报告
- 参数集管理：预定义和可自定义的指标参数集

### Frontend Application (web/ directory)  
- Visualization Dashboard: `Dashboard.js` main interface component  
- Chart Analysis Module: `ChartAnalysis.js` implements data visualization  
- Multi-language Support: `i18n.js` + `web/src/locales/` directory  
- Parameter Configuration: Advanced settings for technical indicators
- Parameter Set Selector: Trading strategy preset configurations

### 前端应用（web/目录）  
- 可视化仪表盘：`Dashboard.js` 主界面组件  
- 图表分析模块：`ChartAnalysis.js` 实现数据可视化  
- 多语言支持：`i18n.js` + `web/src/locales/` 目录  
- 参数配置：技术指标的高级设置
- 参数集选择器：交易策略预设配置

### Data Processing Scripts (Scripts/ directory)  
- Indicator Calculation: `calculate_indicators.py` using pandas-ta library
- Chart Generation: `generate_charts.py` for static and interactive charts
- Report Generation: `generate_html_report.py`  
- Data Format Fixing: `fix_data_format.py` and `fix_gold_data.py`
- Data Fetching: `fetch_market_data.py` for downloading market data
- Test Scripts: `test_interactive_charts.py` for testing chart functionality
- Regeneration: `regenerate_reports.py` for batch regenerating reports

### 数据处理脚本（Scripts/目录）  
- 指标计算：`calculate_indicators.py` 使用pandas-ta库
- 图表生成：`generate_charts.py` 用于静态和交互式图表
- 报告生成：`generate_html_report.py`  
- 数据格式修复：`fix_data_format.py` 和 `fix_gold_data.py`
- 数据获取：`fetch_market_data.py` 用于下载市场数据
- 测试脚本：`test_interactive_charts.py` 用于测试图表功能
- 重新生成：`regenerate_reports.py` 用于批量重新生成报告

### Template System (Templates/ directory)  
- Contains `interactive_report_template.html` and other report templates  
- Supports multiple languages and dynamic content generation

### 模板系统（Templates/目录）  
- 含`interactive_report_template.html`等报告模板  
- 支持多语言和动态内容生成

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
- All-in-one launcher:
  ```bash
  python run.py both
  ```
- Backend Service Only:  
  ```bash
  python run.py backend
  # or use the batch file:
  start_backend.bat
  ```
- Frontend Development Server Only:  
  ```bash
  python run.py frontend
  # or use the batch file:
  start_frontend.bat
  ```

### 启动服务  
- 一键启动所有服务:
  ```bash
  python run.py both
  ```
- 仅启动后端服务：  
  ```bash
  python run.py backend
  # 或使用批处理文件:
  start_backend.bat
  ```
- 仅启动前端开发服务器：  
  ```bash
  python run.py frontend
  # 或使用批处理文件:
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
3. Generate charts and reports via API:
   - Access `http://localhost:5000/api/charts/<symbol>` for charts
   - Access `http://localhost:5000/api/generate_report/<symbol>` for reports
   - Example: `http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`

### 数据处理流程  
1. 检查数据文件完整性：  
   ```bash
   python check_data_files.py
   ```
2. 修复历史数据格式：  
   ```bash
   python fix_data_format.py
   ```
3. 通过API生成图表和报告:
   - 访问 `http://localhost:5000/api/charts/<symbol>` 获取图表
   - 访问 `http://localhost:5000/api/generate_report/<symbol>` 获取报告
   - 示例: `http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`

### Production Build  
- Build frontend static resources:  
  ```bash
  python run.py build
  # or manually:
  cd web
  npm run build
  ```
- After building, run backend only:
  ```bash
  python run.py backend
  ```
- Access the application at http://localhost:5000

### 生产环境构建  
- 构建前端静态资源：  
  ```bash
  python run.py build
  # 或手动执行:
  cd web
  npm run build
  ```
- 构建后，仅运行后端:
  ```bash
  python run.py backend
  ```
- 在 http://localhost:5000 访问应用

## Available Parameter Sets
The system supports various technical indicator parameter sets:
- `default`: Balanced indicator settings with comprehensive technical indicators
- `short_term`: Settings optimized for short-term analysis (5-20 day periods)
- `medium_term`: Settings for medium-term timeframes with 200-day moving averages
- `high_freq`: High-frequency trading indicators with multiple MACD configurations
- `tight_channel`: Narrow channel detection with 1.5 standard deviation Bollinger Bands
- `wide_channel`: Broad market trend detection with 2.5 standard deviation Bollinger Bands
- `trend_following`: Strong trend identification optimized for directional markets
- `momentum`: Momentum-based indicators for accelerating price movements
- `volatility`: Volatility measurement for range-bound markets
- `ichimoku`: Japanese Ichimoku cloud system for comprehensive price analysis

Each parameter set comes with optimized configurations for:
- Moving Averages (SMA/EMA with various periods)
- RSI (with appropriate lookback periods)
- MACD (with fast/slow/signal settings)
- Bollinger Bands (with length and standard deviation settings)
- Additional specialized indicators

## 可用参数集
系统支持多种技术指标参数集:
- `default`: 均衡指标设置，包含全面的技术指标
- `short_term`: 为短期分析优化的设置（5-20天周期）
- `medium_term`: 适用于中期时间框架的设置，含200日均线
- `high_freq`: 高频交易指标，含多种MACD配置
- `tight_channel`: 窄通道检测，使用1.5标准差布林带
- `wide_channel`: 广泛市场趋势检测，使用2.5标准差布林带
- `trend_following`: 强趋势识别，针对趋势性市场优化
- `momentum`: 基于动量的指标，适用于加速价格走势
- `volatility`: 波动性测量，适用于区间震荡市场
- `ichimoku`: 日本一目云系统，用于全面价格分析

每个参数集都包含针对以下指标的优化配置：
- 移动平均线（各周期的SMA/EMA）
- RSI（适当的回溯期）
- MACD（快线/慢线/信号线设置）
- 布林带（长度和标准差设置）
- 其他专业指标

## File Structure Explanation  
```
├── api/                  # Backend service  
│   ├── app.py            # Flask API server
│   └── requirements.txt  # Python dependencies
├── web/                  # Frontend application  
│   ├── src/              # React source code
│   ├── build/            # Production build output
│   └── package.json      # NPM dependencies
├── Scripts/              # Data processing scripts  
│   ├── calculate_indicators.py    # Technical indicator calculations
│   ├── generate_charts.py         # Chart generation
│   ├── generate_html_report.py    # Report generation
│   ├── fetch_market_data.py       # Market data download
│   └── BackupScripts/             # Original versions of modified scripts
├── Templates/            # Report templates  
├── Data/                 # Market data storage
├── Charts/               # Generated chart output  
├── Reports/              # Auto-generated report output  
├── run.py                # All-in-one launcher script
├── start_backend.bat     # Backend startup script
├── start_frontend.bat    # Frontend startup script
├── design.md             # Project design document
├── README.md             # This documentation file  
└── .gitignore            # Git ignore configuration  
```

## 文件结构说明  
```
├── api/                  # 后端服务  
│   ├── app.py            # Flask API服务器
│   └── requirements.txt  # Python依赖
├── web/                  # 前端应用  
│   ├── src/              # React源代码
│   ├── build/            # 生产环境构建输出
│   └── package.json      # NPM依赖
├── Scripts/              # 数据处理脚本  
│   ├── calculate_indicators.py    # 技术指标计算
│   ├── generate_charts.py         # 图表生成
│   ├── generate_html_report.py    # 报告生成
│   ├── fetch_market_data.py       # 市场数据下载
│   └── BackupScripts/             # 修改脚本的原始版本
├── Templates/            # 报告模板  
├── Data/                 # 市场数据存储
├── Charts/               # 生成的图表输出  
├── Reports/              # 自动生成的报告输出  
├── run.py                # 一体化启动脚本
├── start_backend.bat     # 后端启动脚本
├── start_frontend.bat     # 前端启动脚本
├── design.md             # 项目设计文档
├── README.md             # 本说明文件  
└── .gitignore            # Git忽略配置  
```

## Technical Improvements
Recent technical improvements to the system:

1. **Indicator Engine Upgrade**: Replaced custom implementation with pandas-ta library
   - Increased accuracy and reliability of calculations
   - Expanded available indicators from ~10 to 130+
   - Improved calculation performance

2. **Parameter Set Management**: Restructured using dictionary data structures
   - Enhanced extensibility and maintainability
   - More flexible parameter combinations
   - Structured configuration approach

3. **Chart System Enhancement**:
   - 重构图表生成模块，采用模块化设计方法
   - 将配置与实现分离，使用字典结构定义策略配置
   - 实现统一的样式管理系统，提高一致性
   - 优化错误处理机制，提供优雅的降级策略
   - 分离静态（Matplotlib）和交互式（Plotly）图表生成逻辑
   - 增加交互式缩放和平移功能
   - 支持多指标叠加显示
   - 针对移动设备查看进行了优化

4. **Report Generator Improvements** (in progress):
   - PDF export functionality under development
   - Machine learning analysis components planned
   - Custom report layout support coming soon

## 技术改进
系统最近的技术改进：

1. **指标引擎升级**：将自定义实现替换为pandas-ta库
   - 提高了计算的准确性和可靠性
   - 可用指标从约10个扩展到130+
   - 改进了计算性能

2. **参数集管理**：使用字典数据结构重构
   - 增强了可扩展性和可维护性
   - 更灵活的参数组合
   - 结构化配置方法

3. **图表系统增强**：
   - 重构图表生成模块，采用模块化设计方法
   - 将配置与实现分离，使用字典结构定义策略配置
   - 实现统一的样式管理系统，提高一致性
   - 优化错误处理机制，提供优雅的降级策略
   - 分离静态（Matplotlib）和交互式（Plotly）图表生成逻辑
   - 增加交互式缩放和平移功能
   - 支持多指标叠加显示
   - 针对移动设备查看进行了优化

4. **报告生成器改进**（进行中）：
   - 正在开发PDF导出功能
   - 计划添加机器学习分析组件
   - 即将支持自定义报告布局

## Notes  
1. Environment variable configuration file: `web/.env` needs to be modified according to the actual deployment environment  
2. Data files are stored in the `Data/` directory and should be kept up-to-date with market data  
3. Use `python run.py` as the primary way to start, build, and manage the application
4. Interactive charts are available in the `Charts/` directory with *_interactive_*.html filenames
5. For development, use `python run.py both` to start both frontend and backend together
6. To access different parameter sets, use the query parameter `parameter_sets` in API calls (e.g., `http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`)
7. Charts currently use fixed heights (850px). For better responsive behavior on different screen sizes, modify CSS in templates to use relative units (vh/%) and Flexbox/Grid layouts

## 注意事项  
1. 环境变量配置文件：`web/.env` 需要根据实际部署环境修改  
2. 数据文件存放在`Data/`目录，需保持最新市场数据  
3. 使用`python run.py`作为启动、构建和管理应用程序的主要方式
4. 交互式图表可在`Charts/`目录中找到，文件名包含*_interactive_*.html
5. 开发时，使用`python run.py both`同时启动前端和后端
6. 要访问不同的参数集，可在API调用中使用查询参数`parameter_sets`（例如：`http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`）
7. 图表当前使用固定高度（850px）。为了在不同屏幕尺寸上获得更好的响应式表现，请修改模板中的CSS，使用相对单位（vh/%）和Flexbox/Grid布局
