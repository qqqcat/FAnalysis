import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  Card, Row, Col, Typography, Select, Button, Spin, 
  Tabs, Empty, Alert, Divider, Form, DatePicker, Radio 
} from 'antd';
import { 
  PrinterOutlined, 
  DownloadOutlined, 
  FileTextOutlined, 
  AreaChartOutlined 
} from '@ant-design/icons';
import ApiService from '../services/ApiService';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

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
  const [error, setError] = useState(null);
  
  // Load assets and parameters on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Fetch asset categories
        const categories = await ApiService.getAssets();
        setAssetCategories(categories);
        
        // Fetch parameter sets
        const parameters = await ApiService.getParameters();
        setParameterSets(parameters);
        
        // If symbol is provided in URL, generate report
        if (symbol) {
          generateReport();
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
  
  const generateReport = async () => {
    if (!selectedSymbol) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Generate charts first (which also calculates indicators)
      const chartsData = await ApiService.generateCharts(
        selectedSymbol, 
        [selectedParameterSet], 
        period
      );
      
      // Assume charts generation was successful, create a URL for the report
      // In a real implementation, we would make an API call to generate a report
      // and get a direct URL to that report
      const reportUrlPath = `/reports/${selectedSymbol}_interactive_report_${new Date().toISOString().split('T')[0].replace(/-/g, '')}_${selectedParameterSet}.html`;
      setReportUrl(reportUrlPath);
    } catch (error) {
      console.error(`Error generating report for ${selectedSymbol}:`, error);
      setError(t('error'));
    } finally {
      setLoading(false);
    }
  };
  
  const handleSymbolChange = (value) => {
    setSelectedSymbol(value);
  };
  
  const handleParameterChange = (value) => {
    setSelectedParameterSet(value);
  };
  
  const handlePeriodChange = (value) => {
    setPeriod(value);
  };
  
  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
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
    
    if (!reportUrl) {
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
          >
            {t('detailed_report.download_report')}
          </Button>
        </div>
        
        <iframe
          src={reportUrl}
          style={{
            width: '100%',
            height: '800px',
            border: 'none',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
          title={`${selectedSymbol} Report`}
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