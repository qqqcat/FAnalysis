import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  Card, Row, Col, Typography, Select, Button, Spin, 
  Empty, Alert, Form, Radio 
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

// Debounced function to auto-generate reports when parameters change
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
};

// Custom hook for managing report generation and display
const useReportManager = (initialSymbol, initialParams) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reportUrl, setReportUrl] = useState(null);
  const [reportContent, setReportContent] = useState('');
  const [reportState, setReportState] = useState('idle'); // 'idle', 'loading', 'success', 'error'
  
  const reportRef = useRef(null);
  
  // Function to generate a report
  const generateReport = useCallback(async (symbol, parameterSet, period, language) => {
    if (!symbol || loading) return null;
    
    try {
      setLoading(true);
      setError(null);
      setReportState('loading');
      
      // Extract base symbol if needed
      const baseSymbol = symbol.includes('_') ? symbol.split('_')[0] : symbol;
      
      // Single API call to generate the report (no need to call generateCharts first)
      const reportResponse = await ApiService.get(
        `/api/generate_report/${baseSymbol}?parameter_set=${parameterSet}&period=${period}&language=${language}`
      );
      
      if (reportResponse && reportResponse.report_url) {
        setReportUrl(reportResponse.report_url);
        setReportState('success');
        return reportResponse.report_url;
      } else {
        throw new Error('Failed to get report URL from server');
      }
    } catch (error) {
      console.error(`Error generating report for ${symbol}:`, error);
      setError(t('error_generating_report', 'Error generating report'));
      setReportState('error');
      return null;
    } finally {
      setLoading(false);
    }
  }, [t]);
  
  // Function to fetch and display a report by URL
  const fetchAndDisplayReport = useCallback(async (url) => {
    if (!url) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Fetch the HTML content
      const response = await axios.get(url);
      
      if (response.status === 200) {
        const htmlContent = response.data;
        
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
          
          setReportState('success');
        } else {
          throw new Error('Could not extract report body content');
        }
      } else {
        throw new Error(`Failed to fetch report: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching report:', error);
      setError(t('error_fetching_report', 'Error fetching report'));
      setReportState('error');
    } finally {
      setLoading(false);
    }
  }, [t]);
  
  // Process scripts in the report after rendering
  const processScripts = useCallback(() => {
    if (!reportRef.current) return;
    
    // Process any script tags in the report
    const scripts = reportRef.current.querySelectorAll('script');
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
  }, []);
  
  // Return everything needed to manage reports
  return {
    loading,
    error,
    reportUrl,
    reportContent,
    reportState,
    reportRef,
    generateReport,
    fetchAndDisplayReport,
    processScripts,
    setReportUrl,
    setReportContent
  };
};

// Strategy explanations component - separates hardcoded explanations from the main component
const StrategyExplanation = ({ parameterSet }) => {
  const { t } = useTranslation();
  
  // Get strategy details from translations or backend
  const getStrategyInfo = (parameterSet) => {
    const strategyMap = {
      'trend_following': {
        indicators: 'SMA(50,200) + EMA(12,26) + ADX(14)',
        translationKey: 'strategy_explanations.trend_following'
      },
      'momentum': {
        indicators: 'RSI(14) + MACD(12,26,9) + Stochastic(14,3)',
        translationKey: 'strategy_explanations.momentum'
      },
      'volatility': {
        indicators: 'Bollinger Bands(20,2) + ATR(14) + Keltner Channels',
        translationKey: 'strategy_explanations.volatility'
      },
      'ichimoku': {
        indicators: 'Ichimoku Cloud(9,26,52) + Parabolic SAR(0.02,0.2) + On-Balance Volume',
        translationKey: 'strategy_explanations.ichimoku'
      },
      'default': {
        indicators: 'SMA(50) + EMA(20) + RSI(14) + MACD(12,26,9)',
        translationKey: 'strategy_explanations.default'
      }
    };
    
    return strategyMap[parameterSet] || {
      indicators: t('strategy_explanations.custom_indicators'),
      translationKey: 'strategy_explanations.custom'
    };
  };
  
  const strategyInfo = getStrategyInfo(parameterSet);
  
  if (!parameterSet) return null;
  
  return (
    <div>
      <b>{t(`parameter_sets.${parameterSet}`)}: </b>
      {strategyInfo.indicators}. {t(strategyInfo.translationKey, 'No explanation available for this strategy.')}
    </div>
  );
};

const DetailedReport = () => {
  const { symbol } = useParams();
  const [searchParams] = useSearchParams();
  const { t, i18n } = useTranslation();
  const [selectedSymbol, setSelectedSymbol] = useState(symbol || '');
  const [parameterSets, setParameterSets] = useState([]);
  const [selectedParameterSet, setSelectedParameterSet] = useState(
    searchParams.get('parameter_set') || 'default'
  );
  const [language, setLanguage] = useState(i18n.language || 'en');
  const [period, setPeriod] = useState('1y');
  const [assetCategories, setAssetCategories] = useState({});
  
  const debouncedSymbol = useDebounce(selectedSymbol, 500);
  const debouncedParameterSet = useDebounce(selectedParameterSet, 500);
  const debouncedPeriod = useDebounce(period, 500);
  const debouncedLanguage = useDebounce(language, 500);
  
  const {
    loading,
    error,
    reportUrl,
    reportContent,
    reportRef,
    generateReport,
    fetchAndDisplayReport,
    processScripts
  } = useReportManager(selectedSymbol, { parameterSet: selectedParameterSet, period, language });
  
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch asset categories
        const categories = await ApiService.getAssets();
        setAssetCategories(categories);
        
        // Fetch parameter sets
        const parameters = await ApiService.getParameters();
        setParameterSets(parameters);
        
        // If symbol is provided in URL and it's a direct link to a report file, display it
        if (symbol && symbol.endsWith('.html')) {
          const reportPath = `/reports/${symbol}`;
          await fetchAndDisplayReport(reportPath);
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };
    
    fetchInitialData();
  }, [symbol, fetchAndDisplayReport]);
  
  useEffect(() => {
    if (debouncedSymbol && debouncedParameterSet && debouncedPeriod && debouncedLanguage) {
      generateReport(debouncedSymbol, debouncedParameterSet, debouncedPeriod, debouncedLanguage);
    }
  }, [debouncedSymbol, debouncedParameterSet, debouncedPeriod, debouncedLanguage, generateReport]);
  
  const handleSymbolChange = (value) => {
    if (value !== selectedSymbol) {
      setSelectedSymbol(value);
    }
  };
  
  const handleParameterChange = (value) => {
    if (value !== selectedParameterSet) {
      setSelectedParameterSet(value);
    }
  };
  
  const handlePeriodChange = (value) => {
    if (value !== period) {
      setPeriod(value);
    }
  };
  
  const handleLanguageChange = (e) => {
    if (e.target.value !== language) {
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
            <Button size="small" onClick={() => generateReport(selectedSymbol, selectedParameterSet, period, language)}>
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
          ref={reportRef}
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
                onClick={() => generateReport(selectedSymbol, selectedParameterSet, period, language)}
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
            <StrategyExplanation parameterSet={selectedParameterSet} />
          </Paragraph>
        </Card>
      )}
    </div>
  );
};

export default DetailedReport;
