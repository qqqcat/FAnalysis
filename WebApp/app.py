import os
import sys
import time
import threading
import json
from datetime import datetime
import traceback
import shutil  # Added for file operations
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory

# Add the parent directory to sys.path to import from Scripts folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix existing GOLD report if it exists
reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
gold_report_old = os.path.join(reports_dir, "GOLD_report_20250501.html")
gold_report_new = os.path.join(reports_dir, "GOLD_Beautiful_Report_20250501.html")
if os.path.exists(gold_report_old) and not os.path.exists(gold_report_new):
    try:
        shutil.copy2(gold_report_old, gold_report_new)
        print(f"Successfully renamed GOLD report to the correct format: {gold_report_new}")
    except Exception as e:
        print(f"Error renaming GOLD report: {str(e)}")

from Scripts.fetch_market_data import fetch_data
from Scripts.calculate_indicators import calculate_indicators, load_data
from Scripts.generate_html_report import generate_html_report

app = Flask(__name__)
app.secret_key = 'financial_analysis_secret_key'  # Required for flash messages and sessions

# Store report generation progress
report_generation_tasks = {}

# 多语言翻译字典
TRANSLATIONS = {
    'en': {
        # 导航栏
        'nav_title': 'Financial Analysis Dashboard',
        'help': 'Help',
        'language': 'Language',
        'home': 'Home',
        
        # 生成报告区域
        'generate_new_analysis': 'Generate New Analysis',
        'product_type': 'Product Type',
        'currency_pairs': 'Currency Pairs',
        'indices': 'Indices',
        'commodities': 'Commodities',
        'select_product': 'Select Product',
        'date_label': 'Date (YYYYMMDD)',
        'date_format_help': 'Enter date in format: YYYYMMDD (e.g., 20250430) or use the calendar picker',
        'generate_report': 'Generate Report',
        
        # 查看报告区域
        'view_existing_reports': 'View Existing Reports',
        'latest_reports': 'Latest Reports',
        'all_reports': 'All Reports',
        'view_latest': 'View Latest',
        'no_reports': 'No Reports',
        'no_existing_reports': 'No existing reports found.',
        'date': 'Date',
        'product': 'Product',
        'view': 'View',
        
        # 帮助模态框
        'how_to_use': 'How to Use This Tool',
        'generate_new_report': 'Generate a New Report',
        'supported_products': 'Supported Products:',
        'currency_pairs_desc': 'Currency Pairs: EURUSD, GBPUSD, USDJPY, and more',
        'indices_desc': 'Indices: S&P500, NASDAQ, DOW, and others',
        'commodities_desc': 'Commodities: GOLD, OIL, SILVER, WHEAT, CORN, COTTON, COFFEE',
        'close': 'Close',
        
        # 报告页面特定术语
        'report': 'Report',
        'generate_other_reports': 'Generate Other Reports',
        'click_to_generate': 'Click to Generate',
        'click_to_scroll': 'Click to Scroll',
        'generate_detailed_report_now': 'Generate Detailed Report Now',
        'return_to_home': 'Return to Home',
        'report_is_being_generated': 'Report for {product} is being generated',
        'please_wait_for_analysis': 'Please wait while we analyze the data and prepare your report...',
        'generate_detailed_analysis_report': 'Generate Detailed Analysis Report',
        'continue_iteration': 'Continue to iterate?',
        
        # 页脚
        'footer_text': 'Financial Analysis System © 2025'
    },
    'zh': {
        # 导航栏
        'nav_title': '金融分析仪表盘',
        'help': '帮助',
        'language': '语言',
        'home': '首页',
        
        # 生成报告区域
        'generate_new_analysis': '生成新分析',
        'product_type': '产品类型',
        'currency_pairs': '货币对',
        'indices': '指数',
        'commodities': '商品',
        'select_product': '选择产品',
        'date_label': '日期 (YYYYMMDD)',
        'date_format_help': '输入日期格式: YYYYMMDD (例如, 20250430) 或使用日历选择',
        'generate_report': '生成报告',
        
        # 查看报告区域
        'view_existing_reports': '查看现有报告',
        'latest_reports': '最新报告',
        'all_reports': '所有报告',
        'view_latest': '查看最新',
        'no_reports': '无报告',
        'no_existing_reports': '未找到现有报告。',
        'date': '日期',
        'product': '产品',
        'view': '查看',
        
        # 帮助模态框
        'how_to_use': '如何使用此工具',
        'generate_new_report': '生成新报告',
        'supported_products': '支持的产品:',
        'currency_pairs_desc': '货币对: EURUSD, GBPUSD, USDJPY等',
        'indices_desc': '指数: S&P500, NASDAQ, DOW等',
        'commodities_desc': '商品: 黄金, 石油, 白银, 小麦, 玉米, 棉花, 咖啡',
        'close': '关闭',
        
        # 报告页面特定术语
        'report': '报告',
        'generate_other_reports': '生成其他报告',
        'click_to_generate': '点击生成',
        'click_to_scroll': '点击滚动',
        'generate_detailed_report_now': '立即生成详细报告',
        'return_to_home': '返回首页',
        'report_is_being_generated': '{product} 的报告正在生成中',
        'please_wait_for_analysis': '请稍候，我们正在分析数据并准备您的报告...',
        'generate_detailed_analysis_report': '生成详细分析报告',
        'continue_iteration': '继续迭代?',
        
        # 页脚
        'footer_text': '金融分析系统 © 2025'
    }
}

