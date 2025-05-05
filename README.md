# Financial Data Analysis and Visualization Platform  
## 金融数据分析与可视化平台  

## Project Overview  
This is a comprehensive financial data analysis system that includes data collection, indicator calculation, and visual report generation modules. It supports multi-language interface switching (Chinese/English), provides advanced technical analysis capabilities with interactive charts and reports, and features a flexible parameter set management system for various trading strategies. The platform now supports analysis of forex, commodities, stock indices, cryptocurrencies, and sector ETFs.

## 项目简介  
本项目为金融数据综合分析系统，包含数据采集、指标计算、可视化报告生成等模块。支持多语言界面切换（中/英文），提供先进的技术分析功能，包括交互式图表和报告，并具备灵活的参数集管理系统，适用于各种交易策略分析。目前已支持外汇、大宗商品、股指、加密货币和行业ETF的全面分析。

## Functional Modules  
### Backend Service (api/ directory)  
- Data API Service: `app.py` provides RESTful API for data access and analysis
- Indicator Calculation: Technical indicators and analytical methods using pandas-ta
- Interactive Chart Generation: Plotly-based HTML visualizations
- Report Generation: Dynamic HTML reports with multilingual support
- Parameter Set Management: Predefined and customizable indicator parameter sets
- WebSocket Integration: Real-time data streaming support with Socket.IO

### 后端服务（api/目录）  
- 数据接口服务：`app.py` 提供RESTful API用于数据访问和分析
- 指标计算：基于pandas-ta的技术指标和分析方法
- 交互式图表生成：基于Plotly的HTML可视化
- 报告生成：支持多语言的动态HTML报告
- 参数集管理：预定义和可自定义的指标参数集
- WebSocket集成：基于Socket.IO的实时数据流支持

### Frontend Application (web/ directory)  
- Visualization Dashboard: `Dashboard.js` main interface component  
- Chart Analysis Module: `ChartAnalysis.js` implements data visualization  
- Multi-language Support: `i18n.js` + `web/src/locales/` directory  
- Parameter Configuration: Advanced settings for technical indicators
- Parameter Set Selector: Trading strategy preset configurations
- Real-time Data Handling: WebSocket client for live updates

### 前端应用（web/目录）  
- 可视化仪表盘：`Dashboard.js` 主界面组件  
- 图表分析模块：`ChartAnalysis.js` 实现数据可视化  
- 多语言支持：`i18n.js` + `web/src/locales/` 目录  
- 参数配置：技术指标的高级设置
- 参数集选择器：交易策略预设配置
- 实时数据处理：WebSocket客户端实现实时更新

### Data Processing Scripts (Scripts/ directory)  
- Indicator Calculation: `calculate_indicators.py` using pandas-ta library
- Chart Generation: `generate_charts.py` for static and interactive charts
- Report Generation: `generate_html_report.py`  
- Data Format Fixing: `fix_data_format.py` and `fix_gold_data.py`
- Data Fetching: `fetch_market_data.py` for downloading market data
- Test Scripts: `test_interactive_charts.py` for testing chart functionality
- Regeneration: `regenerate_reports.py` for batch regenerating reports
- Multi-source Data: Support for Yahoo Finance, Alpha Vantage, and local files

### 数据处理脚本（Scripts/目录）  
- 指标计算：`calculate_indicators.py` 使用pandas-ta库
- 图表生成：`generate_charts.py` 用于静态和交互式图表
- 报告生成：`generate_html_report.py`  
- 数据格式修复：`fix_data_format.py` 和 `fix_gold_data.py`
- 数据获取：`fetch_market_data.py` 用于下载市场数据
- 测试脚本：`test_interactive_charts.py` 用于测试图表功能
- 重新生成：`regenerate_reports.py` 用于批量重新生成报告
- 多源数据：支持Yahoo Finance、Alpha Vantage和本地文件

### Template System (Templates/ directory)  
- Contains `interactive_report_template.html` and other report templates  
- Supports multiple languages and dynamic content generation
- Enhanced responsive design for various devices

### 模板系统（Templates/目录）  
- 含`interactive_report_template.html`等报告模板  
- 支持多语言和动态内容生成
- 增强的响应式设计，适配各种设备

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

## Supported Asset Types
The platform now supports analysis of the following asset classes:

### Forex
Major currency pairs including EURUSD, GBPUSD, AUDUSD, USDJPY, and others.

### Commodities
Gold, Silver, Oil, Copper, Natural Gas, and other major commodities.

### Stock Indices
Global market indices including:
- US markets: S&P 500, Dow Jones, NASDAQ, Russell 2000
- Asian markets: Hang Seng, Shanghai Composite, Nikkei 225, KOSPI
- European markets: FTSE 100, DAX, CAC 40, STOXX50E
- Other global markets: Australia, Brazil, Canada, Mexico, and more

