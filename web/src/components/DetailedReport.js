import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  Card, Row, Col, Typography, Select, Button, Spin, 
  Tabs, Empty, Alert, Divider, Form, Radio 
} from 'antd';
import { 
  PrinterOutlined, 
  DownloadOutlined, 
  ReloadOutlined 
} from '@ant-design/icons';
import ApiService from '../services/ApiService';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const DetailedReport = () => {
  const { symbol } = useParams();
  const [searchParams] = useSearchParams();
  const { t, i18n } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [assetCategories, setAssetCategories] = useState({});
  const [selectedSymbol, setSelectedSymbol] = useState(symbol || '');
  const [parameterSets, setParameterSets] = useState([]);
  const [selectedParameterSet, setSelectedParameterSet] = useState(
    searchParams.get('parameter_set') || 'default'
  );
  const [language, setLanguage] = useState(i18n.language || 'en');
  const [period, setPeriod] = useState('1y');
  const [reportUrl, setReportUrl] = useState(null);
  const [reportContent, setReportContent] = useState('');
  const [error, setError] = useState(null);
  
  // Use refs to track loading status and prevent duplicate requests
  const reportAlreadyLoaded = useRef(false);
  const initialDataLoaded = useRef(false);
  const generatingReport = useRef(false);
  const reportContainerRef = useRef(null);
  
  // Handle direct links to report HTML files - only runs once on mount
  useEffect(() => {
    if (symbol && symbol.endsWith('.html') && !reportAlreadyLoaded.current) {
      reportAlreadyLoaded.current = true;
      // Extract the actual symbol from the filename
      const baseSymbol = symbol.split('_')[0];
      setSelectedSymbol(baseSymbol);
      
      // Set report URL directly without triggering report generation
      const reportPath = `/reports/${symbol}`;
      setReportUrl(reportPath);
      fetchAndDisplayReport(reportPath);
    }
  }, []); 

  // Load assets and parameters on component mount
  useEffect(() => {
    // Prevent duplicate calls
    if (initialDataLoaded.current) {
      return;
    }
    
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        initialDataLoaded.current = true;
        
        // Fetch asset categories
        const categories = await ApiService.getAssets();
        setAssetCategories(categories);
        
        // Fetch parameter sets
        const parameters = await ApiService.getParameters();
        setParameterSets(parameters);
        
        // If symbol is provided in URL and we haven't loaded a report yet, attempt to show it
        if (symbol && !reportAlreadyLoaded.current) {
          // Extract the actual symbol if it's an HTML file name
          let actualSymbol = symbol;
          if (symbol.includes('_interactive_report_')) {
            actualSymbol = symbol.split('_')[0];
            setSelectedSymbol(actualSymbol);
          }
          
          // If this is a direct link to a report file, just display it without regenerating
          if (symbol.endsWith('.html')) {
            reportAlreadyLoaded.current = true;
            const reportPath = `/reports/${symbol}`;
            setReportUrl(reportPath);
            await fetchAndDisplayReport(reportPath);
          } else if (!generatingReport.current) {
            // Only generate a new report if we're not already generating one
            await generateReport();
          }
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
        setError(t('error'));
      } finally {
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, [symbol, t]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Function to fetch and display the report content
  const fetchAndDisplayReport = async (url) => {
    try {
      setLoading(true);
      // Fetch the HTML content
      const response = await axios.get(url);
      
      if (response.status === 200) {
        // Get the full HTML content
        let htmlContent = response.data;
        
        // Extract the <head> content for styles and scripts
        const headMatch = htmlContent.match(/<head[^>]*>([\s\S]*)<\/head>/i);
        const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i);
        
        if (bodyMatch && bodyMatch[1]) {
          // Get just the body content
          const bodyContent = bodyMatch[1];
          
          // Create a div to hold styles and scripts
          let stylesAndScripts = '';
          
          // Extract and prepare styles from <head>
          if (headMatch && headMatch[1]) {
            const headContent = headMatch[1];
            
            // Extract style tags
            const styleTagsRegex = /<style[^>]*>[\s\S]*?<\/style>/gi;
            const styleTags = headContent.match(styleTagsRegex) || [];
            stylesAndScripts += styleTags.join('');
            
            // Extract link tags for CSS
            const linkTagsRegex = /<link[^>]*rel=["']stylesheet["'][^>]*>/gi;
            const linkTags = headContent.match(linkTagsRegex) || [];
            
            // Extract cdn script tags (especially plotly)
            const scriptTagsRegex = /<script[^>]*src=["'][^"']*cdn[^"']*["'][^>]*>[\s\S]*?<\/script>/gi;
            const scriptTags = headContent.match(scriptTagsRegex) || [];
            stylesAndScripts += scriptTags.join('');
          }
          
          // Set the HTML content with necessary styles and external scripts
          setReportContent(`
            ${stylesAndScripts}
            <div class="report-content">
              ${bodyContent}
            </div>
          `);
          
          // Add event listener for script execution
          setTimeout(() => {
            if (reportContainerRef.current) {
              // Manually add Plotly if needed
              if (!window.Plotly) {
                const plotlyScript = document.createElement('script');
                plotlyScript.src = 'https://cdn.plot.ly/plotly-latest.min.js';
                plotlyScript.async = true;
                document.head.appendChild(plotlyScript);
                
                plotlyScript.onload = () => {
                  // Process any inline scripts that might depend on Plotly
                  processScripts();
                };
              } else {
                processScripts();
              }
            }
          }, 100);
        } else {
          throw new Error('Could not extract report body content');
        }
      } else {
        throw new Error(`Failed to fetch report: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching report:', error);
      setError(t('error_fetching_report'));
    } finally {
      setLoading(false);
    }
  };
  
  // Helper function to process scripts in the report
  const processScripts = () => {
    if (!reportContainerRef.current) return;
    
    // Process any script tags in the report
    const scripts = reportContainerRef.current.querySelectorAll('script');
    scripts.forEach(script => {
      try {
        const newScript = document.createElement('script');
        
        // Copy all attributes from old script to new script
        Array.from(script.attributes).forEach(attr => {
          newScript.setAttribute(attr.name, attr.value);
        });
        
        // If it has src, set it, otherwise use the inner content
        if (script.src) {
          newScript.src = script.src;
        } else {
          newScript.textContent = script.textContent;
        }
        
        // Replace old with new
        script.parentNode.replaceChild(newScript, script);
      } catch (err) {
        console.error('Error processing script:', err);
      }
    });
  };
  
  const generateReport = async () => {
    if (!selectedSymbol || generatingReport.current) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      generatingReport.current = true;
      
      // Make sure we're always using the base symbol (not a filename)
      let baseSymbol = selectedSymbol;
      if (selectedSymbol.includes('_')) {
        // Extract the actual symbol if it's a filename pattern
        baseSymbol = selectedSymbol.split('_')[0];
        setSelectedSymbol(baseSymbol);
      }
      
      // First, generate charts (which calculates indicators)
      await ApiService.generateCharts(
        baseSymbol, 
        [selectedParameterSet], 
        period
      );
      
      // Now call the API endpoint to generate the report
      const reportResponse = await ApiService.get(
        `/api/generate_report/${baseSymbol}?parameter_set=${selectedParameterSet}&period=${period}&language=${language}`
      );
      
      if (reportResponse && reportResponse.report_url) {
        reportAlreadyLoaded.current = true;
        setReportUrl(reportResponse.report_url);
        // Fetch and display the report content
        await fetchAndDisplayReport(reportResponse.report_url);
      } else {
        throw new Error('Failed to get report URL from server');
      }
    } catch (error) {
      console.error(`Error generating report for ${selectedSymbol}:`, error);
      setError(t('error'));
    } finally {
      setLoading(false);
      generatingReport.current = false;
    }
  };
  
  const handleSymbolChange = (value) => {
    if (value !== selectedSymbol) {
      // Reset the report URL when changing symbols
      setReportUrl(null);
      setReportContent('');
      reportAlreadyLoaded.current = false;
      setSelectedSymbol(value);
    }
  };
  
  const handleParameterChange = (value) => {
    if (value !== selectedParameterSet) {
      // Reset the report URL when changing parameters
      setReportUrl(null);
      setReportContent('');
      reportAlreadyLoaded.current = false;
      setSelectedParameterSet(value);
    }
  };
  
  const handlePeriodChange = (value) => {
    if (value !== period) {
      // Reset the report URL when changing period
      setReportUrl(null);
      setReportContent('');
      reportAlreadyLoaded.current = false;
      setPeriod(value);
    }
  };
  
  const handleLanguageChange = (e) => {
    if (e.target.value !== language) {
      // Reset the report URL when changing language
      setReportUrl(null);
      setReportContent('');
      reportAlreadyLoaded.current = false;
      setLanguage(e.target.value);
    }
  };
  
  const handleRefresh = () => {
    if (reportUrl) {
      fetchAndDisplayReport(reportUrl);
    }
  };
  
  const renderSymbolOptions = () => {
    const options = [];
    
    if (assetCategories) {
      Object.entries(assetCategories).forEach(([category, assets]) => {
        const categoryOptions = assets.map(asset => (
          <Option key={asset} value={asset}>
            {asset} ({t(`categories.${category}`)})
          </Option>
        ));
        options.push(...categoryOptions);
      });
    }
    
    return options;
  };
  
  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <p>{t('loading')}</p>
        </div>
      );
    }
    
    if (error) {
      return (
        <Alert
          message={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={generateReport}>
              {t('retry')}
            </Button>
          }
        />
      );
    }
    
    if (!reportUrl || !reportContent) {
      return (
        <Empty 
          description={t('detailed_report.report_not_found')}
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      );
    }
    
    return (
      <div className="report-display">
        <div className="report-actions" style={{ marginBottom: '15px' }}>
          <Button 
            type="primary" 
            icon={<PrinterOutlined />} 
            onClick={() => window.print()}
            style={{ marginRight: '10px' }}
          >
            {t('detailed_report.print_report')}
          </Button>
          
          <Button 
            icon={<DownloadOutlined />} 
            onClick={() => window.open(reportUrl, '_blank')}
            style={{ marginRight: '10px' }}
          >
            {t('detailed_report.download_report')}
          </Button>

          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
          >
            {t('refresh')}
          </Button>
        </div>
        
        <div 
          ref={reportContainerRef}
          className="report-container"
          style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
          dangerouslySetInnerHTML={{ __html: reportContent }}
        />
      </div>
    );
  };
  
  return (
    <div className="detailed-report-container">
      <Title level={2}>{t('detailed_report.title')}</Title>
      
      <Card className="mb-4">
        <Form layout="vertical">
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item label={t('chart_analysis.select_symbol')}>
                <Select
                  placeholder={t('chart_analysis.select_symbol')}
                  onChange={handleSymbolChange}
                  value={selectedSymbol}
                  style={{ width: '100%' }}
                  showSearch
                  filterOption={(input, option) =>
                    option.children.toString().toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {renderSymbolOptions()}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={5}>
              <Form.Item label={t('chart_analysis.select_parameter')}>
                <Select
                  placeholder={t('chart_analysis.select_parameter')}
                  onChange={handleParameterChange}
                  value={selectedParameterSet}
                  style={{ width: '100%' }}
                >
                  {parameterSets.map(param => (
                    <Option key={param} value={param}>
                      {t(`parameter_sets.${param}`)}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={5}>
              <Form.Item label={t('chart_analysis.select_period')}>
                <Select
                  placeholder={t('chart_analysis.select_period')}
                  onChange={handlePeriodChange}
                  value={period}
                  style={{ width: '100%' }}
                >
                  <Option value="1mo">{t('chart_analysis.periods.1mo')}</Option>
                  <Option value="3mo">{t('chart_analysis.periods.3mo')}</Option>
                  <Option value="6mo">{t('chart_analysis.periods.6mo')}</Option>
                  <Option value="1y">{t('chart_analysis.periods.1y')}</Option>
                  <Option value="2y">{t('chart_analysis.periods.2y')}</Option>
                  <Option value="5y">{t('chart_analysis.periods.5y')}</Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={6}>
              <Form.Item label={t('language')}>
                <Radio.Group onChange={handleLanguageChange} value={language}>
                  <Radio.Button value="en">English</Radio.Button>
                  <Radio.Button value="zh">中文</Radio.Button>
                </Radio.Group>
              </Form.Item>
            </Col>
            
            <Col xs={24}>
              <Button
                type="primary"
                onClick={generateReport}
                loading={loading}
                disabled={!selectedSymbol}
              >
                {t('detailed_report.generate_new_report')}
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>
      
      <Card className="report-container">
        {renderContent()}
      </Card>
      
      {reportUrl && !error && !loading && (
        <Card className="explanation-card mt-4">
          <Title level={4}>{t('detailed_report.strategy_explanation')}</Title>
          <Paragraph>
            {selectedParameterSet === 'trend_following' && (
              <div>
                <b>{t('parameter_sets.trend_following')}: </b>
                SMA(50,200) + EMA(12,26) + ADX(14). 
                {t('strategy_explanations.trend_following')}
              </div>
            )}
            
            {selectedParameterSet === 'momentum' && (
              <div>
                <b>{t('parameter_sets.momentum')}: </b>
                RSI(14) + MACD(12,26,9) + Stochastic(14,3). 
                {t('strategy_explanations.momentum')}
              </div>
            )}
            
            {selectedParameterSet === 'volatility' && (
              <div>
                <b>{t('parameter_sets.volatility')}: </b>
                Bollinger Bands(20,2) + ATR(14) + Keltner Channels. 
                {t('strategy_explanations.volatility')}
              </div>
            )}
            
            {selectedParameterSet === 'ichimoku' && (
              <div>
                <b>{t('parameter_sets.ichimoku')}: </b>
                Ichimoku Cloud(9,26,52) + Parabolic SAR(0.02,0.2) + On-Balance Volume. 
                {t('strategy_explanations.ichimoku')}
              </div>
            )}
          </Paragraph>
        </Card>
      )}
    </div>
  );
};

export default DetailedReport;