# Define supported product types and their display names
PRODUCT_TYPES = {
    'CURRENCY_PAIRS': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'],
    'INDICES': ['S&P500', 'NASDAQ', 'DOW', 'FTSE', 'DAX'],
    'COMMODITIES': ['GOLD', 'OIL', 'SILVER', 'WHEAT', 'CORN', 'COTTON', 'COFFEE']
}

def get_translation(key, lang=None, **format_args):
    """获取翻译并支持字符串格式化参数"""
    if not lang:
        lang = session.get('language', 'en')
    translation = TRANSLATIONS.get(lang, {}).get(key, key)
    # 如果有格式化参数，应用它们
    if format_args and '{' in translation:
        try:
            return translation.format(**format_args)
        except KeyError:
            # 如果格式化失败，返回原始翻译
            return translation
    return translation

# 创建一个Jinja2过滤器，专门用于在模板中处理带参数的翻译
def template_translation(key, **kwargs):
    """专为模板设计的翻译函数，支持关键字参数"""
    return get_translation(key, **kwargs)

# Register Jinja2 template filter for t function
@app.template_filter('t')
def translate_filter(key, **kwargs):
    return get_translation(key, **kwargs)

# Register the 't' function directly in the template context
@app.context_processor
def utility_processor():
    def t(key, **kwargs):
        # Extract 'product' or other parameters from kwargs if they exist
        # and pass them correctly as format_args to get_translation
        format_args = {}
        lang = None
        
        # Handle specific parameters
        if 'lang' in kwargs:
            lang = kwargs.pop('lang')
        
        # Any other kwargs are considered format arguments
        format_args.update(kwargs)
        
        return get_translation(key, lang=lang, **format_args)
    return {'t': t}

@app.route('/set_language/<lang>')
def set_language(lang):
    """设置语言并返回上一页"""
    if lang in TRANSLATIONS:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    # Get language preference from session or query param
    lang = request.args.get('lang', session.get('language', 'en'))
    if lang in TRANSLATIONS:
        session['language'] = lang
    else:
        lang = 'en'
        session['language'] = lang
    
    # Get available products and organize by category
    products = []
    for category, items in PRODUCT_TYPES.items():
        products.extend(items)
    
    # Get available dates from Reports directory
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
    available_dates = set()
    product_dates = {}  # Track which dates are available for each product
    unique_products = set()  # Track unique products that have reports
    
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            if filename.endswith('.html') and 'Beautiful_Report' in filename:
                parts = filename.split('_')
                if len(parts) >= 3:
                    product = parts[0]  # Extract product name
                    unique_products.add(product)
                    
                    # Extract date (last part before .html extension)
                    date_str = parts[-1].split('.')[0]
                    try:
                        # Validate date format is YYYYMMDD
                        datetime.strptime(date_str, "%Y%m%d")
                        available_dates.add(date_str)
                        
                        # Add date to product's list of dates
                        if product not in product_dates:
                            product_dates[product] = []
                        product_dates[product].append(date_str)
                    except ValueError:
                        continue
    
    # Sort dates for each product
    for product in product_dates:
        product_dates[product] = sorted(product_dates[product], reverse=True)
    
    # Sort all dates and products
    available_dates = sorted(list(available_dates), reverse=True)
    unique_products = sorted(list(unique_products))
    
    # Get current date for form default value
    date_today = datetime.now().strftime("%Y%m%d")
    
    return render_template('index.html', 
                          products=products, 
                          dates=available_dates,
                          unique_products=unique_products,
                          product_dates=product_dates,
                          date_today=date_today,
                          t=get_translation,
                          lang=lang)