### Cryptocurrencies
Major digital currencies including Bitcoin, Ethereum, Binance Coin, Ripple, Cardano, Solana, and others.

### Sector ETFs
SPDR sector ETFs for industry-specific analysis, including Financial, Energy, Technology, Healthcare, and others.

### Agricultural Futures
Major agricultural products including Corn, Wheat, Soybeans, Coffee, Sugar, Cotton, and more.

## 支持的资产类型
平台现已支持以下资产类别的分析：

### 外汇
主要货币对包括欧元/美元、英镑/美元、澳元/美元、美元/日元等。

### 大宗商品
黄金、白银、原油、铜、天然气和其他主要商品。

### 股票指数
全球市场指数，包括：
- 美国市场：标普500、道琼斯、纳斯达克、罗素2000
- 亚洲市场：恒生指数、上海综合指数、日经225、韩国KOSPI指数
- 欧洲市场：富时100、德国DAX、法国CAC 40、欧洲斯托克50
- 其他全球市场：澳大利亚、巴西、加拿大、墨西哥等

### 加密货币
主要数字货币包括比特币、以太坊、币安币、瑞波币、艾达币、索拉纳等。

### 行业ETF
SPDR行业ETF提供行业细分分析，包括金融、能源、科技、医疗保健等。

### 农产品期货
主要农产品包括玉米、小麦、大豆、咖啡、糖、棉花等。

