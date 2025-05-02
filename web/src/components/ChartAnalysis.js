import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Row, Col, Typography, Select, Button, Spin, Tabs, Radio, Empty, Alert, Divider } from 'antd';
import { AreaChartOutlined, LineChartOutlined, FileTextOutlined } from '@ant-design/icons';
import ApiService from '../services/ApiService';

// Get the same API URL used in ApiService
const API_URL = process.env.REACT_APP_API_URL || '';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const ChartAnalysis = () => {
  const { symbol } = useParams();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [parametersLoading, setParametersLoading] = useState(false);
  const [parameterSets, setParameterSets] = useState([]);
  const [selectedParameterSet, setSelectedParameterSet] = useState('default');
  const [period, setPeriod] = useState('1y');
  const [chartData, setChartData] = useState(null);
  const [error, setError] = useState(null);

  // Load available parameter sets
  useEffect(() => {
    const fetchParameters = async () => {
      try {
        setParametersLoading(true);
        const data = await ApiService.getParameters();
        setParameterSets(data);
      } catch (error) {
        console.error('Error fetching parameter sets:', error);
        setError(t('error'));
      } finally {
        setParametersLoading(false);
      }
    };

    fetchParameters();
  }, [t]);

  // Generate charts when component mounts with default parameters
  useEffect(() => {
    if (symbol) {
      generateCharts();
    }
  }, [symbol]); // eslint-disable-line react-hooks/exhaustive-deps

  const generateCharts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await ApiService.generateCharts(symbol, [selectedParameterSet], period);
      setChartData(data);
    } catch (error) {
      console.error(`Error generating charts for ${symbol}:`, error);
      // Set more detailed error message
      if (error.response && error.response.data && error.response.data.error) {
        setError(`${t('error')}: ${error.response.data.error}`);
      } else {
        setError(t('error'));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleParameterChange = (value) => {
    setSelectedParameterSet(value);
  };

  const handlePeriodChange = (value) => {
    setPeriod(value);
  };

  const renderIframe = (url) => {
    // Ensure the URL is properly formatted with API base URL if it's a relative URL
    const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
    
    return (
      <iframe
        src={fullUrl}
        style={{
          width: '100%',
          height: '500px',
          border: 'none',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
        title={`${symbol} Chart`}
      />
    );
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <p>{t('chart_analysis.loading_chart')}</p>
        </div>
      );
    }

    if (error) {
      return (
        <Alert
          message={error}
          description={t('error_description')}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={generateCharts}>
              {t('retry')}
            </Button>
          }
        />
      );
    }

    if (!chartData || !chartData.charts) {
      return <Empty description={t('no_data')} />;
    }

    return (
      <Tabs defaultActiveKey="indicators">
        <TabPane
          tab={
            <span>
              <LineChartOutlined />
              {t('chart_analysis.indicators')}
            </span>
          }
          key="indicators"
        >
          {chartData.charts.indicators && chartData.charts.indicators.length > 0 ? (
            renderIframe(chartData.charts.indicators[0])
          ) : (
            <Empty description={t('no_data')} />
          )}
        </TabPane>
        <TabPane
          tab={
            <span>
              <AreaChartOutlined />
              {t('chart_analysis.bollinger')}
            </span>
          }
          key="bollinger"
        >
          {chartData.charts.bollinger && chartData.charts.bollinger.length > 0 ? (
            renderIframe(chartData.charts.bollinger[0])
          ) : (
            <Empty description={t('no_data')} />
          )}
        </TabPane>
        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              {t('chart_analysis.report')}
            </span>
          }
          key="report"
        >
          <Alert
            message={t('chart_analysis.report_info')}
            description={
              <Button 
                type="primary" 
                onClick={() => window.open(`/reports/${symbol}?parameter_set=${selectedParameterSet}`, '_blank')}
              >
                {t('chart_analysis.view_report')}
              </Button>
            }
            type="info"
            showIcon
          />
        </TabPane>
      </Tabs>
    );
  };

  return (
    <div className="chart-analysis-container">
      <Title level={2}>
        {symbol} - {t('chart_analysis.title')}
      </Title>

      <Card className="mb-4">
        <Row gutter={16} align="middle">
          <Col xs={24} md={6}>
            <Select
              placeholder={t('chart_analysis.select_parameter')}
              onChange={handleParameterChange}
              value={selectedParameterSet}
              style={{ width: '100%' }}
              loading={parametersLoading}
            >
              {parameterSets.map(param => (
                <Option key={param} value={param}>
                  {t(`parameter_sets.${param}`)}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={6}>
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
          </Col>
          <Col xs={24} md={12}>
            <Button
              type="primary"
              onClick={generateCharts}
              loading={loading}
              style={{ marginRight: '10px' }}
            >
              {t('chart_analysis.generate_charts')}
            </Button>
            
            <Button
              onClick={() => window.open(`/reports/${symbol}?parameter_set=${selectedParameterSet}`, '_blank')}
            >
              {t('chart_analysis.view_report')}
            </Button>
          </Col>
        </Row>
      </Card>

      <Card className="chart-display">
        {renderContent()}
      </Card>
    </div>
  );
};

export default ChartAnalysis;