def generate_report_task_with_iteration(product, date, report_type, task_id):
    """Enhanced version of generate_report_task that improves on existing reports when iterating."""
    try:
        task_info = report_generation_tasks[task_id]
        is_iteration = task_info.get('is_iteration', False)
        iteration_source = task_info.get('iteration_source')
        
        # Update task status
        report_generation_tasks[task_id]['status'] = 'in_progress'
        report_generation_tasks[task_id]['progress'] = 10
        report_generation_tasks[task_id]['message'] = 'Analyzing existing report and fetching additional market data...'
        
        # For iterations, we'll use the existing data but enhance the analysis
        if is_iteration and iteration_source and os.path.exists(iteration_source):
            print(f"Performing iteration on existing report for {product} on {date}")
        
        # Continue with normal report generation steps
        # Step 1: Fetch market data (same as before, but with enhanced history for iterations)
        try:
            # Get the script directory
            script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Scripts")
            data_dir = os.path.join(os.path.dirname(script_dir), "Data")
            
            # Ensure the data directory exists
            os.makedirs(data_dir, exist_ok=True)
            
            print(f"Fetching {'enhanced' if is_iteration else 'standard'} data for {product} on {date}")
            
            # 使用正确的参数调用fetch_data函数
            data = fetch_data(product, date)
            
            if data is None:
                raise Exception(f"Failed to fetch data for {product} on {date}")
            
            # Save the data to a CSV file
            # Clean symbol for filename (remove =X or =F if present)
            clean_symbol = product.split('=')[0]
            file_suffix = "_enhanced" if is_iteration else ""
            file_path = os.path.join(data_dir, f"{clean_symbol}_{date}{file_suffix}.csv")
            data.to_csv(file_path)
            data_file_path = file_path
            print(f"Data saved to {file_path}")
            
            # Check if the data file exists after fetching
            if not os.path.exists(data_file_path):
                raise FileNotFoundError(f"Failed to create data file for {product} on {date}")
                
            report_generation_tasks[task_id]['data_file'] = data_file_path
            
        except Exception as e:
            report_generation_tasks[task_id]['status'] = 'failed'
            report_generation_tasks[task_id]['message'] = f'Market data fetch failed: {str(e)}'
            print(f"Error fetching market data: {str(e)}")
            return
        
        report_generation_tasks[task_id]['progress'] = 40
        report_generation_tasks[task_id]['message'] = 'Calculating indicators with enhanced analysis...'
        
        # Step 2: Calculate indicators with enhanced parameters for iterations
        try:
            # Verify the data file exists
            data_file = report_generation_tasks[task_id].get('data_file')
            if not data_file or not os.path.exists(data_file):
                raise FileNotFoundError(f"Data file for {product} on {date} not found")
                
            print(f"Calculating {'enhanced' if is_iteration else 'standard'} indicators for {product}")
            
            # Load the data first
            try:
                market_data = load_data(data_file)
                
                # Make sure market_data is not None and has data
                if market_data is None or len(market_data) == 0:
                    raise ValueError(f"Market data loaded from {data_file} is empty")
                
                # Now calculate indicators using our loaded data
                print(f"Loaded market data shape: {market_data.shape}")
                
                # Calculate indicators and save them
                reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
                charts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Charts")
                
                # Ensure directories exist
                os.makedirs(reports_dir, exist_ok=True)
                os.makedirs(charts_dir, exist_ok=True)
                
                # Import necessary functions
                from Scripts.calculate_indicators import calculate_indicators, generate_report, plot_indicators
                
                # For iterations, use enhanced analysis parameters
                if is_iteration:
                    # Calculate indicators with additional technical indicators and more complex analysis
                    data_with_indicators = calculate_indicators(
                        market_data, 
                        use_enhanced_analysis=True,
                        include_additional_indicators=True
                    )
                    
                    # Generate an enhanced report with more detailed analysis
                    generate_report(
                        data_with_indicators, 
                        product, 
                        reports_dir, 
                        report_date=date,
                        enhanced_analysis=True
                    )
                    
                    # Generate enhanced charts with more visualization options
                    plot_indicators(
                        data_with_indicators, 
                        product, 
                        charts_dir, 
                        chart_date=date, 
                        strategy="advanced"
                    )
                else:
                    # Use standard analysis for normal reports
                    data_with_indicators = calculate_indicators(market_data)
                    generate_report(data_with_indicators, product, reports_dir, report_date=date)
                    plot_indicators(data_with_indicators, product, charts_dir, chart_date=date, strategy="default")
                
            except Exception as calc_error:
                print(f"Error during indicator calculation: {str(calc_error)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise calc_error
            
        except Exception as e:
            report_generation_tasks[task_id]['status'] = 'failed'
            report_generation_tasks[task_id]['message'] = f'Indicator calculation failed: {str(e)}'
            print(f"Error calculating indicators: {str(e)}")
            return
        
        report_generation_tasks[task_id]['progress'] = 70
        report_generation_tasks[task_id]['message'] = 'Generating enhanced final report...'
        
        # Step 3: Generate HTML report with the enhanced report type for iterations
        try:
            # Check if the indicator report exists
            indicator_report = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                          "Reports", f"{product}_indicator_report_{date}.txt")
            
            # 增加更详细的文件和路径检查
            print(f"正在查找指标报告文件: {indicator_report}")
            
            # 检查Reports目录中所有文件
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
            print(f"Reports目录路径: {reports_dir}")
            if os.path.exists(reports_dir):
                files = os.listdir(reports_dir)
                print(f"Reports目录中的文件: {files}")
            
            if not os.path.exists(indicator_report):
                # 尝试使用不同的路径
                alt_indicator_report = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "Reports", f"{product}_indicator_report_{date}.txt")
                print(f"尝试替代路径: {alt_indicator_report}")
                
                if os.path.exists(alt_indicator_report):
                    print(f"在替代路径找到指标报告文件")
                    indicator_report = alt_indicator_report
                else:
                    # 如果没有找到指标报告，尝试创建一个空白的指标报告文件
                    print(f"未找到指标报告文件，创建空白文件")
                    os.makedirs(os.path.dirname(indicator_report), exist_ok=True)
                    with open(indicator_report, 'w', encoding='utf-8') as f:
                        f.write(f"# {product} Technical Indicator Report\n# Date: {date}")
            else:
                print(f"找到指标报告文件: {indicator_report}")
                
            # Get the user's selected language from the task info
            language = report_generation_tasks[task_id].get('language', 'zh')
            
            # For iterations, create an improved report with more detailed analysis
            enhanced_report_type = 'enhanced' if is_iteration else report_type
            
            print(f"Generating {'enhanced' if is_iteration else 'standard'} report in language: {language}")
            
            # 修改generate_html_report的调用，增加详细日志
            try:
                print(f"调用generate_html_report函数，参数: symbol={product}, report_date={date}, language={language}")
                report_file = generate_html_report(
                    product, 
                    date, 
                    output_dir=reports_dir,  # 明确指定输出目录
                    language=language
                )
                print(f"报告生成成功: {report_file}")
            except Exception as gen_error:
                print(f"报告生成期间发生异常: {str(gen_error)}")
                print(f"异常详情: {traceback.format_exc()}")
                raise gen_error
            
        except Exception as e:
            report_generation_tasks[task_id]['status'] = 'failed'
            report_generation_tasks[task_id]['message'] = f'Report generation failed: {str(e)}'
            print(f"Error generating HTML report: {str(e)}")
            print(f"详细错误信息: {traceback.format_exc()}")
            return
        
        # 验证报告文件是否已创建 - 增强版
        report_filename = f"{product}_Beautiful_Report_{date}.html"
        
        # 定义多个可能的报告路径
        possible_report_paths = [
            os.path.join(reports_dir, report_filename),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports", report_filename),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Scripts", "Reports", report_filename),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reports", report_filename)
        ]
        
        # 添加重试机制
        max_retries = 3
        retry_delay = 1  # 秒
        report_found = False
        
        for attempt in range(max_retries):
            for path in possible_report_paths:
                print(f"检查报告文件路径 (尝试 {attempt+1}/{max_retries}): {path}")
                if os.path.exists(path):
                    print(f"找到报告文件: {path}")
                    report_found = True
                    report_path = path
                    break
            
            if report_found:
                break
                
            if attempt < max_retries - 1:
                print(f"报告文件未找到，等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
        
        if not report_found:
            report_generation_tasks[task_id]['status'] = 'failed'
            report_generation_tasks[task_id]['message'] = 'Report file was not created. Check the server logs for details.'
            print(f"错误：无法找到生成的报告文件。已尝试以下路径：{possible_report_paths}")
            return
        
        # 如果报告找到但不在预期位置，复制到标准位置
        standard_path = os.path.join(reports_dir, report_filename)
        if report_found and report_path != standard_path:
            print(f"报告文件在非标准位置找到，正在复制到标准位置: {standard_path}")
            try:
                shutil.copy2(report_path, standard_path)
                print(f"成功复制报告到标准位置")
            except Exception as copy_error:
                print(f"复制报告文件失败: {str(copy_error)}")
                # 继续处理，因为我们已经找到了报告文件
        
        report_generation_tasks[task_id]['progress'] = 100
        report_generation_tasks[task_id]['status'] = 'completed'
        report_generation_tasks[task_id]['message'] = 'Enhanced report generation complete!'
        
    except Exception as e:
        report_generation_tasks[task_id]['status'] = 'failed'
        report_generation_tasks[task_id]['message'] = f'Error: {str(e)}'
        print(f"Unexpected error in report generation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

@app.route('/generate_report', methods=['POST'])
def generate_report():
    product = request.form.get('product')
    date = request.form.get('date')
    report_type = request.form.get('report_type', 'detailed')
    force_regenerate = request.form.get('force_regenerate', 'false').lower() == 'true'
    
    # Get current language preference
    language = session.get('language', 'zh')
    
    if not product or not date:
        flash('Please provide both product and date', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Validate date format
        date_obj = datetime.strptime(date, "%Y%m%d")
        
        # Check if the date is in the future
        if date_obj > datetime.now():
            flash(f'Cannot generate report for future date: {date}', 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid date format. Please use YYYYMMDD format', 'danger')
        return redirect(url_for('index'))
    
    # Check if product is supported
    all_products = []
    for category, items in PRODUCT_TYPES.items():
        all_products.extend(items)
    
    if product not in all_products:
        flash(f'Unsupported product: {product}', 'danger')
        return redirect(url_for('index'))
    
    # Check if report already exists
    report_filename = f"{product}_Beautiful_Report_{date}.html"
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "Reports", report_filename)
    
    # If report exists and force_regenerate is not true, show existing report directly
    if os.path.exists(report_path) and not force_regenerate:
        return redirect(url_for('view_report', product=product, date=date))
    
    # Clear any old task for this product/date combination
    for task_id in list(report_generation_tasks.keys()):
        task = report_generation_tasks[task_id]
        if task.get('product') == product and task.get('date') == date:
            del report_generation_tasks[task_id]
    
    # Start asynchronous report generation
    task_id = f"{product}_{date}_{int(time.time())}"
    report_generation_tasks[task_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing report generation...',
        'product': product,
        'date': date,
        'report_type': report_type,
        'language': language,  # Store language setting
        'is_iteration': False  # This is a standard report, not an iteration
    }
    
    # Store task_id in session for progress tracking
    session['current_task_id'] = task_id
    
    # Start background task using the new enhanced function
    thread = threading.Thread(
        target=generate_report_task_with_iteration, 
        args=(product, date, report_type, task_id)
    )
    thread.daemon = True
    thread.start()
    
    # Redirect to the report page with a flag to show progress
    return redirect(url_for('view_report', product=product, date=date, generating=True))

@app.route('/report_progress')
def report_progress():
    """Endpoint to check report generation progress."""
    task_id = session.get('current_task_id')
    if task_id and task_id in report_generation_tasks:
        return jsonify(report_generation_tasks[task_id])
    return jsonify({
        'status': 'unknown',
        'progress': 0,
        'message': 'No active report generation task found'
    })

@app.route('/view_report/<product>/<date>')
def view_report(product, date):
    """View a generated report or show the generation progress."""
    # Get current language preference
    lang = session.get('language', 'en')
    
    generating = request.args.get('generating', 'false').lower() == 'true'
    
    # Get task_id from session if it exists
    task_id = session.get('current_task_id')
    
    # Check if there's a failed task for this product/date
    failed = False
    error_message = None
    
    if task_id and task_id in report_generation_tasks:
        task = report_generation_tasks[task_id]
        if task.get('product') == product and task.get('date') == date:
            if task.get('status') == 'failed':
                failed = True
                error_message = task.get('message', 'Report generation failed')
            elif task.get('status') in ['starting', 'in_progress']:
                generating = True
    
    report_filename = f"{product}_Beautiful_Report_{date}.html"
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "Reports", report_filename)
    
    # If the report exists, show it
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            return render_template('report.html', 
                                  product=product, 
                                  date=date, 
                                  report_content=report_content,
                                  t=template_translation,
                                  lang=lang)
        except Exception as e:
            error_message = f"Error reading report file: {str(e)}"
            return render_template('report.html',
                                  product=product,
                                  date=date,
                                  error_message=error_message,
                                  t=template_translation,
                                  lang=lang)
    
    # If generating or just failed, show the progress page
    elif generating:
        return render_template('report.html',
                              product=product,
                              date=date,
                              generating=True,
                              t=template_translation,
                              lang=lang)
    elif failed:
        return render_template('report.html',
                              product=product,
                              date=date,
                              error_message=error_message,
                              t=template_translation,
                              lang=lang)
    
    # If report doesn't exist and not generating, show error
    else:
        error_message = f"Report for {product} on {date} not found. Would you like to generate it?"
        return render_template('report.html',
                              product=product,
                              date=date,
                              error_message=error_message,
                              show_generate_button=True,
                              t=template_translation,
                              lang=lang)

@app.route('/products')
def products():
    """Return the list of available products as JSON."""
    return jsonify(PRODUCT_TYPES)

@app.route('/reports/<path:filename>')
def serve_report(filename):
    """Serve report HTML files from the Reports directory."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
    return send_from_directory(reports_dir, filename)

@app.route('/charts/<path:filename>')
def serve_chart(filename):
    """Serve chart images from the Charts directory."""
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Charts")
    return send_from_directory(charts_dir, filename)

@app.route('/continue_iteration', methods=['POST'])
def continue_iteration():
    """Handle request to continue iteration on a report with improved analysis."""
    product = request.form.get('product')
    date = request.form.get('date')
    
    if not product or not date:
        flash('Please provide both product and date', 'danger')
        return redirect(url_for('index'))
    
    # Get current language preference
    lang = session.get('language', 'en')
    
    # Check multiple possible locations for the report file
    report_filename = f"{product}_Beautiful_Report_{date}.html"
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports", report_filename),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Scripts", "Reports", report_filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reports", report_filename)
    ]
    
    report_path = None
    for path in possible_paths:
        if os.path.exists(path):
            report_path = path
            break
    
    if not report_path:
        error_message = f"Report for {product} on {date} not found. Would you like to generate it?"
        return render_template('report.html',
                              product=product,
                              date=date,
                              error_message=error_message,
                              show_generate_button=True,
                              t=template_translation,
                              lang=lang)
    
    try:
        # Read the existing report content to use for improvement
        with open(report_path, 'r', encoding='utf-8') as f:
            existing_report_content = f.read()
            
        # Store the existing report for reference in the task
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Reports")
        iteration_source = os.path.join(reports_dir, f"{product}_iteration_source_{date}.html")
        with open(iteration_source, 'w', encoding='utf-8') as f:
            f.write(existing_report_content)
            
        print(f"Stored existing report as reference for iteration at {iteration_source}")
    except Exception as e:
        print(f"Error reading existing report: {str(e)}")
        # Continue even if we can't read the existing report
    
    # Start asynchronous report generation with iteration flag
    task_id = f"{product}_{date}_iteration_{int(time.time())}"
    report_generation_tasks[task_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Starting report iteration with enhanced analysis...',
        'product': product,
        'date': date,
        'report_type': 'detailed',
        'is_iteration': True,  # Flag to indicate this is an iteration
        'language': lang,      # Store language setting
        'iteration_source': iteration_source if 'iteration_source' in locals() else None
    }
    
    # Store task_id in session for progress tracking
    session['current_task_id'] = task_id
    
    # Modify generate_report_task to use the iteration flag
    thread = threading.Thread(
        target=generate_report_task_with_iteration, 
        args=(product, date, 'detailed', task_id)
    )
    thread.daemon = True
    thread.start()
    
    # Redirect to the report page with a flag to show progress
    return redirect(url_for('view_report', product=product, date=date, generating=True, iteration=True))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('report.html', error_message="Page not found", t=get_translation, lang=session.get('language', 'en')), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('report.html', error_message=f"Server error: {str(e)}", t=get_translation, lang=session.get('language', 'en')), 500

if __name__ == '__main__':
    app.run(debug=True)