## File Structure Explanation  
```
├── api/                  # Backend service  
│   ├── app.py            # Flask API server
│   └── requirements.txt  # Python dependencies
├── web/                  # Frontend application  
│   ├── src/              # React source code
│   │   ├── components/   # React components
│   │   │   ├── ChartAnalysis.js    # Enhanced chart analysis component
│   │   │   └── Dashboard.js        # Main dashboard interface
│   │   └── locales/      # Internationalization resources
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
│   └── Symbols/          # Symbol definitions and configurations
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
│   │   ├── components/   # React组件
│   │   │   ├── ChartAnalysis.js    # 增强的图表分析组件
│   │   │   └── Dashboard.js        # 主仪表盘界面
│   │   └── locales/      # 国际化资源
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
│   └── Symbols/          # 符号定义和配置
├── Charts/               # 生成的图表输出  
├── Reports/              # 自动生成的报告输出  
├── run.py                # 一体化启动脚本
├── start_backend.bat     # 后端启动脚本
├── start_frontend.bat    # 前端启动脚本
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
   - Modular redesign of chart generation module
   - Separation of configuration and implementation using dictionary-based strategy configuration
   - Unified styling management system for greater consistency
   - Enhanced error handling with graceful degradation
   - Significantly improved ChartAnalysis.js frontend component with:
     - Organized indicator grouping by function (main plot/oscillators/MACD/Bollinger/volume)
     - Optimized multi-pane layout with better space allocation
     - Centralized styling system with consistent color schemes
     - Enhanced interactive features (zoom, pan, hover data)
     - Better error handling and empty state management
   - Separate static (Matplotlib) and interactive (Plotly) chart generation logic
   - Added interactive zoom and pan capabilities
   - Support for multiple indicator overlay display
   - Optimized for mobile device viewing

4. **Report Generator Improvements** (in progress):
   - PDF export functionality under development
   - Machine learning analysis components planned
   - Custom report layout support coming soon

5. **Frontend UI Enhancements**:
   - Redesigned parameter selection controls
   - More intuitive time range selector
   - Implemented report quick-access functionality
   - Responsive layout optimizations for various screen sizes
   - Improved loading states and error notifications
   - Smoother interface transitions

6. **Extended Asset Support**:
   - Added support for cryptocurrencies with specialized indicators
   - Expanded global market index coverage
   - Added SPDR sector ETF analysis
   - Included agricultural futures with seasonal analysis tools

7. **Real-time Data Updates**:
   - WebSocket integration for live market data
   - Socket.IO backend implementation
   - Optimized data streaming for bandwidth efficiency
   - Dynamic chart updates without page refresh

8. **Data Source Diversification**:
   - Added Alpha Vantage API integration
   - Enhanced Yahoo Finance data fetching
   - Support for local CSV/Excel data imports
   - Automatic fallback mechanism between data sources

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
   - 图表生成模块的模块化重新设计
   - 使用基于字典的策略配置将配置与实现分离
   - 统一的样式管理系统，提高一致性
   - 增强的错误处理机制，实现优雅降级
   - 显著改进的ChartAnalysis.js前端组件：
     - 按功能组织指标分组（主图/震荡指标/MACD/布林带/成交量）
     - 优化的多窗格布局，更合理的空间分配
     - 集中式样式系统，统一的配色方案
     - 增强的交互功能（缩放、平移、悬停数据）
     - 更好的错误处理和空状态管理
   - 分离静态（Matplotlib）和交互式（Plotly）图表生成逻辑
   - 增加交互式缩放和平移功能
   - 支持多指标叠加显示
   - 针对移动设备查看进行了优化

4. **报告生成器改进**（进行中）：
   - 正在开发PDF导出功能
   - 计划添加机器学习分析组件
   - 即将支持自定义报告布局

5. **前端UI增强**：
   - 重新设计的参数选择控件
   - 更直观的时间范围选择器
   - 实现了报告快速访问功能
   - 针对各种屏幕尺寸的响应式布局优化
   - 改进的加载状态和错误通知
   - 更流畅的界面过渡效果

6. **扩展资产支持**：
   - 增加了加密货币专用指标支持
   - 扩展了全球市场指数覆盖范围
   - 增加了SPDR行业ETF分析
   - 包含了具有季节性分析工具的农产品期货

7. **实时数据更新**：
   - 集成WebSocket实现实时市场数据
   - Socket.IO后端实现
   - 优化数据流传输，提高带宽效率
   - 无需刷新页面的动态图表更新

8. **数据源多样化**：
   - 增加了Alpha Vantage API集成
   - 增强了Yahoo Finance数据获取
   - 支持本地CSV/Excel数据导入
   - 数据源之间的自动降级机制

## Future Development Plans
Looking ahead, the project has the following planned enhancements:

1. **Machine Learning Integration**:
   - Predictive model components for price forecasting
   - Anomaly detection for unusual market patterns
   - Sentiment analysis indicators from news sources
   - Pattern recognition for classic chart formations

2. **Community Features**:
   - Report sharing functionality
   - User parameter set sharing mechanism
   - Comments and discussion system
   - Collaborative analysis tools

3. **Advanced Subscription Services**:
   - Professional feature set design
   - API access permission mechanisms
   - Automated report subscription service
   - Premium indicator packages

4. **Mobile Application**:
   - Native mobile app development
   - Push notifications for key market events
   - Optimized mobile interface for on-the-go analysis
   - Offline capability for report viewing

5. **Expanded Data Integration**:
   - Additional data source connections
   - Economic calendar integration
   - News feed correlation with price movements
   - Fundamental data overlay on technical charts

## 未来发展计划
展望未来，项目有以下计划的增强功能：

1. **机器学习集成**：
   - 价格预测的预测模型组件
   - 异常市场模式检测
   - 来自新闻源的情绪分析指标
   - 经典图表形态的模式识别

2. **社区功能**：
   - 报告分享功能
   - 用户参数集共享机制
   - 评论和讨论系统
   - 协作分析工具

3. **高级订阅服务**：
   - 专业功能集设计
   - API访问权限机制
   - 自动化报告订阅服务
   - 高级指标包

4. **移动应用**：
   - 原生移动应用开发
   - 关键市场事件的推送通知
   - 针对移动分析优化的界面
   - 报告查看的离线功能

5. **扩展数据集成**：
   - 额外数据源连接
   - 经济日历集成
   - 新闻提要与价格走势的相关性
   - 技术图表上的基本面数据叠加

## Notes  
1. Environment variable configuration file: `web/.env` needs to be modified according to the actual deployment environment  
2. Data files are stored in the `Data/` directory and should be kept up-to-date with market data  
3. Use `python run.py` as the primary way to start, build, and manage the application
4. Interactive charts are available in the `Charts/` directory with *_interactive_*.html filenames
5. For development, use `python run.py both` to start both frontend and backend together
6. To access different parameter sets, use the query parameter `parameter_sets` in API calls (e.g., `http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`)
7. Charts currently use fixed heights (850px). For better responsive behavior on different screen sizes, modify CSS in templates to use relative units (vh/%) and Flexbox/Grid layouts
8. WebSocket functionality is now available for real-time data, requires both backend and frontend running simultaneously
9. New report format with enhanced interactivity is available by adding `format=enhanced` to the report API calls

## 注意事项  
1. 环境变量配置文件：`web/.env` 需要根据实际部署环境修改  
2. 数据文件存放在`Data/`目录，需保持最新市场数据  
3. 使用`python run.py`作为启动、构建和管理应用程序的主要方式
4. 交互式图表可在`Charts/`目录中找到，文件名包含*_interactive_*.html
5. 开发时，使用`python run.py both`同时启动前端和后端
6. 要访问不同的参数集，可在API调用中使用查询参数`parameter_sets`（例如：`http://localhost:5000/api/charts/EURUSD?parameter_sets=default,trend_following`）
7. 图表当前使用固定高度（850px）。为了在不同屏幕尺寸上获得更好的响应式表现，请修改模板中的CSS，使用相对单位（vh/%）和Flexbox/Grid布局
8. WebSocket实时数据功能现已可用，需要同时运行后端和前端
9. 通过在报告API调用中添加`format=enhanced`可使用具有增强交互性的新报告格式
